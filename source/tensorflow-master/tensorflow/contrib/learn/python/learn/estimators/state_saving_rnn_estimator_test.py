# Copyright 2016 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Tests for learn.estimators.state_saving_rnn_estimator."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import tempfile

# TODO: #6568 Remove this hack that makes dlopen() not crash.
if hasattr(sys, 'getdlopenflags') and hasattr(sys, 'setdlopenflags'):
  import ctypes
  sys.setdlopenflags(sys.getdlopenflags() | ctypes.RTLD_GLOBAL)

import numpy as np

from tensorflow.contrib.layers.python.layers import feature_column
from tensorflow.contrib.layers.python.layers import target_column as target_column_lib
from tensorflow.contrib.learn.python.learn.estimators import model_fn as model_fn_lib
from tensorflow.contrib.learn.python.learn.estimators import run_config
from tensorflow.contrib.learn.python.learn.estimators import state_saving_rnn_estimator as ssre
from tensorflow.python.framework import constant_op
from tensorflow.python.framework import dtypes
from tensorflow.python.ops import array_ops
from tensorflow.python.ops import data_flow_ops
from tensorflow.python.ops import math_ops
from tensorflow.python.ops import random_ops
from tensorflow.python.ops import string_ops
from tensorflow.python.ops import variables
from tensorflow.python.platform import test


class PrepareInputsForRnnTest(test.TestCase):

  def _test_prepare_inputs_for_rnn(self, sequence_features, context_features,
                                   num_unroll, batch_size, expected):
    features_by_time = ssre._prepare_inputs_for_rnn(sequence_features,
                                                    context_features,
                                                    num_unroll)

    with self.test_session() as sess:
      sess.run(variables.global_variables_initializer())
      sess.run(data_flow_ops.initialize_all_tables())
      features_val = sess.run(features_by_time)
      self.assertAllEqual(expected, features_val)

  def testPrepareInputsForRnnBatchSize1(self):
    num_unroll = 3
    batch_size = 1

    expected = [
        np.array([[11., 31., 5., 7.]]), np.array([[12., 32., 5., 7.]]),
        np.array([[13., 33., 5., 7.]])
    ]

    sequence_features = {
        'seq_feature0': constant_op.constant([[11., 12., 13.]]),
        'seq_feature1': constant_op.constant([[31., 32., 33.]])
    }
    context_features = {
        'ctx_feature0': constant_op.constant([[5.]]),
        'ctx_feature1': constant_op.constant([[7.]])
    }
    self._test_prepare_inputs_for_rnn(sequence_features, context_features,
                                      num_unroll, batch_size, expected)

  def testPrepareInputsForRnnBatchSize2(self):

    num_unroll = 3
    batch_size = 2

    expected = [
        np.array([[11., 31., 5., 7.], [21., 41., 6., 8.]]),
        np.array([[12., 32., 5., 7.], [22., 42., 6., 8.]]),
        np.array([[13., 33., 5., 7.], [23., 43., 6., 8.]])
    ]

    sequence_features = {
        'seq_feature0':
            constant_op.constant([[11., 12., 13.], [21., 22., 23.]]),
        'seq_feature1':
            constant_op.constant([[31., 32., 33.], [41., 42., 43.]])
    }

    context_features = {
        'ctx_feature0': constant_op.constant([[5.], [6.]]),
        'ctx_feature1': constant_op.constant([[7.], [8.]])
    }

    self._test_prepare_inputs_for_rnn(sequence_features, context_features,
                                      num_unroll, batch_size, expected)

  def testPrepareInputsForRnnNoContext(self):
    num_unroll = 3
    batch_size = 2

    expected = [
        np.array([[11., 31.], [21., 41.]]), np.array([[12., 32.], [22., 42.]]),
        np.array([[13., 33.], [23., 43.]])
    ]

    sequence_features = {
        'seq_feature0':
            constant_op.constant([[11., 12., 13.], [21., 22., 23.]]),
        'seq_feature1':
            constant_op.constant([[31., 32., 33.], [41., 42., 43.]])
    }

    context_features = None

    self._test_prepare_inputs_for_rnn(sequence_features, context_features,
                                      num_unroll, batch_size, expected)


class StateSavingRnnEstimatorTest(test.TestCase):

  def testPrepareFeaturesForSQSS(self):
    mode = model_fn_lib.ModeKeys.TRAIN
    seq_feature_name = 'seq_feature'
    ctx_feature_name = 'ctx_feature'
    input_key_column_name = 'input_key_column'
    sequence_length = 4

    seq_feature = constant_op.constant(1.0, shape=[sequence_length])
    ctx_feature = constant_op.constant(2.0)
    input_key0 = constant_op.constant('input0')

    features = {
        input_key_column_name: input_key0,
        seq_feature_name: seq_feature,
        ctx_feature_name: ctx_feature
    }

    labels = constant_op.constant(5.0, shape=[sequence_length])

    sequence_feature_columns = [
        feature_column.real_valued_column(
            seq_feature_name, dimension=1)
    ]

    context_feature_columns = [
        feature_column.real_valued_column(
            ctx_feature_name, dimension=1)
    ]

    expected_input_key = b'input0'

    expected_sequence = {
        ssre.RNNKeys.LABELS_KEY: np.array([5., 5., 5., 5.]),
        seq_feature_name: np.array([1., 1., 1., 1.]),
    }

    expected_context = {ctx_feature_name: 2.}

    input_key, sequence, context = ssre._prepare_features_for_sqss(
        features, labels, mode, input_key_column_name, sequence_feature_columns,
        context_feature_columns)

    def assert_equal(a, b):
      self.assertEqual(sorted(a), sorted(b))
      for k, v in a.items():
        self.assertAllEqual(v, b[k])

    with self.test_session() as sess:
      sess.run(variables.global_variables_initializer())
      sess.run(data_flow_ops.initialize_all_tables())
      actual_input_key, actual_sequence, actual_context = sess.run(
          [input_key, sequence, context])
      self.assertEqual(expected_input_key, actual_input_key)
      assert_equal(expected_sequence, actual_sequence)
      assert_equal(expected_context, actual_context)

  def testMaskActivationsAndLabels(self):
    """Test `mask_activations_and_labels`."""
    batch_size = 4
    padded_length = 6
    num_classes = 4
    np.random.seed(1234)
    sequence_length = np.random.randint(0, padded_length + 1, batch_size)
    activations = np.random.rand(batch_size, padded_length, num_classes)
    labels = np.random.randint(0, num_classes, [batch_size, padded_length])
    (activations_masked_t, labels_masked_t) = ssre.mask_activations_and_labels(
        constant_op.constant(
            activations, dtype=dtypes.float32),
        constant_op.constant(
            labels, dtype=dtypes.int32),
        constant_op.constant(
            sequence_length, dtype=dtypes.int32))

    with self.test_session() as sess:
      activations_masked, labels_masked = sess.run(
          [activations_masked_t, labels_masked_t])

    expected_activations_shape = [sum(sequence_length), num_classes]
    np.testing.assert_equal(
        expected_activations_shape, activations_masked.shape,
        'Wrong activations shape. Expected {}; got {}.'.format(
            expected_activations_shape, activations_masked.shape))

    expected_labels_shape = [sum(sequence_length)]
    np.testing.assert_equal(expected_labels_shape, labels_masked.shape,
                            'Wrong labels shape. Expected {}; got {}.'.format(
                                expected_labels_shape, labels_masked.shape))
    masked_index = 0
    for i in range(batch_size):
      for j in range(sequence_length[i]):
        actual_activations = activations_masked[masked_index]
        expected_activations = activations[i, j, :]
        np.testing.assert_almost_equal(
            expected_activations,
            actual_activations,
            err_msg='Unexpected logit value at index [{}, {}, :].'
            '  Expected {}; got {}.'.format(i, j, expected_activations,
                                            actual_activations))

        actual_labels = labels_masked[masked_index]
        expected_labels = labels[i, j]
        np.testing.assert_almost_equal(
            expected_labels,
            actual_labels,
            err_msg='Unexpected logit value at index [{}, {}].'
            ' Expected {}; got {}.'.format(i, j, expected_labels,
                                           actual_labels))
        masked_index += 1

  def _getModelFnOpsForMode(self, mode):
    """Helper for testGetRnnModelFn{Train,Eval,Infer}()."""
    cell_size = 4
    num_layers = 1
    cell = ssre.lstm_cell(cell_size, num_layers)
    seq_columns = [
        feature_column.real_valued_column(
            'inputs', dimension=cell_size)
    ]
    features = {
        'inputs': constant_op.constant([1., 2., 3.]),
        'input_key_column': constant_op.constant('input0')
    }
    labels = constant_op.constant([1., 0., 1.])
    model_fn = ssre._get_rnn_model_fn(
        cell=cell,
        target_column=target_column_lib.multi_class_target(n_classes=2),
        optimizer='SGD',
        num_unroll=2,
        num_layers=num_layers,
        num_threads=1,
        queue_capacity=10,
        batch_size=1,
        input_key_column_name='input_key_column',
        # Only CLASSIFICATION yields eval metrics to test for.
        problem_type=ssre.ProblemType.CLASSIFICATION,
        sequence_feature_columns=seq_columns,
        context_feature_columns=None,
        learning_rate=0.1)
    model_fn_ops = model_fn(features=features, labels=labels, mode=mode)
    return model_fn_ops

  # testGetRnnModelFn{Train,Eval,Infer}() test which fields
  # of ModelFnOps are set depending on mode.
  def testGetRnnModelFnTrain(self):
    model_fn_ops = self._getModelFnOpsForMode(model_fn_lib.ModeKeys.TRAIN)
    self.assertIsNotNone(model_fn_ops.predictions)
    self.assertIsNotNone(model_fn_ops.loss)
    self.assertIsNotNone(model_fn_ops.train_op)
    # None may get normalized to {}; we accept neither.
    self.assertNotEqual(len(model_fn_ops.eval_metric_ops), 0)

  def testGetRnnModelFnEval(self):
    model_fn_ops = self._getModelFnOpsForMode(model_fn_lib.ModeKeys.EVAL)
    self.assertIsNotNone(model_fn_ops.predictions)
    self.assertIsNotNone(model_fn_ops.loss)
    self.assertIsNone(model_fn_ops.train_op)
    # None may get normalized to {}; we accept neither.
    self.assertNotEqual(len(model_fn_ops.eval_metric_ops), 0)

  def testGetRnnModelFnInfer(self):
    model_fn_ops = self._getModelFnOpsForMode(model_fn_lib.ModeKeys.INFER)
    self.assertIsNotNone(model_fn_ops.predictions)
    self.assertIsNone(model_fn_ops.loss)
    self.assertIsNone(model_fn_ops.train_op)
    # None may get normalized to {}; we accept both.
    self.assertFalse(model_fn_ops.eval_metric_ops)

  def testExport(self):
    input_key_column_name = 'input0'
    input_feature_key = 'magic_input_feature_key'
    batch_size = 8
    cell_size = 4
    sequence_length = 10
    num_unroll = 2
    num_classes = 2

    seq_columns = [
        feature_column.real_valued_column(
            'inputs', dimension=cell_size)
    ]

    def get_input_fn(mode, seed):

      def input_fn():
        input_key = string_ops.string_join([
            'key_', string_ops.as_string(
                random_ops.random_uniform(
                    (),
                    minval=0,
                    maxval=10000000,
                    dtype=dtypes.int32,
                    seed=seed))
        ])
        features = {}
        random_sequence = random_ops.random_uniform(
            [sequence_length + 1], 0, 2, dtype=dtypes.int32, seed=seed)
        labels = array_ops.slice(random_sequence, [0], [sequence_length])
        inputs = math_ops.to_float(
            array_ops.slice(random_sequence, [1], [sequence_length]))
        features = {'inputs': inputs, input_key_column_name: input_key}

        if mode == model_fn_lib.ModeKeys.INFER:
          input_examples = array_ops.placeholder(dtypes.string)
          features[input_feature_key] = input_examples
          labels = None
        return features, labels

      return input_fn

    model_dir = tempfile.mkdtemp()

    def estimator_fn():
      return ssre.multi_value_rnn_classifier(
          num_classes=num_classes,
          num_units=cell_size,
          num_unroll=num_unroll,
          batch_size=batch_size,
          input_key_column_name=input_key_column_name,
          sequence_feature_columns=seq_columns,
          predict_probabilities=True,
          model_dir=model_dir,
          queue_capacity=2 + batch_size)

    # Train a bit to create an exportable checkpoint.
    estimator_fn().fit(input_fn=get_input_fn(
        model_fn_lib.ModeKeys.TRAIN, seed=1234),
                       steps=100)
    # Now export, but from a fresh estimator instance, like you would
    # in an export binary. That means .export() has to work without
    # .fit() being called on the same object.
    export_dir = tempfile.mkdtemp()
    print('Exporting to', export_dir)
    estimator_fn().export(
        export_dir,
        input_fn=get_input_fn(
            model_fn_lib.ModeKeys.INFER, seed=4321),
        use_deprecated_input_fn=False,
        input_feature_key=input_feature_key)


# TODO(jtbates): move all tests below to a benchmark test.
class StateSavingRNNEstimatorLearningTest(test.TestCase):
  """Learning tests for state saving RNN Estimators."""

  def testLearnSineFunction(self):
    """Tests learning a sine function."""
    batch_size = 8
    num_unroll = 5
    sequence_length = 64
    train_steps = 250
    eval_steps = 20
    cell_size = 4
    learning_rate = 0.3
    loss_threshold = 0.03
    input_key_column_name = 'input_key_column'

    def get_sin_input_fn(sequence_length, increment, seed=None):

      def input_fn():
        start = random_ops.random_uniform(
            (), minval=0, maxval=(np.pi * 2.0), dtype=dtypes.float32, seed=seed)
        sin_curves = math_ops.sin(
            math_ops.linspace(start, (sequence_length - 1) * increment,
                              sequence_length + 1))
        inputs = array_ops.slice(sin_curves, [0], [sequence_length])
        labels = array_ops.slice(sin_curves, [1], [sequence_length])
        input_key = string_ops.string_join([
            'key_',
            string_ops.as_string(math_ops.cast(10000 * start, dtypes.int32))
        ])
        return {'inputs': inputs, input_key_column_name: input_key}, labels

      return input_fn

    seq_columns = [
        feature_column.real_valued_column(
            'inputs', dimension=cell_size)
    ]
    config = run_config.RunConfig(tf_random_seed=1234)
    sequence_estimator = ssre.multi_value_rnn_regressor(
        num_units=cell_size,
        num_unroll=num_unroll,
        batch_size=batch_size,
        input_key_column_name=input_key_column_name,
        sequence_feature_columns=seq_columns,
        learning_rate=learning_rate,
        input_keep_probability=0.9,
        output_keep_probability=0.9,
        config=config,
        queue_capacity=2 * batch_size)

    train_input_fn = get_sin_input_fn(sequence_length, np.pi / 32, seed=1234)
    eval_input_fn = get_sin_input_fn(sequence_length, np.pi / 32, seed=4321)

    sequence_estimator.fit(input_fn=train_input_fn, steps=train_steps)
    loss = sequence_estimator.evaluate(
        input_fn=eval_input_fn, steps=eval_steps)['loss']
    self.assertLess(loss, loss_threshold,
                    'Loss should be less than {}; got {}'.format(loss_threshold,
                                                                 loss))

  def testLearnShiftByOne(self):
    """Tests that learning a 'shift-by-one' example.

    Each label sequence consists of the input sequence 'shifted' by one place.
    The RNN must learn to 'remember' the previous input.
    """
    batch_size = 16
    num_classes = 2
    num_unroll = 32
    sequence_length = 32
    train_steps = 200
    eval_steps = 20
    cell_size = 4
    learning_rate = 0.5
    accuracy_threshold = 0.9
    input_key_column_name = 'input_key_column'

    def get_shift_input_fn(sequence_length, seed=None):

      def input_fn():
        random_sequence = random_ops.random_uniform(
            [sequence_length + 1], 0, 2, dtype=dtypes.int32, seed=seed)
        labels = array_ops.slice(random_sequence, [0], [sequence_length])
        inputs = math_ops.to_float(
            array_ops.slice(random_sequence, [1], [sequence_length]))
        input_key = string_ops.string_join([
            'key_', string_ops.as_string(
                random_ops.random_uniform(
                    (),
                    minval=0,
                    maxval=10000000,
                    dtype=dtypes.int32,
                    seed=seed))
        ])
        return {'inputs': inputs, input_key_column_name: input_key}, labels

      return input_fn

    seq_columns = [
        feature_column.real_valued_column(
            'inputs', dimension=cell_size)
    ]
    config = run_config.RunConfig(tf_random_seed=21212)
    sequence_estimator = ssre.multi_value_rnn_classifier(
        num_classes=num_classes,
        num_units=cell_size,
        num_unroll=num_unroll,
        batch_size=batch_size,
        input_key_column_name=input_key_column_name,
        sequence_feature_columns=seq_columns,
        learning_rate=learning_rate,
        config=config,
        predict_probabilities=True,
        queue_capacity=2 + batch_size)

    train_input_fn = get_shift_input_fn(sequence_length, seed=12321)
    eval_input_fn = get_shift_input_fn(sequence_length, seed=32123)

    sequence_estimator.fit(input_fn=train_input_fn, steps=train_steps)

    evaluation = sequence_estimator.evaluate(
        input_fn=eval_input_fn, steps=eval_steps)
    accuracy = evaluation['accuracy']
    self.assertGreater(accuracy, accuracy_threshold,
                       'Accuracy should be higher than {}; got {}'.format(
                           accuracy_threshold, accuracy))

    # Testing `predict` when `predict_probabilities=True`.
    prediction_dict = sequence_estimator.predict(
        input_fn=eval_input_fn, as_iterable=False)
    self.assertListEqual(
        sorted(list(prediction_dict.keys())),
        sorted([
            ssre.RNNKeys.PREDICTIONS_KEY, ssre.RNNKeys.PROBABILITIES_KEY,
            ssre._get_state_name(0)
        ]))
    predictions = prediction_dict[ssre.RNNKeys.PREDICTIONS_KEY]
    probabilities = prediction_dict[ssre.RNNKeys.PROBABILITIES_KEY]
    self.assertListEqual(list(predictions.shape), [batch_size, sequence_length])
    self.assertListEqual(
        list(probabilities.shape), [batch_size, sequence_length, 2])


if __name__ == '__main__':
  test.main()
