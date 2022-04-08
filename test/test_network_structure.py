import unittest
import networkx as nx
from src.helper_network_structure import get_weight_receiver_synapse_paths


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
        super(Test_weight_receiver_synapse_paths, self).__init__(*args, **kwargs)

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
            if node == 0:
                # Assert complete set.
                self.assertEqual(set([(1, 2), (2, 1)]), G.nodes[node]["wr_paths"])
            if node == 1:
                # Assert complete set.
                self.assertEqual(set([(0, 2), (2, 0)]), G.nodes[node]["wr_paths"])
            if node == 2:
                # Assert complete set.
                self.assertEqual(set([(1, 0), (0, 1)]), G.nodes[node]["wr_paths"])

    def test_weight_receiver_synapse_paths_fully_connected_4_nodes(self):
        """
        For a complete graph of size 4, should find:
        """
        G = nx.complete_graph(4)
        G = get_weight_receiver_synapse_paths(G)
        expected_set_node_0 = set([(1, 2), (1, 3), (2, 1), (2, 3), (3, 1), (3, 2)])
        expected_set_node_1 = set([(0, 2), (0, 3), (2, 0), (2, 3), (3, 0), (3, 2)])
        expected_set_node_2 = set([(0, 1), (0, 3), (1, 0), (1, 3), (3, 0), (3, 1)])
        expected_set_node_3 = set([(0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1)])
        for node in G.nodes:
            if node == 0:
                # Assert complete set.
                self.assertEqual(
                    expected_set_node_0,
                    G.nodes[node]["wr_paths"],
                )
            if node == 1:
                # Assert complete set.
                self.assertEqual(
                    expected_set_node_1,
                    G.nodes[node]["wr_paths"],
                )
            if node == 2:
                # Assert complete set.
                self.assertEqual(
                    expected_set_node_2,
                    G.nodes[node]["wr_paths"],
                )

            if node == 3:
                # Assert complete set.
                self.assertEqual(
                    expected_set_node_3,
                    G.nodes[node]["wr_paths"],
                )

    def test_random_edge_dropout_4_nodes(self):
        """
        TODO: Write a test that gets all possible edge sets in the graph, and
        then drops out each edge set w.r.t. the fully connected graph. Only
        proceed with the connected graphs. Then verify that those dropped
        edges do not occur in the network proposed by:
        get_weight_receiver_synapse_paths().
        """

        expected_set_node_0 = set([(1, 2), (1, 3), (2, 1), (2, 3), (3, 1), (3, 2)])
        expected_set_node_1 = set([(0, 2), (0, 3), (2, 0), (2, 3), (3, 0), (3, 2)])
        expected_set_node_2 = set([(0, 1), (0, 3), (1, 0), (1, 3), (3, 0), (3, 1)])
        expected_set_node_3 = set([(0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1)])

        G = nx.complete_graph(4)
        # TODO:  For all possible edge sets:
        for edge_set in None:
            # Create fully connected graph
            G = nx.complete_graph(4)

            # TODO: remove edge set from fully connected graph

            # TODO: if graph is still a connected graph:

            # TODO: Remove edge set that is removed from graph from expected results.

            # Get synapse paths
            G = get_weight_receiver_synapse_paths(G)

            # TODO: Verify synapse paths are as expected.

            for node in G.nodes:
                if node == 0:
                    # Assert complete set.
                    self.assertEqual(
                        expected_set_node_0,
                        G.nodes[node]["wr_paths"],
                    )
                if node == 1:
                    # Assert complete set.
                    self.assertEqual(
                        expected_set_node_1,
                        G.nodes[node]["wr_paths"],
                    )
                if node == 2:
                    # Assert complete set.
                    self.assertEqual(
                        expected_set_node_2,
                        G.nodes[node]["wr_paths"],
                    )

                if node == 3:
                    # Assert complete set.
                    self.assertEqual(
                        expected_set_node_3,
                        G.nodes[node]["wr_paths"],
                    )
