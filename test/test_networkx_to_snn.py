import unittest
import networkx as nx
from src.helper_network_structure import get_degree_graph, plot_graph
from src.networkx_to_snn import convert_networkx_graph_to_snn



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
        print(f"Incoming G")
        plot_graph(G) # TODO: There can be only one function plot_graph.

        # Convert the fully connected graph into a networkx graph that 
        # stores the snn properties to create an snn that computes the degree
        # in the number of spikes into the degree_receiver neurons.
        get_degree = get_degree_graph(G)
        
        # Convert the get_degree network into an actual snn network.
        convert_networkx_graph_to_snn(get_degree,True,bias=0,du=0, dv=0, weight=1,vth=1)

        # Assert error is thrown for the case where some neuron is underspecified.