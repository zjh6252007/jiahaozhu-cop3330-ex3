package ex45;

import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;

class dataWriter{


    private FileWriter writer;
    private int count_Modification;
    private ArrayList<String> list;


    public dataWriter(String name, ArrayList<String> list) throws IOException {

        writer = new FileWriter("src/main/java/ex45/"+name);
        this.list = list;

    }


    public void writefile() throws IOException {

        for(int i=0;i<list.size();i++) {
            String temp = list.get(i);
            String str = "utilize";
            int index = 0;

            while (true)
            {
                index = temp.indexOf(str, index);
                if (index != -1)
                {
                    count_Modification ++;
                    index += str.length();
                }
                else {
                    break;
                }
            }

            temp = temp.replaceAll("utilize", "use");
            writer.write(temp+"\n");
        }

        writer.close();

    }

    public int getModification() {

        return count_Modification;

    }

}