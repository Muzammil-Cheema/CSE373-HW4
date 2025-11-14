# Ignores empty subsets, since they will never be used.
# Accepts absolute file path or relative file path within project directory
def read_set_cover_file(filename):
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f]

    n = int(lines[0])  # number of elements
    m = int(lines[1])  # number of subsets

    universe = set(range(1, n + 1))
    subsets = []

    for i in range(2, 2 + m):
        subset = set(map(int, lines[i].split()))
        if subset:  # Exclude empty sets
            subsets.append(subset)

    subsets = prune_proper_subsets(subsets)
    return set_to_bitmask(universe), [set_to_bitmask(s) for s in subsets]


## Removes proper subsets from a list of sets.
def prune_proper_subsets(subsets: list[set[int]]) -> list[set[int]]:
    pruned = []
    for s1 in subsets:
        if not any(s1 < s2 for s2 in subsets if s1 != s2): # Keep s1 only if it is not a proper subset of any other subset
            pruned.append(s1)
    return pruned


def dynamic_prune_subsets(universe: int, covered: int, subsets: list[int]) -> list[int]:
    """
    Prune subsets for each set cover recursion step

    1) Remove subsets that contribute no new elements.
    2) If multiple sets contribute the same new elements, keep the smallest set and discard the rest.
    """
    pruned = {}
    for s in subsets:
        u = universe & ~covered & s
        if u == 0: continue
        # Keep the smallest subset for this uncovered pattern
        if u not in pruned or bin(s).count('1') < bin(pruned[u]).count('1'):
            pruned[u] = s

    # Return the list of minimal subsets (one per uncovered pattern)
    return list(pruned.values())


def forced_set_selections(universe, covered, candidate_sets, current_sets):
    n = universe.bit_length()
    element_frequency = [0] * n

    for s in candidate_sets:
        for i in range(n):
            if not (covered & (1 << i)) and (s & (1 << i)):
                element_frequency[i] += 1

    mandatory_sets = []
    for i, freq in enumerate(element_frequency):
        if freq == 1: # Find the candidate set containing this unique uncovered element
            for s in candidate_sets:
                if s & (1 << i):
                    mandatory_sets.append(s)
                    break

    # Remove functional duplicates using dynamic pruning
    mandatory_sets = dynamic_prune_subsets(universe, covered, mandatory_sets)

    for s in mandatory_sets: covered |= s
    candidate_sets = [s for s in candidate_sets if s not in mandatory_sets]
    current_sets += mandatory_sets

    return covered, candidate_sets, current_sets


# Early break if candidate_sets cannot possibly cover remaining vertices
def is_solution_possible(universe, covered, candidate_sets):
    remaining = universe & ~covered
    coverage = 0
    for candidate in candidate_sets: coverage |= candidate
    return (coverage & remaining) == remaining


# Converts a set of values into a corresponding bitmask, where the value, v, of an element will mean the v-1th bit in the bitmask will be set to 1.
def set_to_bitmask(subset: set[int]) -> int:
    mask = 0
    for i in subset:
        mask |= 1 << (i-1)
    return mask


def bitmask_to_set(mask: int) -> set[int]:
    return {i + 1 for i in range(mask.bit_length()) if (mask >> i) & 1}


# Deprecated: faster implementation made in dynamic_prune_subsets() function
# Checks if subset2 is a subset of subset1
def is_subset(universe, covered, subset1, subset2) -> bool:
    return universe & ~covered & subset1 & (covered | ~subset2)


# If update is true, we will set the integer-1th bit of the bitmask to 1, else we will set it to false.
def update_bitmask(bitmask: int, integer: int, update: bool) -> int:
    return (bitmask | (1 << (integer - 1))) if update else (bitmask & ~(1 << (integer - 1)))