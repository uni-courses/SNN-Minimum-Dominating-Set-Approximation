import unittest
import os
from ..src.Main import Main
from ..src.helper_dir_file_edit import *
from ..src.plantuml_generate import *
from ..src.plantuml_compile import compile_diagrams_in_dir_relative_to_root
from ..src.plantuml_to_tex import export_diagrams_to_latex

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

    def test_if_plantuml_file_is_outputted_compiled_and_moved_to_latex(self):
        diagram_text_filename = "trivial_gantt.uml"
        diagram_image_filename = "trivial_gantt.png"
        dynamic_diagram_dir_relative_to_root = (
            f"code/{self.project_name}/src/Diagrams/Dynamic"
        )
        dynamic_diagram_output_dir_relative_to_root = (
            f"latex/{self.project_name}/Images/Diagrams"
        )

        diagram_text_filepath_relative_to_root = (
            f"{dynamic_diagram_dir_relative_to_root}/{diagram_text_filename}"
        )
        diagram_image_filepath_relative_to_root = (
            f"{dynamic_diagram_dir_relative_to_root}/{diagram_image_filename}"
        )
        create_dir_relative_to_root_if_not_exists(dynamic_diagram_dir_relative_to_root)
        self.assertTrue(
            dir_relative_to_root_exists(dynamic_diagram_dir_relative_to_root)
        )

        # Generate a PlantUML diagram.
        filename, lines = create_trivial_gantt(diagram_text_filename)
        output_diagram_text_file(filename, lines, dynamic_diagram_dir_relative_to_root)

        # Assert file exist.
        self.assertTrue(os.path.exists(diagram_text_filepath_relative_to_root))
        # TODO: Assert file content is correct.

        # Compile diagrams to images.
        await_compilation = True
        extension = ".uml"
        jar_path_relative_from_root = f"code/{self.project_name}/src/plantuml.jar"
        input_dir_relative_to_root = dynamic_diagram_dir_relative_to_root
        verbose = True
        compile_diagrams_in_dir_relative_to_root(
            await_compilation,
            extension,
            jar_path_relative_from_root,
            input_dir_relative_to_root,
            verbose,
        )

        # Assert file exist.
        self.assertTrue(os.path.exists(diagram_image_filepath_relative_to_root))

        # Move the uml file to latex.
        export_diagrams_to_latex(
            input_dir_relative_to_root,
            ".uml",
            dynamic_diagram_output_dir_relative_to_root,
        )
        # Assert file exist.
        self.assertTrue(
            os.path.exists(
                f"{dynamic_diagram_output_dir_relative_to_root}/{diagram_text_filename}"
            )
        )

        # Move the png file to latex.
        export_diagrams_to_latex(
            input_dir_relative_to_root,
            ".png",
            dynamic_diagram_output_dir_relative_to_root,
        )
        # Assert file exist.
        self.assertTrue(
            os.path.exists(
                f"{dynamic_diagram_output_dir_relative_to_root}/{diagram_image_filename}"
            )
        )

        # Cleanup latex/projectX/Images/Diagrams/* after test.
        delete_dir_relative_to_root_if_not_exists(
            dynamic_diagram_output_dir_relative_to_root
        )
        self.assertFalse(
            dir_relative_to_root_exists(dynamic_diagram_output_dir_relative_to_root)
        )

        # Cleanup code/projectX/Diagrams/* after test.
        delete_dir_relative_to_root_if_not_exists(dynamic_diagram_dir_relative_to_root)
        self.assertFalse(
            dir_relative_to_root_exists(dynamic_diagram_dir_relative_to_root)
        )
