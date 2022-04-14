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
        return random.sample(large_list, len(G))


def get_a_in_with_random_neurons(G, neighbour, wta_circuit, rand_nrs, multiplier=1):
    """Computes the incoming spike value a_in of degree_receiver_x_y.
    Computation based on the spike_once neurons (x), and the random_neurons(y).
    The used names for x and y are: x=wta_circuit, y=neighbour.

    The multiplier can be used to multiply the spike_once inputs

    """
    # Compute the amount of neighbours the node that is represented by
    # wta_circuit.
    degree = G.degree(wta_circuit)
    print(f"degree={degree}")
    print(f"(wta_circuit={wta_circuit}")

    # Compute random value of relevant node.
    rand_val = rand_nrs[neighbour]
    print(f"rand_val={rand_val}")

    a_in = degree * multiplier + rand_val
    return a_in


def get_node_and_neighbour_from_degree(get_degree_neuron):
    parts = get_degree_neuron.split("_")
    node_index = int(parts[2])
    neighbour_index = int(parts[3])
    return node_index, neighbour_index


def add_neuron_to_dict(neighbour, neuron_dict, rhs_neuron):
    neuron_dict[rhs_neuron] = neighbour
    return neuron_dict


def get_degrree(d, neuron):
    neuronhash = "some_hash"
    return d[neuronhash]


def is_degree_receiver(neuron, neuron_dict):
    neuron_name = neuron_dict[neuron]
    if neuron_name[:16] == "degree_receiver_":
        return True
    else:
        print(f"neuron_name[:16]={neuron_name[:16]}")
        print(f"neuron_name={neuron_name}")
