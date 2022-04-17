import unittest
import networkx as nx
from src.helper import (
    combinations,
    generate_list_of_n_random_nrs,
    get_node_and_neighbour_from_degree,
    get_some_sorting_key,
    list_of_all_combinations_of_set,
)
from src.random_generator import spaced_random_lists


class Test_random_generator(unittest.TestCase):
    """
    Tests whether the connection starts and destinations for the synapses
    between the degree_senders and weight receiver neurons are created
    correctly.

    For each node A in graph G, for each neighbour B_A in neightbours_A, for each C_A in
    neightbours_A, A synapse is created from B_A to C_A with B_A!=CA.
    """

    # Initialize test object
    def __init__(self, *args, **kwargs):
        super(Test_random_generator, self).__init__(*args, **kwargs)

    def test_random_generator(self):
        """
        Test whether all combinations of a set are returned.
        """
        actual_result = spaced_random_lists(4, max=None, seed=42)
        expected_result = [1, 3, 5, 7]
        self.assertEqual(expected_result, actual_result)

    def test_random_generator_minimal_list(self):
        """
        Test whether all combinations of a set are returned.
        """
        for i in range(2, 20):
            expected_result = []
            actual_result = spaced_random_lists(i, max=None, seed=42)
            for j in range(0, i):
                expected_result.append(1 + j * 2)
            print(f"i={i}")
            self.assertEqual(expected_result[-1], i * 2 - 1)
            self.assertEqual(expected_result, actual_result)
            print(f"actual_result={actual_result}")

    def test_random_generator_minimal_list_delta(self):
        """
        Test whether all combinations of a set are returned.
        """
        for delta in range(3, 5):
            for i in range(2, 20):
                expected_result = []
                actual_result = spaced_random_lists(i, delta=delta, max=None, seed=42)
                # print(f'i*delta={i*delta}')
                # print(f'delta={delta}')
                for j in range(0, i * delta, delta):
                    # print(f'j={j}')
                    expected_result.append(1 + j)
                # print(f'i={i}')
                print(f"actual_result={actual_result}")
                self.assertEqual(expected_result[-1], i * delta - delta + 1)
                self.assertEqual(expected_result, actual_result)
