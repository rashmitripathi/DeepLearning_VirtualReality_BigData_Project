
function showTopActivities(){
	 
	 console.log(" show top activities");	
	 alignButtonVertically();
	 //setGraphClass();	
	 
	var fill = d3.scale.category20();
	var cityData = [],
		cityPop = [], 
	    width = 3000, 
	    height = 1800;
	d3.csv("popularword.csv", function(data) {
		console.log(" read csv");
	    // build the list of city names
	    data.forEach( function (d) {
	        cityData.push(d.word);
	       // console.log(d.population);
	        cityPop.push(d.count);
	    });
	    d3.layout.cloud().size([600, 600])
	        .words(cityData.map(function(_,i) {
	         console.log(cityData[i] + " " + cityPop[i] );
	            return {text: cityData[i], size:10 + cityPop[i] / 100};
	        }))
	        .rotate(function() { return ~~(Math.random() * 2) * 90; })
	        .font("Impact")
	        .fontSize(function(d) { return d.size; })
	        .on("end", draw)
	        .start();
	});
	function draw(words) {
		console.log("draw" );
		/*if(document.getElementById("graph").firstChild)
		{
		   console.log("svg graph is present"+ document.getElementsByTagName("svg").innerHTML );
		   //mydiv=document.getElementById('graph');
		   //mydiv.removeChild( mydiv.firstChild );
		   //d3.select("#graph").remove("svg");
		   
		}*/
		
	d3.select("#graph").append("svg")
	    .attr("width", 800)
	    .attr("height",800)
	    .append("g")
	    .attr("transform", "translate(400,400)")
	    .selectAll("text")
	    .data(words)
	    .enter().append("text")
	    .style("font-size", function(d) { 
	    console.log(words);
	    return (d.size-10)+"px"; })
	    .style("font-family", "Impact")
	    .style("fill", function(d, i) { return fill(i); })
	    .attr("text-anchor", "middle")
	    .attr("transform", function(d) {
	        return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
	    })
	    .text(function(d) { return d.text; });
	}	
    
}

function showRisky(){
	
	alert("value"+"queryRiskyActivities");
    document.forms[0].action = "queryRiskyActivities"
    document.forms[0].submit();
    
    //all work is done by servlet

}



function showAgeGroup(){
	
	alignButtonVertically();
	setGraphClass();
	var processed_json = new Array(); 
		//usage:
		readTextFile("agegroup.json", function(text){
		    var data = JSON.parse(text);
		    console.log(data);	   
		    
		    // Populate series
	        for (i = 0; i < data.length; i++){
	            processed_json.push([data[i].ageGroup, data[i].count]);
	        }
		    
		    
	        chart = new Highcharts.Chart({
	            chart: {
	                renderTo: 'graph',
	                type: 'pie'
	            },
	            title:
	            {
	            	text: 'Different Age Groups Talking about their hobbies on sample 100 Tweets using uClassify API'
	            	
	            },
	            plotOptions: {
	                pie: {
	                    showInLegend: false,
	                    dataLabels: {
	                        formatter: function(){
	                            console.log(this);
	                                 this.point.visible = true;
	                                return this.key;
	                            }
	    					   }
	                        }
	                    
	            },
	            
	            
	            series: [{
	            	data:processed_json 
	            }]
	        });
	        
		});
		
	
}


function showHashTags(){
	
	 alignButtonVertically();
	 setGraphClass();
	 var processed_json = new Array(); 
	 var processed_xaxis = new Array(); 
	
	readTextFile("tophashtags.json", function(text){
	    var data = JSON.parse(text);
	    console.log(data);	   
	    
	    // Populate series
        for (i = 0; i < data.length; i++){
            processed_json.push([data[i].value, data[i].count]);
        }
	    
        for (i = 0; i < data.length; i++){
            processed_xaxis.push(data[i].value);
        }
	    
	    chart = new Highcharts.Chart({
	        chart: {
	        	renderTo: 'graph',
	            type: 'column'
	        },
	        title: {
	        	text:'Top Hashtags Across Globe'
	        },
	        xAxis: {
	            type: 'Age-Group',
	            categories: processed_xaxis
	        },
	        yAxis: {
	            title: {
	                text: 'No of People'
	            }
	        },
	        legend: {
	            enabled: false
	        },
	        plotOptions: {
	            series: {
	                borderWidth: 0,
	                dataLabels: {
	                    enabled: true,
	                    format: '{point.y:.1f}'
	                }
	            }
	        },
	        tooltip: {
	            headerFormat: '<span style="font-size:11px">{series.name}</span><br>',
	            pointFormat: '<span style="color:{point.color}">{point.name}</span>: <b>{point.y:.2f}%</b> of total<br/>'
	        },
	        series: [{
	        	name: 'AgeGroup',
	            colorByPoint: true,
	            data:processed_json
	        }]       
	       

	    });
	});
	
	
	
}


function showTopCountries(){
	
	alignButtonVertically();
	document.getElementById('graph').setAttribute("class", "graphMap");
	
	var processed_json = new Array(); 
	//usage:
	readTextFile("country.json", function(text){
	    var data = JSON.parse(text);
	    console.log(data);	   
	    
	    // Populate series
	    processed_json.push( ['Country', 'Popularity']);
        for (i = 0; i < data.length; i++){
            processed_json.push([data[i].country, data[i].count]);
        }
        
        
        //var options = {};
        
        var options = {
        //colorAxis: {colors: ['yellow','red','green','FUCHSIA','purple', 'blue']},
        colorAxis: {colors: ['yellow','green', 'blue']},
        title:'Country wise tweets except US', 		
        //colorAxis: {colors: ['#00853f', 'yellow', '#e31b23']},		
        backgroundColor: '#81d4fa',
        datalessRegionColor: 'white',
        defaultColor: '#f5f5f5',
        showLegend: 'true',
        sizeAxis:{ maxValue: 10000}
        //displayMode: 'text'
              };
        
        var data1 = google.visualization.arrayToDataTable(processed_json);

        var chart = new google.visualization.GeoChart(document.getElementById('graph'));

        chart.draw(data1, options);
        
	});    
    
    

      
      
}


function readTextFile(file, callback) {
    var rawFile = new XMLHttpRequest();
    rawFile.overrideMimeType("application/json");
    rawFile.open("GET", file, true);
    rawFile.onreadystatechange = function() {
        if (rawFile.readyState === 4 && rawFile.status == "200") {
            callback(rawFile.responseText);
        }
    }
    rawFile.send(null);
}



function alignButtonVertically()
{
	 document.getElementById('bodybutton').setAttribute("class", "afterClick");
	 var x = document.getElementById("bodybutton");
	 var y = x.getElementsByTagName("form");
	 var i;
	 for (i = 0; i < y.length; i++) {
	     y[i].setAttribute("class", "");
	     y[i].getElementsByTagName("input")[0].setAttribute("class", "btn btn-circlesmall");
	 }
}

function setGraphClass()
{
	document.getElementById('graph').setAttribute("class", "graphContainer");
   
}





function showPackageStructure()
{
     alignButtonVertically();
	 setGraphClass();
    var treeData = [
  {
    "name": "Top Level",
    "parent": "null",
    "children": [
      {
        "name": "Level 2: A",
        "parent": "Top Level",
        "children": [
          {
            "name": "Son of A",
            "parent": "Level 2: A"
          },
          {
            "name": "Daughter of A",
            "parent": "Level 2: A"
          }
        ]
      },
      {
        "name": "Level 2: B",
        "parent": "Top Level"
      }
    ]
  }
];

// ************** Generate the tree diagram  *****************
var margin = {top: 20, right: 120, bottom: 20, left: 120},
 width = 960 - margin.right - margin.left,
 height = 500 - margin.top - margin.bottom;
 
var i = 0;

var tree = d3.layout.tree()
 .size([height, width]);

var diagonal = d3.svg.diagonal()
 .projection(function(d) { return [d.y, d.x]; });

var svg = d3.select("body").append("svg")
 .attr("width", width + margin.right + margin.left)
 .attr("height", height + margin.top + margin.bottom)
  .append("g")
 .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

root = treeData[0];
  
update(root);

function update(source) {

  // Compute the new tree layout.
  var nodes = tree.nodes(root).reverse(),
   links = tree.links(nodes);

  // Normalize for fixed-depth.
  nodes.forEach(function(d) { d.y = d.depth * 180; });

  // Declare the nodesâ€¦
  var node = svg.selectAll("g.node")
   .data(nodes, function(d) { return d.id || (d.id = ++i); });

  // Enter the nodes.
  var nodeEnter = node.enter().append("g")
   .attr("class", "node")
   .attr("transform", function(d) { 
    return "translate(" + d.y + "," + d.x + ")"; });

  nodeEnter.append("circle")
   .attr("r", 10)
   .style("fill", "#fff");

  nodeEnter.append("text")
   .attr("x", function(d) { 
    return d.children || d._children ? -13 : 13; })
   .attr("dy", ".35em")
   .attr("text-anchor", function(d) { 
    return d.children || d._children ? "end" : "start"; })
   .text(function(d) { return d.name; })
   .style("fill-opacity", 1);

  // Declare the linksâ€¦
  var link = svg.selectAll("path.link")
   .data(links, function(d) { return d.target.id; });

  // Enter the links.
  link.enter().insert("path", "g")
   .attr("class", "link")
   .attr("d", diagonal);

}
}
