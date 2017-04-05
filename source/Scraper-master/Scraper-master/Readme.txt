To whom it may concerned,
Introduction:
This is a Walmart web crawler in java. The program have two functionalities.
If the input is only one argument, like "digital camera", the program will show up the total results of that item on walmart.com.
If the input is two arguments, like "digital camera" and 2, the program will show up the item list in the Page 2.
	For Example:
************************************
		item 1.
		price 10.
************************************
		item 2.
		price 20.
************************************		
		item 3.
		price 30.
************************************		
		item 4.
		price 40.
************************************

Files list:
"Scaper" folder is the source code of this program.
Download scraper.jar to run the program in the terminal.

How to Run:
open your teminal or cmd window and type command like below:

This program handle the two queries below:
Query 1: (requires a single argument)
java -jar scraper.jar <keyword> (e.g. java -jar Assignment.jar "digital camera")
Query 2: (requires two arguments)
java -jar scraper.jar <keyword> <page number> (e.g. java -jar Assignment.jar "digital camera" 2)

The program using Jsoup library. You can find it in the source code folder(\Assignment\Scraper\lib).

Test cases:
I have made some test about the program, working good for me.
below are 3 basic test cases:
1. keyward : "digital camera"
   test : show results list from page 1 to page 30
   expect result: no error and price show correctly
   actural result : good;
2. keyward : "asdsdas"
   test : show results list from page 1 to page 30
   expect result: no error, only one page, price show correctly and no result showed up from 2nd page
   actural result : good;
3. keyward : ""/"  "
   test : show results list from page 1 to page 30
   expect result: no error, no page should show
   actural result : good;

Hope works good

Best,

Fei Deng

