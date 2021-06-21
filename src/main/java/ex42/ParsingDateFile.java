/*
 *  UCF COP3330 Summer 2021 Assignment 3 Solution
 *  Copyright 2021 jiahao zhu
 */
package ex42;
import java.io.*;
/*
 *  UCF COP3330 Summer 2021 Assignment 3 Solution
 *  Copyright 2021 jiahao zhu
 */

import java.util.ArrayList;
import java.util.Scanner;

public class ParsingDateFile {

    public static void main(String[] args) throws FileNotFoundException{
        dataReader dr = new dataReader();
        dataWriter dw = new dataWriter();
        dataSpilter ds = new dataSpilter();
        Scanner scan = new Scanner(new File("src/main/java/ex42/exercise42_input.txt"));
        ArrayList<String> array = new ArrayList<>();
        ArrayList<String> splitedArray = new ArrayList<>();
        dr.read(scan,array);
        splitedArray = ds.split(array);
        scan.close();
        try{
            dw.dataOutput(splitedArray);
        }catch (Exception e){
            System.out.println(e);
        }
    }
}