package ex41;

import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;

public class nameWriter {
    public void nameOutput(ArrayList<String> name) throws IOException {
        FileWriter writer = new FileWriter("src/main/java/ex41/exercise41_output.txt");
        writer.write("Total of " + name.size() + " names\n");
        writer.write("----------------------\n");

        for(String i : name)
        {
            writer.write(i+"\n");
        }
        writer.close();
    }
}
