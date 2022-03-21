import unittest
import os
from ..src.Main import Main
import testbook


class Test_main(unittest.TestCase):

    # Initialize test object
    def __init__(self, *args, **kwargs):
        super(Test_main, self).__init__(*args, **kwargs)
        self.script_dir = self.get_script_dir()

        self.main = Main(1)
        print(f"self.main.add_two(3)={self.main.add_two(3)}")

    # returns the directory of this script regardles of from which level the code is executed
    def get_script_dir(self):
        return os.path.dirname(__file__)

    # tests unit test on add_two function of main class
    def test_add_two(self):

        expected_result = 7
        result = self.main.add_two(5)
        self.assertEqual(expected_result, result)


if __name__ == "__main__":
    unittest.main()
