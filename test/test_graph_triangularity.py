import unittest
import networkx as nx
from src.create_planar_triangle_free_graph import (
    create_manual_triangle_free_graph,
    plot_graph,
)

from ..src.graph_properties import is_triangle_free


class Test_graph_triangularity(unittest.TestCase):

    # Initialize test object
    def __init__(self, *args, **kwargs):
        super(Test_graph_triangularity, self).__init__(*args, **kwargs)

    def test_is_not_triangle_free(self):
        G = nx.complete_graph(5)
        self.assertFalse(is_triangle_free(G))

    def test_is_triangle_free(self):
        # G=create_manual_triangle_free_graph()
        G = nx.Graph()
        G.add_nodes_from([0, 1, 2, 3])
        G.add_edges_from(
            [
                (0, 1),
                (1, 2),
                (2, 3),
                (3, 0),
            ]
        )
        plot_graph(G)
        self.assertTrue(is_triangle_free(G))
