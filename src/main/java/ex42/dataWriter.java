package ex42;

import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;

public class dataWriter {
    public void dataOutput(ArrayList<String> data) throws IOException {
        FileWriter writer = new FileWriter("src/main/java/ex42/exercise42_output.txt");
        PrintWriter pwriter = new PrintWriter(writer);
        pwriter.write("Last     First     Salary\n");
        pwriter.write("--------------------------\n");
        int count = 1;
        for (String i : data) {
            pwriter.format("%-10s", i);
            if (count % 3 == 0) {
                pwriter.write("\n");
            }
            count++;
        }
        writer.close();
    }
}