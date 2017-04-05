package Scraper;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.lang.reflect.Field;
import java.util.Collection;
import java.util.List;
import java.util.Map;

import org.apache.poi.hssf.usermodel.HSSFCellStyle;
import org.apache.poi.hssf.usermodel.HSSFFont;
import org.apache.poi.hssf.usermodel.HSSFRichTextString;
import org.apache.poi.hssf.usermodel.HSSFRow;
import org.apache.poi.hssf.usermodel.HSSFSheet;
import org.apache.poi.hssf.usermodel.HSSFWorkbook;
import org.apache.poi.hssf.util.HSSFColor;



public class ExcelUtil<T extends Comparable<?>> {

	private static HSSFCellStyle getHeaderStyle(HSSFWorkbook workBook) {
		HSSFCellStyle styleHeader = workBook.createCellStyle();
		HSSFFont font = workBook.createFont();
		font.setBoldweight(HSSFFont.BOLDWEIGHT_BOLD);
		font.setColor(HSSFColor.WHITE.index);
		styleHeader.setFont(font);
		styleHeader.setFillForegroundColor(HSSFColor.BLUE.index);
		styleHeader.setFillPattern(HSSFCellStyle.SOLID_FOREGROUND);

		return styleHeader;
	}

	public static <T extends Comparable<?>> void writeToExcel(Collection<T> list, String fileName, Class<T> clazz) throws IllegalArgumentException, IllegalAccessException{
		HSSFWorkbook workBook = new HSSFWorkbook();
		createSheet(list,workBook,fileName,clazz);

		try {
			writeWBToStream(fileName,workBook);
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	public static <T extends Comparable<?>> void writeToExcel(Map<String, List<T>> map, String fileName,Class<T> clazz)  throws IllegalArgumentException, IllegalAccessException, InstantiationException{
		HSSFWorkbook workBook = new HSSFWorkbook();
		for (String sheetName : map.keySet()){
			createSheet(map.get(sheetName), workBook, sheetName, clazz);
		}

		try {
			writeWBToStream(fileName,workBook);
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	public static <T extends Comparable<?>> void createSheet(Collection<T> list,HSSFWorkbook workBook, String sheetName,Class<T> clazz) throws IllegalArgumentException, IllegalAccessException{
		int rowNo = 0;
		//YDataLogger.out("2^^^^^^^^^^sheetName -> "+sheetName);
		HSSFSheet sheet;

		if (sheetName.contains(":/") || sheetName.contains(":\\")){
			sheet = workBook.createSheet();
		}else{
			sheet = workBook.createSheet(sheetName);
		}

		 writeInSheet(list, workBook, sheet,0, clazz);

	}

	private static void writeWBToStream(String fileName,HSSFWorkbook workBook) throws IOException{
		FileOutputStream outStream = new FileOutputStream(fileName);
		workBook.write(outStream);
		outStream.flush();
		outStream.close();
	}


	public static <T extends Comparable<?>> void appendToExcel(Map<String, List<T>> map, String fileName,Class<T> clazz)  throws IllegalArgumentException, IllegalAccessException, InstantiationException, IOException
	{  // YDataLogger.out("2^^^^^^^^^^^^ append");
		FileInputStream file = new FileInputStream(new File(fileName));
		HSSFWorkbook workBook = new HSSFWorkbook(file);
		for (String sheetName : map.keySet())
		{
		   // YDataLogger.out("2^^^^^^^^^^^^ append"+sheetName);
			appendToSheet(map.get(sheetName), workBook, sheetName, clazz);
		}   
		writeWBToStream(fileName,workBook);		

	}


	public static <T extends Comparable<?>> void appendToSheet(Collection<T> list,HSSFWorkbook workBook, String sheetName,Class<T> clazz) throws IllegalArgumentException, IllegalAccessException
	{	
			HSSFSheet sheet = workBook.getSheetAt(0);
			int numRows=sheet.getPhysicalNumberOfRows();
		    //YDataLogger.out("2^^^^^^^^^^^^ append"+numRows);
            writeInSheet(list, workBook, sheet, numRows, clazz);
	}


	public static <T extends Comparable<?>> void writeInSheet(Collection<T> list,HSSFWorkbook workBook,HSSFSheet sheet, int numRows ,Class<T> clazz) throws IllegalArgumentException, IllegalAccessException
	{	
			int rowNo=0;            
			for (T containerObj : list){
				Field f[] = clazz.getDeclaredFields();

				if(rowNo == 0){
					HSSFRow headerRow = sheet.createRow(rowNo);
					for(int i = 0 ; i < f.length ; i++){
						f[i].setAccessible(true);
						headerRow.createCell((short)i).setCellStyle(getHeaderStyle(workBook));
						headerRow.getCell(i).setCellValue(new HSSFRichTextString(f[i].getName().toUpperCase()));
					}
					rowNo = rowNo+1;
				}
				HSSFRow row = sheet.createRow(numRows+rowNo);
				for(int i = 0 ; i < f.length ; i++){
					  // YDataLogger.out("2^^^^^^^^^^^^ append write");
					f[i].setAccessible(true);
					Object obj = f[i].get(containerObj);
					if(obj==null)
						row.createCell((short)i).setCellValue(new HSSFRichTextString(" "));
					else
					    row.createCell((short)i).setCellValue(new HSSFRichTextString(obj+""));
				}
				rowNo = rowNo+1;
			}
	}

	
}