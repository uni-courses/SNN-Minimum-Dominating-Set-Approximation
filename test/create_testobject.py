import copy
import networkx as nx
from src.create_planar_triangle_free_graph import create_manual_graph_with_4_nodes

from src.helper import (
    fill_dictionary,
    generate_list_of_n_random_nrs,
    get_expected_amount_of_degree_receiver_neurons,
    sort_neurons,
)
from src.helper_network_structure import (
    get_degree_graph_with_separate_wta_circuits,
    plot_coordinated_graph,
    plot_unstructured_graph,
)
from src.networkx_to_snn import convert_networkx_graph_to_snn_with_one_neuron
from test.contains_neurons_of_type_x import get_n_neurons


def create_test_object(
    G, iteration, plot_input_graph=False, plot_snn_graph=False, export=True
):
    test_object = Test_properties()
    ## Specify the expected neuron properties.
    # TODO: change this to make it a function of
    test_object.sample_selector_neuron = Selector_neuron()
    test_object.sample_spike_once_neuron = Spike_once_neuron()
    test_object.sample_rand_neuron = Rand_neuron()
    test_object.sample_degree_receiver_neuron = Degree_receiver()
    test_object.sample_counter_neuron = Counter_neuron()

    ## Specify the expected synaptic weights
    # TODO: Specify per synapse group. (except for the random synapses)
    test_object.incoming_selector_weight = -5

    ## Generate the graph on which the algorithm is ran.
    #  Generate a fully connected graph with n=4.
    test_object.G = G
    # test_object.G = nx.complete_graph(4)
    # test_object.G = create_manual_graph_with_4_nodes()
    try:
        if plot_input_graph or export:
            plot_unstructured_graph(test_object.G, iteration, len(G), plot_input_graph)
    except:
        pass

    ## Generate the maximum random ceiling
    # +2 to allow selecting a larger range of numbers than the number of
    # nodes in the graph.
    test_object.rand_ceil = len(test_object.G) + 2
    # Get the list of random numbers.
    test_object.rand_nrs = generate_list_of_n_random_nrs(
        test_object.G, max=test_object.rand_ceil, seed=42
    )
    print(f"before delta={test_object.rand_nrs}")

    # Make the random numbers differ with at least delta>=2. This is to
    # prevent multiple degree_receiver_x_y neurons (that differ less than
    # delta) in a single WTA circuit to spike before they are inhibited by
    # the first winner. This inhibition goes via the selector neuron and
    # has a delay of 2. So a winner should have a difference of at least 2.
    test_object.delta = 2
    # Spread the random numbers with delta to ensure 1 winner in WTA
    # circuit.
    test_object.rand_nrs = [x * test_object.delta for x in test_object.rand_nrs]
    print(f"after_delta={test_object.rand_nrs}")
    print(f"test_object.rand_ceil={test_object.rand_ceil}")
    # Add inhibition to rand_nrs to ensure the degree_receiver current u[1]
    # always starts negative. The a_in of the degree_receiver_x_y neuron is
    # : the incoming spike_once_x weights+rand_x neurons+selector_excitation
    # - There are at most n incoming spike signals.
    # - Each spike_once should have a weight of at least random_ceiling+1.
    # That is because the random value should map to 0<rand<1 with respect
    # to the difference of 1 spike_once more or less.
    # - The random_ceiling is specified.
    # - The excitatory neuron comes in at +1, a buffer of 1 yields+2.
    # Hence, the inhibition is computed as:
    test_object.inhibition = (
        len(test_object.G) * (test_object.rand_ceil * test_object.delta + 1)
        + (test_object.rand_ceil) * test_object.delta
        + 1
    )
    test_object.rand_nrs = [x - test_object.inhibition for x in test_object.rand_nrs]
    print(
        f"After inhibition of:{test_object.inhibition}, rand_nrs={test_object.rand_nrs}"
    )
    ## Convert the fully connected graph into a networkx graph that
    # stores the snn properties.
    # rand_ceil+1 because the maximum random number is rand_ceil which should map
    # to range 0<rand<1 when divided by the synaptic weight of spike_once neurons.
    # (and not to range 0<rand<=1 as it would without the +1)
    test_object.get_degree = get_degree_graph_with_separate_wta_circuits(
        test_object.G,
        test_object.rand_nrs,
        test_object.rand_ceil * test_object.delta + 1,
    )

    try:
        if plot_snn_graph or export:
            plot_coordinated_graph(
                test_object.get_degree, iteration, len(G), plot_snn_graph
            )
    except:
        pass
    # raise Exception("stop")

    ## Convert the snn networkx graph into a Loihi implementation.
    (
        test_object.converted_nodes,
        test_object.lhs_neuron,
        test_object.neurons,
        test_object.lhs_node,
        test_object.neuron_dict,
    ) = convert_networkx_graph_to_snn_with_one_neuron(
        test_object.get_degree, True, bias=0, du=0, dv=0, weight=1, vth=1
    )

    # Specify boolean array that stores whether a winner has been found in WTA
    # circuits.
    test_object.found_winner = [False] * len(test_object.G)
    # degree_receiver_x_y neurons will get first input spike from selector
    # neuron at t=2
    test_object.found_winner_at_t = [2] * len(test_object.G)

    return test_object


def get_degree_receiver_neurons(test_object, sorted=True):
    degree_receiver_neurons = get_n_neurons(
        get_expected_amount_of_degree_receiver_neurons(test_object.G),
        test_object.neurons,
        test_object.neuron_dict,
        "degree_receiver_",
        test_object.sample_degree_receiver_neuron,
    )

    # Sort the neurons by default before returning them.
    if sorted:
        sorted_degree_receiver_neurons = sort_neurons(
            degree_receiver_neurons, test_object.neuron_dict
        )

    # Get the first neuron in the SNN to start the simulation
    starter_neuron = degree_receiver_neurons[0]
    return test_object, sorted_degree_receiver_neurons, starter_neuron


def get_selector_neurons(test_object, sorted=True):
    # TODO: create stripped down function that just gets the selector neurons.
    selector_neurons = get_n_neurons(
        len(test_object.G),
        test_object.neurons,
        test_object.neuron_dict,
        "selector_",
        test_object.sample_selector_neuron,
    )

    # Sort the neurons by default before returning them.
    if sorted:
        sorted_selector_neurons = sort_neurons(
            selector_neurons, test_object.neuron_dict
        )

    # Get the first neuron in the SNN to start the simulation
    starter_neuron = selector_neurons[0]
    return test_object, sorted_selector_neurons, starter_neuron


def get_counter_neurons(test_object, sorted=True):
    # TODO: create stripped down function that just gets the counter neurons.
    counter_neurons = get_n_neurons(
        len(test_object.G),
        test_object.neurons,
        test_object.neuron_dict,
        "counter_",
        test_object.sample_counter_neuron,
    )

    # Sort the neurons by default before returning them.
    if sorted:
        sorted_counter_neurons = sort_neurons(counter_neurons, test_object.neuron_dict)

    # Get the first neuron in the SNN to start the simulation
    starter_neuron = counter_neurons[0]
    return test_object, sorted_counter_neurons, starter_neuron


def get_degree_receiver_previous_property_dicts(test_object, degree_receiver_neurons):
    degree_receiver_previous_us = {}
    degree_receiver_previous_vs = {}
    degree_receiver_previous_has_spiked = {}
    (
        degree_receiver_previous_us,
        degree_receiver_previous_vs,
        degree_receiver_previous_has_spiked,
    ) = fill_dictionary(
        test_object.neuron_dict,
        degree_receiver_neurons,
        degree_receiver_previous_us,
        degree_receiver_previous_vs,
        previous_has_spiked=degree_receiver_previous_has_spiked,
    )
    # degree_receiver_has_spiked = copy.deepcopy(degree_receiver_previous_us)
    # degree_receiver_has_spiked =degree_receiver_has_spiked.fromkeys(degree_receiver_has_spiked, False)
    # Print:
    return (
        degree_receiver_previous_has_spiked,
        degree_receiver_previous_us,
        degree_receiver_previous_vs,
    )


def get_selector_previous_property_dicts(test_object, selector_neurons):
    selector_previous_a_in = {}
    selector_previous_us = {}
    selector_previous_vs = {}
    (
        selector_previous_a_in,
        selector_previous_us,
        selector_previous_vs,
    ) = fill_dictionary(
        test_object.neuron_dict,
        selector_neurons,
        selector_previous_us,
        selector_previous_vs,
        selector_previous_a_in,
    )
    return selector_previous_a_in, selector_previous_us, selector_previous_vs


def get_counter_previous_property_dicts(test_object, counter_neurons):
    counter_previous_a_in = {}
    counter_previous_us = {}
    counter_previous_vs = {}
    (
        counter_previous_a_in,
        counter_previous_us,
        counter_previous_vs,
    ) = fill_dictionary(
        test_object.neuron_dict,
        counter_neurons,
        counter_previous_us,
        counter_previous_vs,
        counter_previous_a_in,
    )
    return counter_previous_a_in, counter_previous_us, counter_previous_vs


class Selector_neuron:
    """Creates expected properties of the selector neuron."""

    def __init__(self):
        self.first_name = "selector_0"
        self.bias = 5
        self.du = 0
        self.dv = 1
        self.vth = 4


class Spike_once_neuron:
    """Creates expected properties of the spike_once neuron."""

    def __init__(self):
        self.first_name = "spike_once_0"
        self.bias = 2
        self.du = 0
        self.dv = 0
        self.vth = 1


class Rand_neuron:
    """Creates expected properties of the rand neuron."""

    def __init__(self):
        self.first_name = "rand_0"
        self.bias = 2
        self.du = 0
        self.dv = 0
        self.vth = 1


class Counter_neuron:
    """Creates expected properties of the counter neuron."""

    def __init__(self):
        self.first_name = "counter_0"
        self.bias = 0
        self.du = 0
        self.dv = 1
        self.vth = 0


class Degree_receiver:
    """Creates expected properties of the spike_once neuron."""

    def __init__(self):
        self.first_name = "spike_once_0"
        self.bias = 0
        self.du = 0
        self.dv = 1
        self.vth = 1


class Test_properties:
    """Contains test parameters"""

    def __init__(self):
        pass
