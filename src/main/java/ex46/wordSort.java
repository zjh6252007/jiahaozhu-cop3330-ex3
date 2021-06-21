package ex46;

import java.util.*;

public class wordSort {
    Comparator<Map.Entry<String, Integer>> valCmp = new Comparator<Map.Entry<String, Integer>>() {
        @Override
        public int compare(Map.Entry<String, Integer> o1, Map.Entry<String, Integer> o2) {
            return o2.getValue() - o1.getValue();
        }
    };
    public void sort(Map m)
    {
        List<Map.Entry<String,Integer>> list = new ArrayList<Map.Entry<String, Integer>>(m.entrySet());
        Collections.sort(list,valCmp);
        for(int i = 0 ; i < list.size(); i++)
        {
            System.out.format("%-10s",list.get(i).getKey()+":");
            for(int j = 0 ; j < list.get(i).getValue();j++)
            {
                System.out.print("*");
            }
            System.out.println();
        }
    }
}