from libc.stdint cimport uint32_t, uint64_t
from libc.stdlib cimport malloc, free
cimport cython
from Bitmask cimport Bitmask, MODE_32, MODE_64, MODE_PY

# --------------------------------------------------------
# File reading (Python-callable)
cpdef tuple read_set_cover_file(str filename):
    cdef int n, m, i
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f]

    n = int(lines[0])
    m = int(lines[1])

    cdef list subsets = []
    cdef set s
    for i in range(2, 2 + m):
        s = set(map(int, lines[i].split()))
        if s:
            subsets.append(s)

    subsets = [Bitmask.from_set(n, s) for s in subsets]
    subsets = prune_proper_subsets(subsets)

    cdef Bitmask universe = Bitmask.from_set(n, set(range(1, n + 1)))

    return universe, subsets


# --------------------------------------------------------
# Remove proper subsets (C-level)
cdef list prune_proper_subsets(list subsets):
    cdef int n = len(subsets)
    if n == 0:
        return []

    # Use Python list, not memoryview
    cdef list bm_array = [None] * n
    cdef int i, j, used = 0
    cdef Bitmask s1, s2
    cdef bint is_subset

    # copy Python list
    for i in range(n):
        bm_array[i] = subsets[i]

    cdef list pruned_array = [None] * n

    for i in range(n):
        s1 = bm_array[i]
        is_subset = False
        for j in range(n):
            if i == j:
                continue
            s2 = bm_array[j]
            # Check if s1 is a proper subset of s2
            if (s1 & ~s2) == Bitmask(s1.n) and s1 != s2:
                is_subset = True
                break
        if not is_subset:
            pruned_array[used] = s1
            used += 1

    return [pruned_array[i] for i in range(used)]

# --------------------------------------------------------
# Dynamic pruning using Bitmask
cdef list dynamic_prune_subsets(Bitmask universe, Bitmask covered, list subsets):
    cdef int n = len(subsets)
    if n == 0:
        return []

    cdef Bitmask uncovered = universe & ~covered
    cdef list pruned_array = [None] * n
    cdef list pruned_counts = [-1] * n  # -1 = empty slot
    cdef int i, j, used = 0
    cdef Bitmask s, u

    for s in subsets:
        u = s & uncovered
        if not u:
            continue
        # check if u already exists in pruned_array
        for j in range(used):
            if pruned_array[j] == u:
                if s.count() < pruned_array[j].count():
                    pruned_array[j] = s
                break
        else:
            pruned_array[used] = s
            used += 1

    return [pruned_array[i] for i in range(used)]

# --------------------------------------------------------
# Forced set selections
cdef tuple forced_set_selections(Bitmask universe, Bitmask covered, list candidate_sets, list current_sets):
    cdef int n = universe.n
    cdef Bitmask uncovered = universe & ~covered
    cdef list element_frequency = [0] * n
    cdef int i, j
    cdef Bitmask s, u, singleton
    cdef uint32_t val32
    cdef uint64_t val64

    # Count uncovered elements
    for s in candidate_sets:
        u = s & uncovered
        if s.mode == MODE_32:
            val32 = u.mask32
            for i in range(n):
                if val32 & (1 << i):
                    element_frequency[i] += 1
        elif s.mode == MODE_64:
            val64 = u.mask64
            for i in range(n):
                if val64 & (1 << i):
                    element_frequency[i] += 1
        else:
            valpy = u.maskpy
            for i in range(n):
                if valpy & (1 << i):
                    element_frequency[i] += 1

    # Collect mandatory sets
    cdef int candidate_count = len(candidate_sets)
    cdef list mandatory_sets = [None] * candidate_count
    cdef int mandatory_used = 0

    for i in range(n):
        if element_frequency[i] == 1:
            singleton = Bitmask.from_set(n, {i + 1})
            for s in candidate_sets:
                if s & singleton:
                    mandatory_sets[mandatory_used] = s
                    mandatory_used += 1
                    break

    # Dynamic prune mandatory sets
    cdef list mandatory = dynamic_prune_subsets(universe, covered, [mandatory_sets[i] for i in range(mandatory_used)])

    # Update covered
    for s in mandatory:
        covered |= s

    # Remove mandatory from candidate_sets
    cdef list new_candidates = []
    for s in candidate_sets:
        if s not in mandatory:
            new_candidates.append(s)

    current_sets += mandatory
    return covered, new_candidates, current_sets

# --------------------------------------------------------
# Early exit if solution impossible
cdef bint is_solution_possible(Bitmask universe, Bitmask covered, list candidate_sets):
    cdef Bitmask remaining = universe & ~covered
    cdef Bitmask coverage = Bitmask(universe.n)
    cdef Bitmask s
    for s in candidate_sets:
        coverage |= s
    return (coverage & remaining) == remaining
