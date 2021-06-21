package ex46;

import java.io.*;

public class wordCounter {
    public int count(String input,File f) throws IOException {
        FileReader fr = new FileReader(f);
        BufferedReader br = new BufferedReader(fr);
        int count=0;
        String[] words = null;
        String s;
        while((s=br.readLine())!=null)
        {
            words=s.split(" ");
            for (String word : words)
            {
                if (word.equals(input))
                {
                    count++;
                }
            }
        }
        br.close();
        return count;
    }
}
