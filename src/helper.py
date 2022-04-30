from datetime import datetime
import itertools
import os
import pickle
import random
import shutil
import networkx as nx
import traceback


from src.helper_snns import print_neuron_properties
from test.contains_neurons_of_type_x import get_n_neurons


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
    if some_set != set():
        return max(some_set)
    else:
        return 0


def get_y_position(G, node, neighbour, d):
    """Ensures the degree receiver nodes per node are alligned with
    continuous interval. for example for node 1, the positions 0,2,3 are
    mapped to positions: 0,1,2 by subtracting 1."""
    if neighbour > node:
        return float((node + (neighbour - 1) / len(G)) * 4 * d)
    else:
        return float((node + neighbour / len(G)) * 4 * d)


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
    # print(f"degree={degree}")
    # print(f"(wta_circuit={wta_circuit}")

    # Compute random value of relevant node.
    rand_val = rand_nrs[neighbour]
    # print(f"rand_val={rand_val}")

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
    # print(f"degree={degree}")
    # print(f"(wta_circuit={wta_circuit}")

    # Compute random value of relevant node.
    rand_val = rand_nrs[neighbour]
    # print(f"rand_val={rand_val}")

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
    elif neuron_name[:5] == "rand_":
        node_index = int(parts[1])
    elif neuron_name[:9] == "selector_":
        parts = neuron_name.split("_")
        node_index = int(parts[1])
    elif neuron_name[:8] == "counter_":
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


def print_neurons_properties(test_object, neuron_dict, neurons, t, descriptions=""):
    sorted_neurons = []
    # Sort by value.
    descriptions = ""
    spikes = []
    sorted_dict = dict(sorted(neuron_dict.items(), key=lambda item: item[1]))
    if descriptions == "":
        for neuron, neuron_name in sorted_dict.items():
            if neuron in neurons:
                sorted_neurons.append(neuron)
                descriptions = f"{descriptions} {neuron_name[-9:]}"
                monitor = test_object.monitor_dict[neuron]
                monitor_dict = monitor.get_data()
                inner_dict = list(monitor_dict.values())[0]
                spikelist = list(inner_dict.values())[0]
                current_spike = spikelist[t - 1]
                spikes.append(current_spike[0])

    print(descriptions[1:])
    print_neuron_properties(sorted_neurons, spikes)
    return sorted_neurons, spikes


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
    # Get max randomness of node:
    max_input = max(input_signals)

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
        return incoming_selector_weight * (t - t_degree_receiver_first_spike + 1)
    else:
        return 0


def get_a_in_for_spike_once(t):
    """The recurrent synapse with weight -2 should get a spike at time t=1,
    which means at the next timestep, t=2 it should receive an a_in of -2."""
    if t == 2:
        return -2
    else:
        return 0


def get_expected_amount_of_degree_receiver_neurons(
    G,
):
    expected_amount = 0
    for node in G.nodes:
        for neighbour in nx.all_neighbors(G, node):
            if node != neighbour:
                expected_amount = expected_amount + 1
    return expected_amount


def get_a_in_for_degree_receiver(
    G,
    found_winner,
    found_winner_at_t,
    node,
    previous_u,
    previous_v,
    rand_nrs,
    spike_once_weight,
    sample_degree_receiver_neuron,
    t,
    x,
    y,
):
    if x == 3 and y == 0 and t == 22:
        verbose = True
    else:
        verbose = False
    a_in = 0

    for node in G.nodes:
        for neighbour in nx.all_neighbors(G, node):
            if node != neighbour:
                for other_node in G.nodes:
                    if (
                        G.has_edge(neighbour, other_node)
                        and x == node
                        and y == neighbour
                        and t == 2
                    ):

                        a_in = a_in + spike_once_weight
                        # print(f'node={node},neighbour={neighbour},other_node={other_node},a_in={a_in}')

    for circuit in G.nodes:
        # Add synapse between random node and degree receiver nodes.
        for circuit_target in G.nodes:
            if circuit != circuit_target:
                # Check if there is an edge from neighbour_a to neighbour_b.
                if circuit in nx.all_neighbors(G, circuit_target):
                    # rand_to_degree_receiver
                    # f"rand_{circuit}", to: f"degree_receiver_{circuit_target}_{circuit}",
                    a_in = a_in + add_rand_to_degree_receiver(
                        circuit,
                        circuit_target,
                        rand_nrs[circuit],
                        t,
                        x,
                        y,
                        verbose,
                    )

        # Synapse from degree_selector to selector node.
        for neighbour_b in nx.all_neighbors(G, circuit):
            if circuit != neighbour_b:
                # f"degree_receiver_{circuit}_{neighbour_b}",to: f"selector_{circuit}",
                pass

    for node in G.nodes:
        for neighbour in nx.all_neighbors(G, node):
            # f"selector_{circuit}", f"degree_receiver_{circuit}_{neighbour_b}",
            a_in = a_in + get_a_in_from_selector_into_degree_receiver(
                found_winner,
                found_winner_at_t,
                t,
                neighbour,
                node,
                previous_u,
                previous_v,
                sample_degree_receiver_neuron,
                x,
                y,
                verbose,
            )
    return a_in


def add_spike_weight_to_degree_receiver(
    neighbour_a, neighbour_b, spike_once_weight, t, x, y, verbose=False
):
    """The spike_once neuron spikes at t=1, meaning the spike signal comes in
    at degree_receiver at t=2"""
    # Check if the degree_receiver_x_y that is being tested, is indeed the one
    # in the for loops for which a synapse exists.
    if x == neighbour_a:
        if y == neighbour_b:
            if t == 2:
                if verbose:
                    print(f"spike_once_weight={spike_once_weight}")
                return spike_once_weight
    return 0


def add_rand_to_degree_receiver(
    circuit, circuit_target, rand_weight, t, x, y, verbose=False
):
    """The rand neuron spikes at t=1, meaning the spike signal comes in
    at degree_receiver at t=2"""
    # Check if the degree_receiver_x_y that is being tested, is indeed the one
    # in the for loops for which a synapse exists.
    if x == circuit_target:
        if y == circuit:
            if t == 2:
                if verbose:
                    print(f"rand_weight={rand_weight}")
                return rand_weight
    return 0


def get_a_in_from_selector_into_degree_receiver(
    found_winner,
    found_winner_at_t,
    t,
    neighbour,
    node,
    previous_u,
    previous_v,
    sample_degree_receiver_neuron,
    x,
    y,
    verbose=False,
):
    """The selector neuron spikes at t=1, meaning the excitatory spike signal
    comes in at degree_receiver at t=2. The selector keeps firing until it is
    inhibited."""
    # Check if the degree_receiver_x_y that is being tested, is indeed the one
    # in the for loops for which a synapse exists.
    if x == node:
        if y == neighbour:
            # Spikes only start coming in from selector excitatory neuron at t>=2.
            if t >= 2:
                # Check if a winner degree_receiver_x_y is found for WTA circuit x.
                if not found_winner[node]:

                    # No winner has been found yet. Check if the previous current of the
                    # degree_receiver_x_y neuron was larger than its threshold.
                    if previous_u > sample_degree_receiver_neuron.vth:

                        # The winning degree_receiver_x_y neuron has fired in the previous round.
                        # The excitatory selector neuron still sends one last spike to the other
                        # degree_receiver_x_z neurons (and to x_y). After that no more spikes
                        # come in. Store that a winner is found
                        found_winner[node] = True
                        # Store the timestep, such that for the other degree_receivers_x_z,
                        # the inhibition of the selector neuron can be processed as a_in=0
                        # AFTER t=this time step.
                        found_winner_at_t[node] = t
                        # The selector neuron still sends 1 last spike to degree_receiver_x_y.
                        return 1
                    else:
                        # If degree_receiver_x_y neurons have not yet reached vth, they
                        # will always get an excitatory spike from selector neuron.
                        return 1
                elif found_winner_at_t[node] < t:
                    # The selector neuron still sends 1 last spike to all other degree_receiver_x_z
                    # neurons at time found_winner_at_t, after time found_winner_at_t, no more
                    # spikes come in, so a_in from the selector neuron will be 0 for degree_receiver_x_..
                    return 0
                else:
                    # A winner has not yet been found, or found after the first WTA circuit winner
                    # was found (after t=found_winner_at_t[node]), so the degree_receiver_x_,.. will
                    # still receive an input signal from the selector neuron.
                    return 1
    # This is not the neuron who's input spikes from selector_x are computed, so no input
    # signals will be returned.
    return 0


def sort_neurons(neurons, neuron_dict):
    sorted_neurons = []
    # Sort by value.
    sorted_dict = dict(sorted(neuron_dict.items(), key=lambda item: item[1]))
    for neuron, neuron_name in sorted_dict.items():
        if neuron in neurons:
            sorted_neurons.append(neuron)
    return sorted_neurons


def fill_dictionary(
    neuron_dict,
    neurons,
    previous_us,
    previous_vs,
    previous_selector=None,
    previous_has_spiked=None,
):
    sorted_neurons = sort_neurons(neurons, neuron_dict)
    for neuron in sorted_neurons:
        neuron_name = neuron_dict[neuron]
        previous_us[neuron_name] = 0
        previous_vs[neuron_name] = 0
        if not previous_selector is None:
            previous_selector[neuron_name] = 0
        if not previous_has_spiked is None:
            previous_has_spiked[neuron_name] = False

    if not previous_selector is None:
        if not previous_has_spiked is None:
            return previous_us, previous_vs, previous_selector, previous_has_spiked
        else:
            return previous_us, previous_vs, previous_selector
    else:
        if not previous_has_spiked is None:
            return previous_us, previous_vs, previous_has_spiked
        else:
            return previous_us, previous_vs
    raise Exception("Expected to have returned the correct set.")


def get_degree_reciever_neurons_per_wta_circuit(
    degree_receiver_neurons, neuron_dict, wta_circuit
):
    wta_degree_receiver_neurons = []
    for degree_receiver_neuron in degree_receiver_neurons:
        neuron_name = neuron_dict[degree_receiver_neuron]
        if neuron_name[:16] == "degree_receiver_":
            parts = neuron_name.split("_")
            # get wta circuit of neuron.
            node_index = int(parts[2])
            if wta_circuit == node_index:
                wta_degree_receiver_neurons.append(degree_receiver_neuron)
        else:
            raise Exception("Expected only degree_receiver neurons.")
    return wta_degree_receiver_neurons


def degree_receiver_x_y_is_connected_to_counter_z(
    counter_neuron, degree_receiver_neuron, G, neuron_dict
):
    z = get_wta_circuit_from_neuron_name(neuron_dict[counter_neuron])
    x, y = get_node_and_neighbour_from_degree(neuron_dict[degree_receiver_neuron])
    for circuit in G.nodes:
        for neighbour_b in nx.all_neighbors(G, circuit):
            if x == circuit and y == neighbour_b and neighbour_b == z:
                if circuit != neighbour_b:
                    return True
                else:
                    return False
    # raise Exception("Would have expected to find x and y.")
    return False


def get_x_position(m):
    """Ensures the degree receiver nodes per node are aligned with
    continuous interval. for example for node 1, the positions 0,2,3 are
    mapped to positions: 0,1,2 by subtracting 1."""
    if m == 0:
        return float(1.0)
    if m == 1:
        return float(1.75)


def delete_files_in_folder(folder):
    os.makedirs(folder, exist_ok=True)
    try:
        shutil.rmtree(folder)
    except Exception:
        print(traceback.format_exc())
    os.makedirs(folder, exist_ok=False)


def get_neurons(neuron_identifier, m, test_object):
    if neuron_identifier == "degree_receiver_":
        expected_n = get_expected_amount_of_degree_receiver_neurons(test_object.G)
        sample_neuron = test_object.sample_degree_receiver_neuron
    elif neuron_identifier == "selector_":
        expected_n = len(test_object.G)
        sample_neuron = test_object.sample_selector_neuron
    elif neuron_identifier == "counter_":
        expected_n = len(test_object.G)
        sample_neuron = test_object.sample_counter_neuron
    elif neuron_identifier == "spike_once_":
        expected_n = len(test_object.G)
        sample_neuron = test_object.sample_spike_once_neuron

    neurons = get_n_neurons(
        expected_n,
        test_object.neurons,
        test_object.neuron_dict,
        neuron_identifier,
        sample_neuron,
        m=m,
    )

    # Sort the neurons by default before returning them.
    if sorted:
        sorted_neurons = sort_neurons(neurons, test_object.neuron_dict)
    return sorted_neurons


def get_grouped_neurons(m, test_object):
    grouped_dict = {}
    for id in range(m + 1):
        grouped_dict[f"spike_once_x_{id}"] = get_neurons("spike_once_", id, test_object)
        grouped_dict[f"degree_receiver_neurons_x_y_{id}"] = get_neurons(
            "degree_receiver_", id, test_object
        )
        grouped_dict[f"selector_neurons_x_{id}"] = get_neurons(
            "selector_", id, test_object
        )
    grouped_dict[f"counter_neurons_x_{m}"] = get_neurons("counter_", m, test_object)

    return grouped_dict


def print_neuron_behaviour(
    test_object,
    grouped_neurons,
    t,
):
    spike_dict = {}
    print(f"t={t}")
    for name, neurons in grouped_neurons.items():
        sorted_neurons, spikes = print_neurons_properties(
            test_object,
            test_object.neuron_dict,
            neurons,
            t,
            descriptions=[],
        )
        spike_dict[name] = spikes
    return spike_dict


def write_results_to_file(m, G, retry, G_alipour, counter_neurons):
    # Append-adds at last
    file1 = open("results.txt", "a")  # append mode
    now = datetime.now()
    file1.write(now.strftime("%Y-%m-%d %H:%M:%S\n"))
    file1.write(f"m={m}\n")
    file1.write(f"len(G)={len(G)}\n")
    file1.write("edges\n")
    for edge in G.edges:
        file1.write(f"{str(edge)}\n")
    file1.write(f"retry={retry}\n")
    file1.write("G_alipour countermarks-SNN counter current\n")
    for node in G.nodes:
        file1.write(
            f'{G_alipour.nodes[node]["countermarks"]}-{counter_neurons[node].u.get()}\n'
        )
    file1.write("\n\n")
    file1.close()


def get_neuron_from_dict(neuron_dict, neurons, neuron_name):
    for neuron in neurons:
        if neuron_dict[neuron] == neuron_name:
            return neuron
    raise Exception("Did not find neuron:{neuron_name} in dict:{neuron_dict}")


def get_counter_neurons_from_dict(neuron_dict, expected_nr_of_neurons):
    counter_neurons = []
    neurons = list(neuron_dict.keys())
    neuron_names = list(neuron_dict.values())
    for neuron_name in neuron_names:
        if neuron_name[:8] == "counter_":
            counter_neurons.append(
                get_neuron_from_dict(neuron_dict, neurons, neuron_name)
            )

    if expected_nr_of_neurons != len(counter_neurons):
        raise Exception(
            f"Error, expected {expected_nr_of_neurons} neurons, yet found {len(counter_neurons)} neurons"
        )
    return counter_neurons


def print_time(status, previous_time, previous_millis):
    now = datetime.now()
    # durationTime = (now - previous_time).total_seconds()
    durationTime = now - previous_time
    import time

    now_millis = int(round(time.time() * 1000))

    duration_millis = now_millis - previous_millis
    print(f"{str(now.time())[:8]}, Duration:{duration_millis} [ms], status:{status}")
    return now, now_millis


def export_get_degree_graph(G, get_degree, iteration, m, seed, size):

    with open(
        f"pickles/test_object_seed{seed}_size{size}_m{m}_iter{iteration}.pkl", "wb"
    ) as fh:
        pickle.dump([G, get_degree, iteration, m, seed, size], fh)


def load_pickle_and_plot(iteration, m, seed, size):
    from src.helper_network_structure import plot_neuron_behaviour_over_time

    pickle_off = open(
        f"pickles/test_object_seed{seed}_size{size}_m{m}_iter{iteration}.pkl", "rb"
    )
    [G, get_degree, iteration, m, seed, size] = pickle.load(pickle_off)
    for t in range(4):
        plot_neuron_behaviour_over_time(get_degree, iteration, size, m, t, show=True)
