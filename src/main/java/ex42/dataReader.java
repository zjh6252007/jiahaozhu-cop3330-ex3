package ex42;

import java.util.ArrayList;
import java.util.Scanner;

public class dataReader {
    public void read(Scanner input, ArrayList<String> data)
    {
        while(input.hasNextLine()){
            data.add(input.nextLine());
        }
    }
}

