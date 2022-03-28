import unittest
import os
from ..src.neumann_a_t_0 import add_two


class Test_neumann_a_t_0(unittest.TestCase):

    # Initialize test object
    def __init__(self, *args, **kwargs):
        super(Test_neumann_a_t_0, self).__init__(*args, **kwargs)
        self.script_dir = self.get_script_dir()

    # returns the directory of this script regardles of from which level the code is executed
    def get_script_dir(self):
        return os.path.dirname(__file__)

    # tests unit test on add_two function of main class
    def test_add_two(self):

        expected_result = 7
        result = add_two(5)
        self.assertEqual(expected_result, result)

