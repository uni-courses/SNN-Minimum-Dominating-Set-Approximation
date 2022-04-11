import unittest
import networkx as nx
from src.helper_network_structure import get_degree_graph, plot_graph
from src.networkx_to_snn import (
    convert_networkx_graph_to_snn,
    convert_networkx_graph_to_snn_with_one_neuron,
)


class Test_networkx_to_snn(unittest.TestCase):
    """
    Tests whether the networks that are fed into networkx_to_snn are generating
    the correct snn networks.
    """

    # Initialize test object
    def __init__(self, *args, **kwargs):
        super(Test_networkx_to_snn, self).__init__(*args, **kwargs)

    def test_networkx_to_snn(self):
        """
        Tests for fully connected network of N=5
        """
        # Generate a fully connected graph with n=4.
        G = nx.complete_graph(4)
        # print(f"Incoming G")
        # plot_graph(G) # TODO: There can be only one function plot_graph.

        # Convert the fully connected graph into a networkx graph that
        # stores the snn properties to create an snn that computes the degree
        # in the number of spikes into the degree_receiver neurons.
        get_degree = get_degree_graph(G)

        # Convert the get_degree network into an actual snn network.
        # convert_networkx_graph_to_snn(
        #    get_degree, True, bias=0, du=0, dv=0, weight=1, vth=1
        # )
        (
            converted_nodes,
            lhs_neuron,
            neurons,
            lhs_node,
        ) = convert_networkx_graph_to_snn_with_one_neuron(
            get_degree, True, bias=0, du=0, dv=0, weight=1, vth=1
        )

        # TODO: Assert error is thrown for the case where some neuron is underspecified.

        
        

        # TODO: Assert the current u(t=2) of each
        # degree_receiver neuron has the same value as the number of the
        # degrees that the node has that is represented by the respective
        # degree_receiver node.

        # TODO: Simulate network for 5 more timesteps,

        # TODO: assert the current does not increase after the initial spikes


def test_spike_once_neurons_in_get_degree(get_degree, t):
    """Tests whether the neurons are all present.
    Verifies the neuron initial properties at t=0.
    Verifies the neuron properties over time.
    Assumes a spike occurs at t=1 in the spike_once neurons.
    """
    pass
    # TODO: Assert all spike_once neurons are present in the snn.

    # TODO: Assert the initial properties for the spike_once neurons are
    # correct at t=0.
    # TODO: Assert the current u(t) for the spike_once neurons is zero
    # at t=0.

    # TODO: Assert the current u(t) for the degree_receiver neurons is zero
    # at t=0.

    # TODO: Assert the spike_once_neurons spike at t=1

    # TODO: Assert the neuron properties for the spike_once neurons are
    # correct at t>0

def test_degree_receiver_neurons_in_get_degree(get_degree, t):
    """Tests whether the degree_receiver neurons are all present.
    Verifies the neuron initial properties at t=0.
    Verifies the neuron properties over time.
    Assumes a spike occurs at t=1 and comes in at t=2 in the degree_receiver
    neurons.
    """
    pass
    # TODO: Assert all degree_receiver neurons are present in the snn.

    # TODO: Assert the initial properties for the degree_receiver neurons are
    # correct at t=0.
    # TODO: Assert the current u(t) for the degree_receiver neurons is zero
    # at t=0.

    # TODO: Assert the current u(t) for the degree_receiver neurons is zero
    # at t=0.

    # TODO: Assert the degree_receiver neurons receive a spike at t=2

    # TODO: Assert the neuron properties for the degree_receiver neurons are
    # correct at t>2


def test_networkx_to_snn_weight_calculation(self):
    """
    TODO: create new test that verifies the incoming random spikes of
    neurons are added to the u(t) of the degree_receiver neurons.
    Verify that this also included the spike_once degree count in u(t).
    """
    pass

    # TODO: Write function that creates the random spiking neurons.
    # Specficy the range of their random values and use those as a
    # multiplication factor for the time window.
    # TODO: Assert the number of spikes is within the specified window.
    # TODO: Write function that creates the synapses between the
    # random spiking neurons and the degree_receiver neurons.
