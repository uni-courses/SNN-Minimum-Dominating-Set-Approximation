import unittest
import os
from ..src.Main import Main
from ..src.helper_dir_file_edit import *

# import testbook


class Test_main(unittest.TestCase):

    # Initialize test object
    def __init__(self, *args, **kwargs):
        super(Test_main, self).__init__(*args, **kwargs)
        self.script_dir = self.get_script_dir()
        self.project_name = "Whitepaper"

    # returns the directory of this script regardles of from which level the code is executed
    def get_script_dir(self):
        return os.path.dirname(__file__)

    def test_dir_relative_to_root_is_created_and_deleted(self):
        dynamic_diagram_dir_relative_to_root = (
            f"latex/{self.project_name}/Images/Diagrams/Dynamic"
        )
        create_dir_relative_to_root_if_not_exists(dynamic_diagram_dir_relative_to_root)
        self.assertTrue(
            dir_relative_to_root_exists(dynamic_diagram_dir_relative_to_root)
        )

        # Cleanup after
        delete_dir_relative_to_root_if_not_exists(dynamic_diagram_dir_relative_to_root)
        self.assertFalse(
            dir_relative_to_root_exists(dynamic_diagram_dir_relative_to_root)
        )
