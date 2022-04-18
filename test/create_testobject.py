import networkx as nx

from src.helper import generate_list_of_n_random_nrs
from src.helper_network_structure import (
    get_degree_graph_with_separate_wta_circuits,
    plot_coordinated_graph,
    plot_unstructured_graph,
)
from src.networkx_to_snn import convert_networkx_graph_to_snn_with_one_neuron


def create_test_object(test_object, plot_input_graph=False, plot_snn_graph=False):
    ## Specify the expected neuron properties.
    # TODO: change this to make it a function of
    test_object.sample_selector_neuron = Selector_neuron()

    ## Specify the expected synaptic weights
    # TODO: Specify per synapse group. (except for the random synapses)
    test_object.incoming_selector_weight = -5

    ## Generate the graph on which the algorithm is ran.
    #  Generate a fully connected graph with n=4.
    test_object.G = nx.complete_graph(4)
    # test_object.G = create_manual_graph_with_4_nodes()
    if plot_input_graph:
        plot_unstructured_graph(test_object.G)

    ## Generate the maximum random ceiling
    # +2 to allow selecting a larger range of numbers than the number of
    # nodes in the graph.
    test_object.rand_ceil = len(test_object.G) + 2
    # Get the list of random numbers.
    test_object.rand_nrs = generate_list_of_n_random_nrs(
        test_object.G, max=test_object.rand_ceil, seed=42
    )
    print(f"before={test_object.rand_nrs}")
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
    # Add inhibition to rand_nrs to ensure the degree_receiver current u[1]
    # always starts negative. The a_in of the degree_receiver_x_y neuron is
    # : the incoming spike_once_x weights+rand_x neurons+selector_excitation
    # - There are at most n incoming spike signals.
    # - Each spike_once should have a weight of at least random_ceiling.
    # That is because the random value should map to 0<rand<1 with respect
    # to the difference of 1 spike_once more or less.
    # - The random_ceiling is specified.
    # - The excitatory neuron comes in at +1, a buffer of 1 yields+2.
    # Hence, the inhibition is computed as:
    test_object.inhibition = (
        len(test_object.G) * test_object.rand_ceil + test_object.rand_ceil + 2
    )
    test_object.rand_nrs = [x - test_object.inhibition for x in test_object.rand_nrs]
    print(
        f"After inhibition of:{test_object.inhibition}, rand_nrs={test_object.rand_nrs}"
    )

    ## Convert the fully connected graph into a networkx graph that
    # stores the snn properties.
    test_object.get_degree = get_degree_graph_with_separate_wta_circuits(
        test_object.G, test_object.rand_nrs
    )
    if plot_snn_graph:
        plot_coordinated_graph(test_object.get_degree)

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

    return test_object


class Selector_neuron:
    """Creates expected properties of the selector neuron."""

    def __init__(self):
        self.first_name = "selector_0"
        self.bias = 5
        self.du = 0
        self.dv = 1
        self.vth = 4
