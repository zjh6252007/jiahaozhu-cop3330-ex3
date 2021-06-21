package ex45;

import java.io.File;
import java.io.FileNotFoundException;
import java.util.ArrayList;
import java.util.Scanner;

class dataReader{

    private ArrayList<String> list;
    private Scanner sc;

    public dataReader() throws FileNotFoundException {
        list = new ArrayList<String>();
        File file = new File("src/main/java/ex45/exercise45_input.txt");
        sc = new Scanner(file);

    }
    public void readile() {

        try
        {
            int i=0;
            while( sc.hasNext() )
            {
                String filedata = sc.nextLine();
                list.add(filedata);
            }
        }
        finally
        {
            sc.close();
        }
    }
    public ArrayList<String> getdata() {
        return list;
    }

}

