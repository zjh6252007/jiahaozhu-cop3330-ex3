package ex42;

import java.util.ArrayList;

public class dataSpilter {
    public static ArrayList<String> split(ArrayList<String> data) {
        ArrayList<String> splitedData = new ArrayList<>();
        for (int i = 0; i < data.size(); i++) {
            String temp[] = data.get(i).split(",");
            for (int j = 0; j < temp.length; j++) {
                splitedData.add(temp[j]);
            }
        }
        return splitedData;
    }
}
