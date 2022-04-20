import collections
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
        return False


def is_selector_neuron_dict(neuron, neuron_dict):
    neuron_name = neuron_dict[neuron]
    if neuron_name[:9] == "selector_":
        return True
    else:
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


def get_wta_circuit_from_neuron_name(neuron_name):
    parts = neuron_name.split("_")
    if neuron_name[:11] == "spike_once_":
        node_index = int(parts[2])
    if neuron_name[:5] == "rand_":
        node_index = int(parts[1])
    elif neuron_name[:9] == "selector_":
        parts = neuron_name.split("_")
        node_index = int(parts[1])
    elif neuron_name[:16] == "degree_receiver_":
        parts = neuron_name.split("_")
        node_index = int(parts[2])
    else:
        print(f"neuron_name={neuron_name}")
        raise Exception(
            "Error tried parsing neuron as spike_once or selector neuron even though it is not."
        )
    return node_index


def get_y_from_degree_receiver_x_y(neuron_name):
    if neuron_name[:16] == "degree_receiver_":
        parts = neuron_name.split("_")
        y = int(parts[3])
    else:
        print(f"neuron_name[:16]={neuron_name[:16]}")
        raise Exception(
            "Error tried parsing neuron as spike_once or selector neuron even though it is not."
        )
    return y


def get_degree_receiver_neuron(neuron_dict, desired_neuron_name):
    for neuron, neuron_name in neuron_dict.items():
        if neuron_name == desired_neuron_name:
            return neuron
    raise Exception(f"Did not find neuron:{desired_neuron_name}!.")


def print_neurons_properties(neuron_dict, neurons, t, descriptions=""):
    sorted_neurons = []
    # Sort by value.
    descriptions = ""
    sorted_dict = dict(sorted(neuron_dict.items(), key=lambda item: item[1]))
    if descriptions == "":
        for neuron, neuron_name in sorted_dict.items():
            if neuron in neurons:
                sorted_neurons.append(neuron)
                descriptions = f"{descriptions} {neuron_name[-9:]}"

    print(f"t={t}")
    print(descriptions[1:])
    print_neuron_properties(sorted_neurons)


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
        print(f"index={index},neighbour={neighbour}")
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


def get_a_in_for_spike_once(t):
    """The recurrent synapse with weight -2 should get a spike at time t=1,
    which means at the next timestep, t=2 it should receive an a_in of -2."""
    if t == 2:
        print(f"t={t},return-2")
        return -2
    else:
        return 0


def get_expected_amount_of_degree_receiver_neurons(G):
    expected_amount = 0
    for node in G.nodes:
        for neighbour in nx.all_neighbors(G, node):
            if node != neighbour:
                expected_amount = expected_amount + 1
    return expected_amount


def get_a_in_for_degree_receiver(G, node, rand_nrs, t, x, y):
    a_in = 0
    for circuit in G.nodes:
        # For each neighbour of node, named degree_receiver:
        for neighbour_a in G.nodes:
            if neighbour_a in nx.all_neighbors(G, circuit) or neighbour_a == circuit:
                for neighbour_b in nx.all_neighbors(G, circuit):
                    if circuit != neighbour_b and neighbour_a != neighbour_b:

                        # Check if there is an edge from neighbour_a to neighbour_b.
                        if neighbour_a in nx.all_neighbors(G, neighbour_b):
                            # Spike_once to degree_receiver
                            # f"spike_once_{circuit}", to: f"degree_receiver_{neighbour_a}_{neighbour_b}",
                            a_in = a_in + add_spike_weight_to_degree_receiver(
                                neighbour_a, neighbour_b, 1, t, x, y
                            )

        # Add synapse between random node and degree receiver nodes.
        for circuit_target in G.nodes:
            if circuit != circuit_target:
                # Check if there is an edge from neighbour_a to neighbour_b.
                if circuit in nx.all_neighbors(G, circuit_target):
                    # rand_to_degree_receiver
                    # f"rand_{circuit}", to: f"degree_receiver_{circuit_target}_{circuit}",
                    a_in = a_in + add_rand_to_degree_receiver(
                        circuit, circuit_target, rand_nrs[circuit], t, x, y
                    )

        # Synapse from degree_selector to selector node.
        for neighbour_b in nx.all_neighbors(G, circuit):
            if circuit != neighbour_b:
                # f"degree_receiver_{circuit}_{neighbour_b}",to: f"selector_{circuit}",
                pass

    for node in G.nodes:
        for neighbour in nx.all_neighbors(G, node):
            # f"selector_{circuit}", f"degree_receiver_{circuit}_{neighbour_b}",
            a_in = a_in + add_selector_to_degree_receiver(t)

    return a_in


def add_spike_weight_to_degree_receiver(
    neighbour_a, neighbour_b, spike_once_weight, t, x, y
):
    """The spike_once neuron spikes at t=1, meaning the spike signal comes in
    at degree_receiver at t=2"""
    # Check if the degree_receiver_x_y that is being tested, is indeed the one
    # in the for loops for which a synapse exists.
    if x == neighbour_a:
        if y == neighbour_b:
            if t == 2:
                return spike_once_weight
    return 0


def add_rand_to_degree_receiver(circuit, circuit_target, rand_weight, t, x, y):
    """The rand neuron spikes at t=1, meaning the spike signal comes in
    at degree_receiver at t=2"""
    # Check if the degree_receiver_x_y that is being tested, is indeed the one
    # in the for loops for which a synapse exists.
    if x == circuit_target:
        if y == circuit:
            if t == 2:
                return rand_weight
    return 0


def add_selector_to_degree_receiver(t):
    """The selector neuron spikes at t=1, meaning the excitatory spike signal
    comes in at degree_receiver at t=2. The selector keeps firing until it is
    inhibited."""
    # Check if the degree_receiver_x_y that is being tested, is indeed the one
    # in the for loops for which a synapse exists.
    if t >= 2:
        # TODO: compute when to stop excitation.
        return 1
    else:
        return 0


def sort_neurons(neurons, neuron_dict):
    sorted_neurons = []
    # Sort by value.
    sorted_dict = dict(sorted(neuron_dict.items(), key=lambda item: item[1]))
    for neuron, neuron_name in sorted_dict.items():
        if neuron in neurons:
            sorted_neurons.append(neuron)
    return sorted_neurons
