from Bitmask cimport Bitmask

cpdef tuple read_set_cover_file(str filename)
cdef list prune_proper_subsets(list subsets)
cdef list dynamic_prune_subsets(Bitmask universe, Bitmask covered, list subsets)
cdef tuple forced_set_selections(Bitmask universe, Bitmask covered, list candidate_sets, list current_sets)
cdef bint is_solution_possible(Bitmask universe, Bitmask covered, list candidate_sets)
