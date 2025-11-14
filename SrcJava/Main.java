import java.util.*;

public class Main {

    public static void main(String[] args) {

        if (args.length != 1) {
            System.out.println("Usage: java Main <filename>");
            System.out.println("Example: java Main s-k-30-50");
            return;
        }

        String folder = "Data/";
        String filename = args[0];

        runFile(folder + filename);
    }


    public static void runFile(String filepath) {
        System.out.println("Running file: " + filepath);

        Functions.Pair<BitSet, List<BitSet>> p;
        try {
            p = Functions.readSetCoverFile(filepath);
        } catch (Exception e) {
            System.out.println("Error reading file: " + e.getMessage());
            return;
        }

        BitSet universe = p.universe();
        List<BitSet> subsets = p.bitsets();

        long start = System.nanoTime();

        SetCover solver = new SetCover();
        Functions.Pair<List<BitSet>, Integer> result =
                solver.setCover(universe, subsets);

        long end = System.nanoTime();
        double seconds = (end - start) / 1e9;

        System.out.printf("Execution time: %.6f seconds%n", seconds);

        List<BitSet> solution = result.universe();
        int size = result.bitsets();

        if (solution == null || size == -1) {
            System.out.println("No solution found.");
            System.out.println();
            return;
        }

        System.out.println("Cover size: " + size);
        for (BitSet bs : solution) {
            System.out.println(Functions.bitSetToString(bs));
        }

        System.out.println();
    }
}
