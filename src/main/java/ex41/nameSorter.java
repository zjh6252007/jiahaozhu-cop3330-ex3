/*
 *  UCF COP3330 Summer 2021 Assignment 3 Solution
 *  Copyright 2021 jiahao zhu
 */
package ex41;
import java.io.*;
/*
 *  UCF COP3330 Summer 2021 Assignment 3 Solution
 *  Copyright 2021 jiahao zhu
 */

import java.util.ArrayList;
import java.util.Collections;
import java.util.Scanner;

public class nameSorter {
    public static void main(String[] args) throws FileNotFoundException {
        nameWriter nr = new nameWriter();
        nameReader rd= new nameReader();
        Scanner scan = new Scanner(new File("src/main/java/ex41/exercise41_input.txt"));
        ArrayList<String> name = new ArrayList<>();
        rd.reader(scan,name);
        Collections.sort(name, String.CASE_INSENSITIVE_ORDER);
        scan.close();

        try{
            nr.nameOutput(name);
        }
        catch (Exception e){
            System.out.println(e);
        }
    }
}
