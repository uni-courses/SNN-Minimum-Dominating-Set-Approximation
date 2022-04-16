import itertools
import random
import networkx as nx


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


def get_a_in_for_selector_neuron(G, incoming_selector_weight, node, rand_nrs, t):
    """If the minimum random value of a degree_receiver_x_y that is connected
    to selector_x is z (e.g. z=32), then degree_receiver_x_y will reach u(t)=0
    at t=z-2 (e.g. t=32-2=30). It is not quite clear why this is not at t=z.
    However, the degree_receiver_x_y neuron will then spike at t=z (so two
    timesteps later, e.g. t=32), because the vth=1, and the u(t) needs to be
    LARGER than vth, which requires a value of u(t)=2. Then there is a delay of
    1 for the spike to reach selector_x from degree_receiver_x_y. Once the spike
    arrives at t=z+1, it will immediatly result in an input a_in of -5 for the
    selector_x neuron."""
    print(f"node={node}")
    found_min_neighbour_rand = False
    # Start with the lowest random value found in the network.
    min_neighbour_rand = min(rand_nrs)
    # Identify the lowest random value in the neighbours (which are part of the network).
    # Therefore, the minimum randomness of the neighbours will always be lower than-,
    # or equal to the minimum random value in the network.
    for neighbour in nx.all_neighbors(G, node):
        if rand_nrs[neighbour] >= min_neighbour_rand:
            min_neighbour_rand = rand_nrs[neighbour]
            found_min_neighbour_rand = True
    if not found_min_neighbour_rand:
        raise Exception(
            "Error, did not find a random value in any neighbour of node:{node}."
        )

    positive_min_neighbour_rand = -1 * min_neighbour_rand
    print(f"positive_min_neighbour_rand={positive_min_neighbour_rand}")

    if t < positive_min_neighbour_rand + 1:
        return 0
    elif t == positive_min_neighbour_rand + 1:
        print(f"equals+1,t={t},return:{incoming_selector_weight}")
        return incoming_selector_weight
    elif t == positive_min_neighbour_rand + 2:
        print(f"equals+2,t={t},return:{incoming_selector_weight}*2")
        # Hardcoded because another degree_receiver neuron also starts firing
        #  at this point.That means the previous current -5 is still present
        # because du=0, then the first degree_receiver neuron fires again
        # because it is not yet inhibited, yielding another -5. Then the new
        # neuron also starts firing adding another -5 yielding -5*3.
        # This is because there is a a -32 and -34 as lowest random weights
        # using seed 42.
        return incoming_selector_weight * 2
    elif t == positive_min_neighbour_rand + 3:
        print(f"equals+3,t={t},return:{0}")
        return 0


def get_degree_receiver_neuron(neuron_dict, desired_neuron_name):
    for neuron, neuron_name in neuron_dict.items():
        if neuron_name == desired_neuron_name:
            return neuron
    raise Exception("Did not find neuron!.")
