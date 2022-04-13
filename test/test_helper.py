import unittest
import networkx as nx
from src.helper import (
    combinations,
    generate_list_of_n_random_nrs,
    get_some_sorting_key,
    list_of_all_combinations_of_set,
)


class Test_helper(unittest.TestCase):
    """
    Tests whether the connection starts and destinations for the synapses
    between the degree_senders and weight receiver neurons are created
    correctly.

    For each node A in graph G, for each neighbour B_A in neightbours_A, for each C_A in
    neightbours_A, A synapse is created from B_A to C_A with B_A!=CA.
    """

    # Initialize test object
    def __init__(self, *args, **kwargs):
        super(Test_helper, self).__init__(*args, **kwargs)

    def skip_test_weight_receiver_synapse_paths(self):
        """
        Test whether all combinations of a set are returned.
        """
        input = set([(1, 1), (2, 2), (3, 3)])
        expected_result = set(
            [
                (),
                (1, 1),
                ((1, 1), (2, 2)),
                ((1, 1), (3, 3)),
                (2, 2),
                ((2, 2), (1, 1)),
                ((2, 2), (3, 3)),
                (3, 3),
                ((3, 3), (1, 1)),
                ((3, 3), (2, 2)),
                ((1, 1), (2, 2), (3, 3)),
            ]
        )
        actual_result = list_of_all_combinations_of_set(input)
        self.assertEquals(expected_result, actual_result)

    def test_weight_receiver_synapse_paths_123(self):
        """
        Test whether all combinations of a set are returned.
        """
        input = set([1, 2, 3])
        expected_result = set(
            [
                (),
                (1,),
                (2,),
                (3,),
                (1, 2),
                (1, 3),
                (2, 3),
                (1, 2, 3),
            ]
        )
        expected_set = set(expected_result)
        print(f"expected_result=(expected_result)")
        actual_result = list_of_all_combinations_of_set(input)
        self.assertEquals(expected_result, actual_result)

    def test_weight_receiver_synapse_paths_123(self):
        """
        Test whether all combinations of a set are returned.
        """
        input = set([1, 2, 3])
        expected_result = [
            set(),
            {1},
            {2},
            {3},
            {1, 2},
            {2, 3},
            {1, 3},
            {1, 2, 3},
        ]
        sorted_expected_result = sorted(expected_result, key=get_some_sorting_key)
        print(f"sorted_expected_result={sorted(sorted_expected_result)}")
        actual_result = combinations(input)
        self.assertEquals(list(sorted_expected_result), list(actual_result))

    def test_generate_list_of_n_random_nrs(self):

        G = nx.complete_graph(6)
        rand_nrs = generate_list_of_n_random_nrs(G)
        self.assertEquals([1, 2, 3, 4, 5, 6], rand_nrs)

        for n in range(1, 20):
            G = nx.complete_graph(n)
            rand_nrs = generate_list_of_n_random_nrs(G)
            self.assertEquals(list(range(1, n + 1)), rand_nrs)

        G = nx.complete_graph(6)
        rand_nrs = generate_list_of_n_random_nrs(G, 100, seed=42)
        self.assertEquals([29, 18, 95, 14, 87, 70], rand_nrs)

        G = nx.complete_graph(7)
        rand_nrs = generate_list_of_n_random_nrs(G, 100, seed=42)
        self.assertEquals([18, 95, 14, 87, 70, 12, 76], rand_nrs)
