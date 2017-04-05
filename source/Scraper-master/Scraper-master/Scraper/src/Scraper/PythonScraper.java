package Scraper;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLConnection;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.select.Elements;
import org.jsoup.nodes.Element;

import java.io.FileWriter;


public class PythonScraper {

	public static void main(String[] args) throws IOException {
		
		
		String url="https://www.tensorflow.org/api_docs/python/";
		
		String html = getUrl(url);

		/* Convert Java String to DOM document */
		Document doc = Jsoup.parse(html);
		
		Elements links = doc.select("a[href*='api_docs/python/tf']");
       // Elements media = doc.select("[src]");
        //Elements imports = doc.select("link[href]");

        System.out.println("Links:"+links.size());
        HashMap<String,String> values=new HashMap<String,String>();
        for (Element link : links) {
        	
        	// System.out.println(" * a:"+link.attr("abs:href"));
        	values.put(link.attr("abs:href"), link.attr("abs:href"));
        	
        }
		
        
        System.out.println("Hashmap:"+values.size());
   	    List<ValueBean> finalList=new ArrayList<ValueBean>();
	 
   	 FileWriter fstream;
     BufferedWriter out;

     // create your filewriter and bufferedreader
     fstream = new FileWriter("values.txt");
     out = new BufferedWriter(fstream);

     
        for (String key : values.keySet()) {
            
        	String html1 = getUrl(key);
        	Document doc1 = Jsoup.parse(html1);
        	
        	Elements paras = doc1.select("p a code");
        	
        	//System.out.println(doc1.toString().contains("Defined in"));
        	
        	System.out.println("para new :"+paras.size());
        	
        	for (Element para : paras) {
            	
            	System.out.println(" * a:"+para.text());
            	values.put(key,para.text());
            	ValueBean valueBean=new ValueBean();
            	valueBean.setKey(key);
            	valueBean.setValue(para.text());
            	
            	finalList.add(valueBean);
            	if(para.text().endsWith(".py"))
            	    out.write(key+","+para.text()+ "\n");
            }
        	

           
            	
            	
           
        	
        	/*List<Map<String, String>> collection = new ArrayList<>();
        	collection.add(values);
        	try {
				writeCollection(new File("excel1.xlsx"),"sheet1",collection);
			} catch (Exception e) {
				// TODO Auto-generated catch block
				System.out.println("Error"+e.getMessage());
			}*/
        
        	 
        	//List<Map<String, String>> collection = new ArrayList<>();
        	//collection.add(values);
        	
        	//Map<String, List<ValueBean>> mpa = new HashMap<String, List<ValueBean>>();
            //mpa.put("Latency", finalList);
            
        	//ExcelUtil.writeToExcel(mpa,"sheet",ValueBean.class);
        	
        //	Map<String, List<ValueBean>> mpa = new HashMap<String, List<ValueBean>>();
          //  mpa.put("Latency", finalList);
            //ExcelUtil.writeToExcel(mpa,"hhh" ,ValueBean.class);
            
        }
        
        
        out.close();
        
	}
	
	
	/*
	 * get the url's document
	 */
	public static String getUrl(String url){
		URL urlObj = null;
		try{
			urlObj = new URL(url);
		}
		catch(MalformedURLException e){
			System.out.println("The url was malformed!");
			return "";
		}
		URLConnection urlCon = null;
		BufferedReader in = null;
		String outputText = "";
		try{
			urlCon = urlObj.openConnection();
			in = new BufferedReader(new
					InputStreamReader(urlCon.getInputStream()));
			String line = "";
			while((line = in.readLine()) != null){
				outputText += line;
			}
			in.close();
		}catch(IOException e){
			System.out.println("There was an error connecting to the URL"+url);
			return "";
		}
		return outputText;
	}

	
	
}
