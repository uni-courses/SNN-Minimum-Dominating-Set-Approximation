# This script generates PlantUML diagrams and outputs them as .uml files.

import os
from os.path import abspath

from .helper_dir_file_edit import create_dir_relative_to_root_if_not_exists
from .helper_dir_file_edit import dir_relative_to_root_exists


def generate_all_dynamic_diagrams(output_dir_relative_to_root):
    """
    Manages the generation of all the diagrams created in this file.

    Args:
    :param output_dir_relative_to_root: Relative path as seen from the root dir of this project, to which modified files are outputted.

    Returns:
        Nothing

    Raises:
    """
    # Create a example Gantt output file.
    filename_one, lines_one = create_trivial_gantt("trivial_gantt.uml")
    output_diagram_text_file(
        filename_one, lines_one, output_dir_relative_to_root
    )

    # Create another example Gantt output file.
    filename_two, lines_two = create_trivial_gantt("another_trivial_gantt.uml")
    output_diagram_text_file(
        filename_two, lines_two, output_dir_relative_to_root,
    )


def output_diagram_text_file(filename, lines, output_dir_relative_to_root):
    """
    Gets the filename and lines of an PlantUML diagram, and writes these to a
    file at the relative output path.

    Args:
    :param filename: The filename of the PlantUML Gantt file that is being created.
    :param lines: The lines of the Gantt chart PlantUML code that is being written to file.
    :param output_dir_relative_to_root: Relative path as seen from the root dir of this project, to which modified files are outputted.

    Returns:
        Nothing

    Raises:
        Exception if input file does not exist.
    """
    abs_filepath = abspath(f"{output_dir_relative_to_root}/{filename}")

    # Ensure output directory is created.
    create_dir_relative_to_root_if_not_exists(output_dir_relative_to_root)
    if not dir_relative_to_root_exists(output_dir_relative_to_root):
        raise Exception(
            f"Error, the output directory relative to root:{output_dir_relative_to_root} does not exist."
        )

    # Delete output file if it already exists.
    if os.path.exists(abs_filepath):
        os.remove(abs_filepath)

    # Write lines to file.
    f = open(abs_filepath, "w")
    for line in lines:
        f.write(line)
    f.close()

    # Assert output file exists.
    if not os.path.isfile(abs_filepath):
        raise Exception(f"The input file:{abs_filepath} does not exist.")


def create_trivial_gantt(filename):
    """
    Creates a trivial Gantt chart.

    Args:
    :param filename: The filename of the PlantUML diagram file that is being
    created.

    Returns:
        The filename of the PlantUML diagram, and the lines of the uml content
        of the diagram

    Raises:
        Nothing
    """
    lines = []
    lines.append("@startuml\n")
    lines.append("[Prototype design] lasts 15 days\n")
    lines.append("[Test prototype] lasts 10 days\n")
    lines.append("\n")
    lines.append("Project starts 2020-07-01\n")
    lines.append("[Prototype design] starts 2020-07-01\n")
    lines.append("[Test prototype] starts 2020-07-16\n")
    lines.append("@enduml\n")
    return filename, lines


def create_another_trivial_gantt(filename):
    """
    Creates a trivial Gantt chart.

    :param filename: The filename of the PlantUML Gantt file that is being created.

    Returns:
        The filename of the PlantUML diagram, and the lines of the uml content
        of the diagram

    Raises:
        Nothing
    """
    lines = []
    lines.append("@startuml\n")
    lines.append("[EXAMPLE SENTENCE] lasts 15 days\n")
    lines.append("[Test prototype] lasts 10 days\n")
    lines.append("\n")
    lines.append("Project starts 2022-07-01\n")
    lines.append("[Prototype design] starts 2022-07-01\n")
    lines.append("[Test prototype] starts 2022-07-16\n")
    lines.append("@enduml\n")

    return filename, lines
