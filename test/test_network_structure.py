import unittest
import networkx as nx
from src.helper_initalisation import get_weight_receiver_synapse_paths

from ..src.graph_properties import is_planar


class Test_weight_receiver_synapse_paths(unittest.TestCase):
    """
    Tests whether the connection starts and destinations for the synapses
    between the degree_senders and weight receiver neurons are created
    correctly.

    For each node A in graph G, for each neighbour B_A in neightbours_A, for each C_A in
    neightbours_A, A synapse is created from B_A to C_A with B_A!=CA.
    """

    # Initialize test object
    def __init__(self, *args, **kwargs):
        super(Test_weight_receiver_synapse_paths, self).__init__(
            *args, **kwargs
        )

    def test_weight_receiver_synapse_paths(self):
        """
        For a complete graph of size 3, should find:

        For Node 0:
            for 1_0:
                1_0->2_0
            for 2_0:
                2_0->1_0
        For Node 1:
            for 0_1:
                0_1->2_1
            for 2_1:
                2_1->1_1
        For Node 2:
            for 1_2:
                1_2->0_2
            for 2_2:
                2_2->1_2
        """
        G = nx.complete_graph(3)
        G = get_weight_receiver_synapse_paths(G)
        for node in G.nodes:
            for neighbour in nx.all_neighbors(G, node):
                # Check node 0
                if node["id"] == 0 and neighbour["id"] == 1:
                    self.assertEqual(neighbour["wr_paths"], set((1, 2)))
                if node["id"] == 0 and neighbour["id"] == 2:
                    self.assertEqual(neighbour["wr_paths"], set((2, 1)))
                    # TODO: Verify the order is correct.
                    # TODO: verify it fails if set contains more tuples.

                # Check node 1
                if node["id"] == 1 and neighbour["id"] == 0:
                    self.assertEqual(neighbour["wr_paths"], set((0, 2)))
                if node["id"] == 1 and neighbour["id"] == 2:
                    self.assertEqual(neighbour["wr_paths"], set((2, 0)))

                # Check node 2
                if node["id"] == 2 and neighbour["id"] == 0:
                    self.assertEqual(neighbour["wr_paths"], set((0, 1)))
                if node["id"] == 2 and neighbour["id"] == 1:
                    self.assertEqual(neighbour["wr_paths"], set((1, 0)))
