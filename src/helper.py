import itertools
import random
import networkx as nx

from src.helper_snns import print_neuron_properties


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


def get_a_in_with_random_neurons_and_excitation(
    G, neighbour, rand_nrs, t, wta_circuit, multiplier=1
):
    """Computes the incoming spike value a_in of degree_receiver_x_y.
    Computation based on the spike_once neurons (x), the random_neurons(y) and
    the excitatory neuron.
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

    a_in = degree * multiplier + rand_val + t - 1
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
        return False


def is_selector_neuron_dict(neuron, neuron_dict):
    neuron_name = neuron_dict[neuron]
    if neuron_name[:9] == "selector_":
        return True
    else:
        print(f"neuron_name[:9]={neuron_name[:9]}")
        print(f"neuron_name={neuron_name}")
        return False


def get_expected_voltage_of_first_spike(rand_nrs, t, a_in):
    if a_in > 1:
        return 0
    else:
        return a_in


def get_node_from_selector_neuron_name(selector_neuron_name):
    if selector_neuron_name[:9] == "selector_":
        parts = selector_neuron_name.split("_")
        node_index = int(parts[1])
        return node_index

    else:
        raise Exception(
            "Error tried parsing neuron as selector neuron even though it is not."
        )


def get_a_in_for_selector_neuron_retry(
    G, delta, incoming_selector_weight, node, rand_nrs, t
):
    """Gets the a_in spikes for the selector neuron."""
    if delta < 2:
        raise Exception(
            "Error, this method does not yield correct results for delta<2."
        )
    neighbours = []
    random_values = []
    degrees = []
    input_signals = []
    for neighbour in nx.all_neighbors(G, node):
        neighbours.append(neighbour)
    # Compute number of neighbours in node.
    for index, neighbour in enumerate(list(nx.all_neighbors(G, node))):
        random_values.append(rand_nrs[neighbour])
        degrees.append(len(list(nx.all_neighbors(G, neighbour))))
        # +1 for the excitatory selector neuron.
        input_signals.append(random_values[index] + degrees[index] + 1)
    print(f"node={node}")
    # Get max randomness of node:
    max_input = max(input_signals)

    if node == 1:
        print(f"random_values={random_values}")
        print(f"degrees={degrees}")
        print(f"input_signals={input_signals}")
        print(f"incoming_selector_weight={incoming_selector_weight}")
        print(f"max_input={max_input}")

    # Compute time at which first neuron degree_receiver spikes
    # +5: +2 Because at t=1 the currents at degree_receiver are still 0.
    # +2 delay because the v[t] should EXCEED, (not equal) vth=1
    # -1 because all neurons start at their degree-randomness+1 for the
    #  excitatory selector neuron.
    # +1 delay from degree_receiver_x_y to selector_x +
    # +1 delay from selector_x to degree_receiver_x_y.
    # So 2+2-1+1+1=5
    #
    t_degree_receiver_first_spike = -1 * max_input + 5
    if t >= t_degree_receiver_first_spike:

        print(
            f"t={t}, returning:a_in={incoming_selector_weight}*{t-t_degree_receiver_first_spike+1}"
        )
        return incoming_selector_weight * (t - t_degree_receiver_first_spike + 1)
    else:
        return 0


def get_degree_receiver_neuron(neuron_dict, desired_neuron_name):
    for neuron, neuron_name in neuron_dict.items():
        if neuron_name == desired_neuron_name:
            return neuron
    raise Exception(f"Did not find neuron:{desired_neuron_name}!.")


def print_degree_neurons(G, neuron_dict, node, t, extra_neuron=None):
    if not extra_neuron is None:
        degree_neuron_names = [neuron_dict[extra_neuron]]
    else:
        degree_neuron_names = []
    degree_receiver_neurons = [extra_neuron]
    for neighbour in nx.all_neighbors(G, node):
        degree_neuron_name = f"degree_receiver_{node}_{neighbour}"
        degree_neuron_names.append(degree_neuron_name)

        # Get neurons that are to be printed
        degree_receiver_neurons.append(
            get_degree_receiver_neuron(neuron_dict, degree_neuron_name)
        )
    # Print which neuron properties are being printed
    print(
        f"t={t},Properties of:{neuron_dict[extra_neuron]}," + f"{degree_neuron_names},"
    )
    # Print neuron properties.
    print_neuron_properties(degree_receiver_neurons)
