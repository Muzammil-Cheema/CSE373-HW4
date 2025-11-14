import java.util.*;

public class SetCover {

    private List<BitSet> bestSolution = null;
    private int bestSolutionSize;

    public Functions.Pair<List<BitSet>, Integer> setCover(BitSet universe, List<BitSet> subsets) {

        bestSolutionSize = subsets.size() + 1;
        bestSolution = null;

        // Mandatory selections
        Functions.Triple<BitSet, List<BitSet>, List<BitSet>> forced = Functions.forcedSetSelections(universe, new BitSet(), cloneListBS(subsets), new ArrayList<>());

        backtrack(universe, forced.covered(), forced.candidates(), forced.current());

        if (bestSolution != null)
            return new Functions.Pair<>(bestSolution, bestSolutionSize);

        return new Functions.Pair<>(null, -1);
    }

    private void backtrack(BitSet universe, BitSet covered, List<BitSet> candidates, List<BitSet> currentSets) {

        // Solution found
        if (covered.equals(universe)) {
            if (currentSets.size() < bestSolutionSize) {
                bestSolutionSize = currentSets.size();
                bestSolution = currentSets;
            }
            return;
        }

        // early return from recursion
        if (currentSets.size() >= bestSolutionSize) return;
        if (candidates.isEmpty()) return;
        if (!Functions.isSolutionPossible(universe, covered, candidates)) return;

        for (BitSet s : candidates) {
            BitSet contribution = cloneBS(universe);
            contribution.andNot(covered);
            contribution.and(s);

            if (contribution.isEmpty()) continue; // contributes nothing

            // new covered
            BitSet newCovered = cloneBS(covered);
            newCovered.or(s);

            // new current sets list
            List<BitSet> newCurrent = new ArrayList<>(currentSets);
            newCurrent.add(s);

            // prune candidates
            List<BitSet> newCandidates = Functions.dynamicPruneSubsets(newCovered, candidates);

            backtrack(universe, newCovered, newCandidates, newCurrent);
        }
    }

    //  Cloning functions for mutation safety

    private BitSet cloneBS(BitSet original) {
        return (BitSet) original.clone();
    }

    private BitSet emptyBS(BitSet template) {
        return new BitSet(template.size());
    }

    private List<BitSet> cloneListBS(List<BitSet> list) {
        List<BitSet> out = new ArrayList<>(list.size());
        for (BitSet bs : list) {
            out.add((BitSet) bs.clone());
        }
        return out;
    }
}
