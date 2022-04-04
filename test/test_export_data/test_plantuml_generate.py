import unittest
import os

import pytest

from src.export_data.Hardcoded_data import Hardcoded_data
from ...src.export_data.plantuml_generate import create_trivial_gantt
from ...src.export_data.plantuml_generate import output_diagram_text_file
from ...src.export_data.helper_dir_file_edit import (
    create_dir_relative_to_root_if_not_exists,
)
from ...src.export_data.helper_dir_file_edit import dir_relative_to_root_exists
from ...src.export_data.helper_dir_file_edit import delete_dir_if_exists

export_data_test = pytest.mark.skipif(
    "not config.getoption('export_data_tests')",
)


class Test_main(unittest.TestCase):

    # Initialize test object
    def __init__(self, *args, **kwargs):
        super(Test_main, self).__init__(*args, **kwargs)
        self.script_dir = self.get_script_dir()
        self.hd = Hardcoded_data()

    # returns the directory of this script regardles of from which level the
    # code is executed.
    def get_script_dir(self):
        return os.path.dirname(__file__)

    @export_data_test
    def test_if_plantuml_file_is_outputted(self):
        diagram_text_filename = "trivial_gantt.uml"
        diagram_text_filepath_relative_to_root = (
            f"{self.hd.dynamic_diagram_dir}/{diagram_text_filename}"
        )

        create_dir_relative_to_root_if_not_exists(self.hd.dynamic_diagram_dir)
        self.assertTrue(
            dir_relative_to_root_exists(self.hd.dynamic_diagram_dir,)
        )

        # Generate a PlantUML diagram.
        filename, lines = create_trivial_gantt(diagram_text_filename)
        output_diagram_text_file(filename, lines, self.hd.dynamic_diagram_dir)

        # Assert file exist.
        self.assertTrue(
            os.path.exists(diagram_text_filepath_relative_to_root,)
        )

        # TODO: Assert file content is correct.

        # Cleanup after
        delete_dir_if_exists(self.hd.dynamic_diagram_dir)
        self.assertFalse(
            dir_relative_to_root_exists(self.hd.dynamic_diagram_dir,)
        )
