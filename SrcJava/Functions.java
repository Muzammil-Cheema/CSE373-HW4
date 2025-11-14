import java.io.*;
import java.util.*;


public class Functions {


    /**
     * Reads a set cover problem file.
     * <p>
     * File format:
     * Line 1: n (size of universe)
     * Line 2: m (number of subsets)
     * Lines 3...: space-separated integers in each subset
     *
     * @param filename
     * Path to the file
     * @return ProblemData<BitSet, List<BitSet>>
     * a Pair containing the universe BitSet and a List of subset BitSets
     * @throws
     * IOException if file is not found
     */
    public static Pair<BitSet, List<BitSet>> readSetCoverFile(String filename) throws IOException {
        BufferedReader reader = new BufferedReader(new FileReader(filename));
        String line;

        // Read universe size
        int n = Integer.parseInt(reader.readLine().trim());

        // Read number of subsets
        int m = Integer.parseInt(reader.readLine().trim());

        List<BitSet> subsetBitSets = new ArrayList<>();

        // Read each subset and build BitSet directly
        for (int i = 0; i < m; i++) {
            line = reader.readLine();
            if (line != null && !line.trim().isEmpty()) {
                BitSet bitset = new BitSet(n);
                String[] elements = line.trim().split("\\s+");
                for (String e : elements) {
                    int val = Integer.parseInt(e);
                    bitset.set(val - 1);
                }
                subsetBitSets.add(bitset);
            }
        }

        reader.close();

        // Universe BitSet
        BitSet universe = new BitSet(n);
        universe.set(0, n);

        // TODO: call pruneProperSubsets if needed on subsetBitSets
         subsetBitSets = pruneProperSubsets(subsetBitSets);

        return new Pair<>(universe, subsetBitSets);
    }


    /**
     * Removes all proper subsets from a list of BitSets.
     * <p>
     * A "proper subset" is a set that is fully contained within another set in the list.
     * This method iterates over each BitSet and checks whether it is a proper subset of any other BitSet in the list.
     * Only sets that are not proper subsets of any other are retained.
     *
     * @param bitsets the input list of BitSets
     * @return a new list of BitSets with proper subsets removed
     */
    private static List<BitSet> pruneProperSubsets(List<BitSet> bitsets) {
        List<BitSet> pruned = new ArrayList<>();
        BitSet candidate, other, temp;
        boolean is_subset;
        for (int i = 0; i < bitsets.size(); i++) {
            candidate = bitsets.get(i);
            is_subset = false;

            for (int j = 0; j < bitsets.size(); j++) {
                if (i == j) continue;
                other = bitsets.get(j);
                temp = (BitSet) candidate.clone();
                temp.andNot(other);
                if (temp.isEmpty()) {
                    is_subset = true;
                    break;
                }
            }

            if (!is_subset)
                pruned.add(candidate);
        }
        return pruned;
    }


    /**
     * Pure function that prunes functionally duplicate subsets. <p>
     * 1. Eliminates subsets that add no uncovered elements. <p>
     * 2. If multiple subsets add the same uncovered elements,
     *    keeps only the one with minimal cardinality.
     *
     * @param covered  BitSet of already-covered elements
     * @param subsets  candidate subsets
     * @return pruned list of subsets
     */
    public static List<BitSet> dynamicPruneSubsets(BitSet covered, List<BitSet> subsets) {

        // Map: uncoveredElementsKey -> smallest subset that covers those elements
        Map<String, BitSet> pruned = new HashMap<>();

        for (BitSet s : subsets) {
            // Compute uncovered = s \ covered
            BitSet uncovered = (BitSet) s.clone();
            uncovered.andNot(covered);

            if (uncovered.isEmpty())
                continue; // contributes nothing new

            // Use string representation for faster, safer, immutable key storage.
            String key = uncovered.toString();
            BitSet best = pruned.get(key);

            // If no candidate exists yet for this uncovered pattern
            if (best == null) {
                pruned.put(key, (BitSet) s.clone());
                continue;
            }

            // Otherwise, keep the one with smaller cardinality
            if (s.cardinality() < best.cardinality())
                pruned.put(key, (BitSet) s.clone());
        }

        return new ArrayList<>(pruned.values());
    }


    public static Triple<BitSet, List<BitSet>, List<BitSet>> forcedSetSelections(
            BitSet universe, BitSet covered, List<BitSet> candidates, List<BitSet> current) {
        BitSet covered_clone = (BitSet) covered.clone();

        int n = universe.length();
        int[] elementFrequency = new int[n];

        // Count frequency of each uncovered element
        for (BitSet candidate : candidates)
            for (int i = 0; i < n; i++)
                if (!covered_clone.get(i) && candidate.get(i))
                    elementFrequency[i]++;

        // Find mandatory sets (those that uniquely cover an uncovered element)
        List<BitSet> mandatorySets = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            if (elementFrequency[i] == 1) {
                for (BitSet candidate : candidates) {
                    if (candidate.get(i)) {
                        mandatorySets.add((BitSet) candidate.clone());
                        break;
                    }
                }
            }
        }

        // Remove functional duplicates
        mandatorySets = dynamicPruneSubsets(covered_clone, mandatorySets);

        // Update covered, candidates, and current sets
        for (BitSet s : mandatorySets)
            covered_clone.or(s);

        List<BitSet> newCandidates = new ArrayList<>();
        for (BitSet candidate : candidates) {
            if (!mandatorySets.contains(candidate)) {
                newCandidates.add(candidate);
            }
        }

        // TODO: Check if copying is necessary
        List<BitSet> newCurrent = new ArrayList<>(current.size());
        for (BitSet bitset : current)
            newCurrent.add( (BitSet)bitset.clone());
        newCurrent.addAll(mandatorySets);

        return new Triple<>(covered_clone, newCandidates, newCurrent);
    }



    public static boolean isSolutionPossible(BitSet universe, BitSet covered, List<BitSet> candidates){
        BitSet uncovered = (BitSet) universe.clone();
        uncovered.andNot(covered);
        BitSet coverage = new BitSet();
        for (BitSet candidate : candidates)
            coverage.or(candidate);
        coverage.and(uncovered);
        return coverage.equals(uncovered);
    }


    public static String bitSetToString(BitSet bs) {
        StringBuilder sb = new StringBuilder();
        sb.append("{");

        boolean first = true;
        for (int i = bs.nextSetBit(0); i >= 0; i = bs.nextSetBit(i + 1)) {
            if (!first) sb.append(", ");
            sb.append(i + 1);    // convert back to 1-based indexing
            first = false;
        }

        sb.append("}");
        return sb.toString();
    }


    /**
     * Create a BitSet object from a Set collection of Integer objects
     * @param n the size of the BitSet. Must be >= maximum element in the Set
     * @param s the Set of integers we want to convert into a BitSet
     * @return a BitSet that represents which elements are in the Set
     */
    private static BitSet fromSet(int n, Set<Integer> s) {
        BitSet bs = new BitSet(n);
        for (int val : s) {
            bs.set(val - 1);
        }
        return bs;
    }

    // Simple Pair record for returning two objects
    public record Pair<U, V>(U universe, V bitsets) {}
    public record Triple<T, U, V>(T covered, U candidates, V current) {}
}
