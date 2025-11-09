import time
import re
import pdb

from backup_functions import read_set_cover_file, dynamic_prune_subsets, bitmask_to_set, forced_set_selections


# universe is a bitmask of the universe
# covered is a bitmask representing which elements we already have included in our cover
# candidate_sets represents the remaining subsets that could be added to the cover after pruning
def set_cover(universe, subsets) -> tuple[None | list[int], int]:
    best_solution_len = len(subsets) + 1
    best_solution = None
    cache = {}


    def set_cover_backtrack(covered: int, candidate_sets: list[int], current_sets: list[int]):
        # print(bitmask_to_set(covered))
        nonlocal best_solution_len, best_solution
        # pdb.set_trace()

        state = (covered, frozenset(candidate_sets), frozenset(current_sets))
        if state in cache: return
        cache[state] = True

        if covered == universe:
            # for s in current_sets: print(bitmask_to_set(s))
            # print("\n\n")
            if len(current_sets) < best_solution_len:
                best_solution_len = len(current_sets)
                best_solution = current_sets
            return
        if len(current_sets) >= best_solution_len:
            return
        if not candidate_sets:
            return
#--------------------------------------------------------
        TEST_RECURSIVE_MANDATORY_SELECTION = False
        if TEST_RECURSIVE_MANDATORY_SELECTION:
            if len(candidate_sets) > 0.8 * universe.bit_length():
                forced_covered, forced_candidate_sets, forced_current_sets = forced_set_selections(universe, covered, candidate_sets, current_sets)
                if forced_covered != covered:
                    set_cover_backtrack(forced_covered, forced_candidate_sets, forced_current_sets)
                else:
                    for s in candidate_sets:
                        if universe & ~covered & s == 0: continue
                        new_current_sets = current_sets + [s]
                        new_covered = covered | s
                        new_candidates = dynamic_prune_subsets(universe, new_covered, candidate_sets)
                        set_cover_backtrack(new_covered, new_candidates, new_current_sets)
            else:
                for s in candidate_sets:
                    if universe & ~covered & s == 0: continue
                    new_current_sets = current_sets + [s]
                    new_covered = covered | s
                    new_candidates = dynamic_prune_subsets(universe, new_covered, candidate_sets)
                    set_cover_backtrack(new_covered, new_candidates, new_current_sets)
        else:
            for s in candidate_sets:
                if universe & ~covered & s == 0: continue
                new_current_sets = current_sets + [s]
                new_covered = covered | s
                new_candidates = dynamic_prune_subsets(universe, new_covered, candidate_sets)
                set_cover_backtrack(new_covered, new_candidates, new_current_sets)
#--------------------------------------------------------
    TEST_MANDATORY_SELECTION = True
    if TEST_MANDATORY_SELECTION:
        # start = time.time()
        covered, candidate_sets, current_sets = forced_set_selections(universe,0, subsets, [])
        # end = time.time()
        # elapsed = end - start
        # print(f"Forced selection time: {elapsed:.6f} seconds")
        set_cover_backtrack(covered, candidate_sets, current_sets)
    else:
        set_cover_backtrack(0, subsets, [])

    if best_solution is not None:
        return best_solution, best_solution_len
    return None, -1


def run_file(identifier, filenames):
    filename = None
    if type(identifier) is int:
        filename = filenames[identifier]
    else:
        filename = identifier

    universe, subsets = read_set_cover_file(f"Data/{filename}")
    start = time.time()
    subsets, length = set_cover(universe, subsets)
    end = time.time()
    difference = end - start
    print(filename)
    if subsets is None and length == -1:
        print("No result found")
    else:
        print(f"Execution took {difference:.6f} seconds")
        print(f"Cover Size: {length}")
        for mask in subsets:
            print(bitmask_to_set(mask))
    print("\n\n")


def sort_filenames_by_numbers(filenames: list[str]) -> list[str]:
    def extract_numbers(name: str):
        # Find all integers in the string
        numbers = re.findall(r'\d+', name)
        if len(numbers) < 2:
            raise ValueError(f"Filename '{name}' does not contain two integers.")
        # Convert to ints for numeric comparison
        return int(numbers[0]), int(numbers[1])

    # Sort by first then second integer
    return sorted(filenames, key=lambda name: extract_numbers(name))


if __name__ == '__main__':
    filenames = ['s-rg-8-10', 's-X-12-6', 's-k-20-30', 's-k-20-35', 's-k-30-50', 's-k-30-55', 's-rg-31-15', 's-k-35-65', 's-rg-40-20', 's-k-40-60', 's-k-40-80', 's-k-50-95', 's-k-50-100', 's-rg-63-25', 's-k-100-175', 's-rg-109-35', 's-rg-118-30', 's-k-150-225', 's-k-150-250', 's-rg-155-40', 's-rg-197-45', 's-k-200-300', 's-rg-245-50', 's-rg-413-75', 's-rg-733-100']
    # filenames = sort_filenames_by_numbers(filenames)
    # print(filenames)
    filenames_enumeration = list(enumerate(filenames))
    print(filenames_enumeration)
    run_file(13, filenames)