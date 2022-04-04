import unittest
import networkx as nx

from ..src.graph_properties import is_planar


class Test_graph_planarity(unittest.TestCase):

    # Initialize test object
    def __init__(self, *args, **kwargs):
        super(Test_graph_planarity, self).__init__(*args, **kwargs)

    # https://mathworld.wolfram.com/Pentatope.html
    def test_is_not_planar(self):
        G = nx.complete_graph(5)
        self.assertFalse(is_planar(G))

    def test_is_planar(self):
        # G=create_manual_triangle_free_graph()
        G = nx.Graph()
        G.add_nodes_from([0, 1, 2, 3])
        G.add_edges_from(
            [(0, 1), (1, 2), (2, 3), (3, 0),]
        )
        self.assertTrue(is_planar(G))
