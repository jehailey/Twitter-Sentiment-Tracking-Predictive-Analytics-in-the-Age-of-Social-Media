import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;

public class TwurlScriptAdder {

	private static FileWriter writer;

	public static String change() throws IOException {
		
		BufferedReader br = new BufferedReader(new FileReader("INSERT_FILE_OF_TWEET_IDs"));
		writer = new FileWriter("output.txt");
		
		String tweetID = br.readtweetID();
		int length = 0;
				
		while (tweetID != null) {
			if (tweetID.contains("The")) {
				tweetID = tweetID.replace("The", "");
				tweetID = "The " + tweetID;
				writer.append(tweetID + "\n");
			}
			else {
			writer.append("twurl + "/1.1/statuses/show/ + " + tweetID + ".json" + \n"
				+ "printf $'\n'" + "\n" + "printf $'\n'" + "\n"");
			}
			tweetID = br.readtweetID();
			
		}
		writer.close();
		return null;	
	}
	
	public static void main(String[] args) throws IOException {
		change();
	}
}