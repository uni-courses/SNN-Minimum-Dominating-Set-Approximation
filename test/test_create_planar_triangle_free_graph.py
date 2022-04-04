import unittest
import networkx as nx
from src.create_planar_triangle_free_graph import (
    create_triangle_free_planar_graph,
)

from ..src.graph_properties import is_planar, is_triangle_free


class Test_create_planar_triangle_free_graph(unittest.TestCase):

    # Initialize test object
    def __init__(self, *args, **kwargs):
        super(Test_create_planar_triangle_free_graph, self,).__init__(
            *args, **kwargs
        )

    def test_random_graph_size_3(self):
        nr_nodes = 3
        edge_probability = 0.85
        seed = 42
        G = create_triangle_free_planar_graph(
            nr_nodes, edge_probability, seed, False,
        )
        self.assertTrue(is_triangle_free(G))
        self.assertTrue(is_planar(G))
        self.assertTrue(nx.is_connected(G))

    def test_random_graph_sizes(self):
        for nr_nodes in range(1, 21):
            edge_probability = 0.85
            seed = 42
            G = create_triangle_free_planar_graph(
                nr_nodes, edge_probability, seed, False
            )
            self.assertTrue(is_triangle_free(G))
            self.assertTrue(is_planar(G))
            self.assertTrue(nx.is_connected(G))
