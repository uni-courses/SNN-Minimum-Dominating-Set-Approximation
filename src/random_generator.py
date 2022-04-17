import random


def spaced_random_lists(length, delta=None, max=None, seed=None):
    """Generates a list of unique random numbers that have at least a
    difference of 2 between them. List has length of G. It can contain numbers
    between 0 and max+, excluding 0, including max."""
    # Generate minimum list
    if delta is None:
        minimal_list = list(range(1, length * 2 + 1, 2))
    else:
        minimal_list = list(range(1, 1 + delta * length, delta))
    if len(minimal_list) != length:
        raise Exception(f"Error{minimal_list} does not have lenght:{length}.")

    if max is None:
        return minimal_list
    elif max < length * 2 - (delta - 1):
        raise Exception(
            "The max does not allow for a large enough range to have at least a delta of 1 "
        )
    elif max > length:
        large_list = list(range(1, max + 1))
        if not seed is None:
            random.seed(seed)
        return random.sample(large_list, length)


def generate_evenly_spaced_list(lenght, start, delta):
    evenly_spaced_list = range(0, 10, 3)
    # for i in range(start,lenght*delta,delta):
    return evenly_spaced_list


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
        return random.sample(large_list, len(G))
