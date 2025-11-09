import time
import re
from Bitmask cimport Bitmask
from functions cimport read_set_cover_file, dynamic_prune_subsets, forced_set_selections

cdef bint TEST_MANDATORY_SELECTION = True

# -----------------------------
# Set cover recursive backtracking
def main():
    """Run the set cover problem on predefined filenames."""

    # -----------------------------
    # Set cover function
    def set_cover(Bitmask universe, list subsets):
        cdef int best_solution_len = len(subsets) + 1
        cdef object best_solution = None
        cdef dict cache = {}

        def set_cover_backtrack(covered, candidate_sets, current_sets):
            nonlocal best_solution_len, best_solution

            # Use tuple of mask values for hashable cache
            state = (covered, frozenset(candidate_sets), frozenset(current_sets))
            if state in cache:
                return
            cache[state] = True

            if covered == universe:
                if len(current_sets) < best_solution_len:
                    best_solution_len = len(current_sets)
                    best_solution = list(current_sets)
                return

            if len(current_sets) >= best_solution_len or not candidate_sets:
                return

            for s in candidate_sets:
                # Skip subsets that contribute nothing new
                if (s & (universe & ~covered)).count() == 0:
                    continue
                new_current_sets = current_sets + [s]
                new_covered = covered | s
                new_candidates = dynamic_prune_subsets(universe, new_covered, candidate_sets)
                set_cover_backtrack(new_covered, new_candidates, new_current_sets)

        cdef Bitmask covered_init = Bitmask(universe.n)  # empty mask
        if TEST_MANDATORY_SELECTION:
            covered_init, candidate_sets, current_sets = forced_set_selections(universe, covered_init, subsets, [])
            set_cover_backtrack(covered_init, candidate_sets, current_sets)
        else:
            set_cover_backtrack(covered_init, subsets, [])

        if best_solution is not None:
            return best_solution, best_solution_len
        return None, -1

    # -----------------------------
    # File runner
    def run_file(identifier, filenames):
        if isinstance(identifier, int):
            filename = filenames[identifier]
        else:
            filename = identifier

        universe, subsets = read_set_cover_file(f"Data/{filename}")
        start = time.time()
        solution, length = set_cover(universe, subsets)
        end = time.time()

        print(filename)
        if solution is None:
            print("No result found")
        else:
            print(f"Execution took {end - start:.6f} seconds")
            print(f"Cover Size: {length}")
            for mask in solution:
                print(mask.to_set())
        print("\n")

    # -----------------------------
    # Sort filenames by universe size and then subset amount
    def sort_filenames_by_numbers(filenames):
        def extract_numbers(name):
            numbers = re.findall(r'\d+', name)
            if len(numbers) < 2:
                raise ValueError(f"Filename '{name}' does not contain two integers.")
            return int(numbers[0]), int(numbers[1])
        return sorted(filenames, key=lambda name: extract_numbers(name))

    filenames = ['s-rg-8-10', 's-X-12-6', 's-k-20-30', 's-k-20-35', 's-k-30-50', 's-k-30-55',
                 's-rg-31-15', 's-k-35-65', 's-rg-40-20', 's-k-40-60', 's-k-40-80', 's-k-50-95',
                 's-k-50-100', 's-rg-63-25', 's-k-100-175', 's-rg-109-35', 's-rg-118-30',
                 's-k-150-225', 's-k-150-250', 's-rg-155-40', 's-rg-197-45', 's-k-200-300',
                 's-rg-245-50', 's-rg-413-75', 's-rg-733-100']

    run_file(6, filenames)
