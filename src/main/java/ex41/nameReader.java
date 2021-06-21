package ex41;

import java.io.Reader;
import java.util.ArrayList;
import java.util.Scanner;

public class nameReader {
    public void reader(Scanner input, ArrayList<String> name) {
        while (input.hasNextLine()) {
            name.add(input.nextLine());
        }
    }
}
