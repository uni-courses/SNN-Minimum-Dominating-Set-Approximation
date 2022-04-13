import itertools
import random


def list_of_all_combinations_of_set(some_set):
    all_combinations = set()
    list(some_set)
    # stuff = [1, 2, 3]
    for L in range(0, len(some_set) + 1):
        for subset in itertools.combinations(some_set, L):
            print(subset)
            all_combinations.add(subset)

    return all_combinations


from itertools import compress, product


def combinations(items):
    result = list(
        set(compress(items, mask)) for mask in product(*[[0, 1]] * len(items))
    )
    return sorted(result, key=get_some_sorting_key)


def get_some_sorting_key(some_set):
    print(f"some_set={some_set}")
    if some_set != set():
        return max(some_set)
    else:
        return 0


def get_y_position(G, node, neighbour):
    """Ensures the degree receiver nodes per node are alligned with
    continuous interval. for example for node 1, the positions 0,2,3 are
    mapped to positions: 0,1,2 by subtracting 1."""
    if neighbour > node:
        return float(node + (neighbour - 1) / len(G))
    else:
        return float(node + neighbour / len(G))


def generate_list_of_n_random_nrs(G, max=None, seed=None):
    """Generates list of numbers in range of 1 to (and including) len(G), or:
    Generates list of numbers in range of 1 to (and including) max, or:
    TODO: Verify list does not contain duplicates, throw error if it does.
    """
    if max is None:
        return list(range(1, len(G) + 1))
    elif max > len(G):
        large_list = list(range(1, max + 1))
        if not seed is None:
            random.seed(seed)
        print(random.sample(large_list, len(G)))
        return random.sample(large_list, len(G))
