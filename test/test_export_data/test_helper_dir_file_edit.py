import unittest
import os
from ...src.export_data.helper_dir_file_edit import add_two

import pytest

export_data_test = pytest.mark.skipif("not config.getoption('export_data_tests')")


class Test_main(unittest.TestCase):

    # Initialize test object
    def __init__(self, *args, **kwargs):
        super(Test_main, self).__init__(*args, **kwargs)
        self.script_dir = self.get_script_dir()
        self.project_name = "Whitepaper"

    # returns the directory of this script regardles of from which level the code is executed
    def get_script_dir(self):
        return os.path.dirname(__file__)

    # tests unit test on add_two function of main class
    @export_data_test
    def test_add_two(self):

        expected_result = 7
        result = add_two(5)
        self.assertEqual(expected_result, result)
