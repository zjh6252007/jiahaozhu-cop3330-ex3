/*
 *  UCF COP3330 Summer 2021 Assignment 3 Solution
 *  Copyright 2021 jiahao zhu
 */

package ex46;
import java.io.File;
import java.io.IOException;
import java.util.Map;
import java.util.TreeMap;

public class frequencyFinder

{
    public static void main(String[] args) throws IOException

    {
        File f=new File("src/main/java/ex46/exercise46_input.txt");
        String[] words= null;
        wordCounter wc = new wordCounter();
        wordSort ws = new wordSort();
        Map<String,Integer> m = new TreeMap<String, Integer>();
        m.put("badger", wc.count("badger",f));
        m.put("mushroom", wc.count("mushroom",f));
        m.put("snake", wc.count("snake",f));
        ws.sort(m);
    }

}