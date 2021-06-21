/*
 *  UCF COP3330 Summer 2021 Assignment 3 Solution
 *  Copyright 2021 jiahao zhu
 */

package ex45;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Scanner;

public class wordChange {

    public static void main(String[] args) throws IOException {
        Scanner scan = new Scanner(System.in);
        System.out.print("\nEnter the output file : ");
        String outputfile = scan.next();
        dataReader dr = new dataReader();
        dr.readile();
        ArrayList<String> list = dr.getdata();
        dataWriter dw = new dataWriter(outputfile, list);
        dw.writefile();
    }

}