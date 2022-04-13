import itertools


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
    if neighbour > node:
        return float(node + (neighbour - 1) / len(G))
    else:
        return float(node + neighbour / len(G))
