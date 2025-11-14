import time
import re
import pdb

from functions import read_set_cover_file, dynamic_prune_subsets, bitmask_to_set, forced_set_selections, \
    is_solution_possible


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
        # if not is_solution_possible(universe, covered, candidate_sets):
        #     return
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
    if type(identifier) is int:
        filename = filenames[identifier]
    else:
        filename = identifier

    universe, subsets = read_set_cover_file(f"../Data/{filename}")
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
    filenames = ['s-rg-8-10', 's-X-12-6', 's-k-20-30', 's-k-20-35', 's-k-30-50', 's-k-30-55', 's-rg-31-15', 's-rg-40-20', 's-k-40-60']
    # filenames = sort_filenames_by_numbers(filenames)
    # print(filenames)
    # filenames_enumeration = list(enumerate(filenames))
    # print(filenames_enumeration)
    for file in filenames:
        run_file(file, filenames)