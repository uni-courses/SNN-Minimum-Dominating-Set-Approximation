# This script automatically compiles the text files representing a PlantUML
# diagram into an actual figure.

# To compile locally manually:
# pip install plantuml
# export  PLANTUML_LIMIT_SIZE=8192
# java -jar plantuml.jar -verbose sequenceDiagram.txt

import os
import subprocess
from os.path import abspath

from .helper_dir_file_edit import get_dir_filelist_based_on_extension
from .plantuml_get_package import got_java_file


def compile_diagrams_in_dir_relative_to_root(
    await_compilation,
    extension,
    jar_path_relative_from_root,
    input_dir_relative_to_root,
    verbose,
):
    """
    Loops through the files in a directory and exports them to the latex /Images
    directory.

    Args:
    :param await_compilation: Make python wait untill the PlantUML compilation
    is completed. param extension: The filetype of the text file that is
    converted to image.
    :param jar_path_relative_from_root: The path as seen from root towards the
    PlantUML .jar file that compiles .uml files to .png files.
    :param verbose: True, ensures compilation output is printed to terminal,
    False means compilation is silent.
    :param extension: The file extension that is used/searched in this function.
    :param input_dir_relative_to_root: The directory as seen from root
    containing files that are modified in this function.

    Returns:
        Nothing

    Raises:
        Nothing
    """
    # Verify the PlantUML .jar file is gotten.
    got_java_file(jar_path_relative_from_root)

    diagram_text_filenames = get_dir_filelist_based_on_extension(
        input_dir_relative_to_root, extension
    )

    for diagram_text_filename in diagram_text_filenames:
        diagram_text_filepath_relative_from_root = (
            f"{input_dir_relative_to_root}/{diagram_text_filename}"
        )

        execute_diagram_compilation_command(
            await_compilation,
            jar_path_relative_from_root,
            diagram_text_filepath_relative_from_root,
            verbose,
        )


def execute_diagram_compilation_command(
    await_compilation,
    jar_path_relative_from_root,
    relative_filepath_from_root,
    verbose,
):
    """
    Compiles a .uml/text file containing a PlantUML diagram to a .png image
    using the PlantUML .jar file.

    Args:
    :param await_compilation: Make python wait untill the PlantUML compilation
    is completed. param extension: The filetype of the text file that is
    converted to image.
    :param jar_path_relative_from_root: The path as seen from root towards the
    PlantUML .jar file that compiles .uml files to .png files.
    :param verbose: True, ensures compilation output is printed to terminal,
    False means compilation is silent.
    :param input_dir_relative_to_root: The directory as seen from root
    containing files that are modified in this function.
    Returns:
        Nothing

    Raises:
        Nothing
    """
    # Verify the files required for compilation exist, and convert the paths
    # into absolute filepaths.
    (abs_diagram_filepath, abs_jar_path,) = assert_diagram_compilation_requirements(
        jar_path_relative_from_root,
        relative_filepath_from_root,
    )

    # Generate command to compile the PlantUML diagram locally.
    print(
        f"abs_jar_path={abs_jar_path},"
        + f" abs_diagram_filepath={abs_diagram_filepath}\n\n"
    )
    bash_diagram_compilation_command = (
        f"java -jar {abs_jar_path} -verbose {abs_diagram_filepath}"
    )
    print(f"bash_diagram_compilation_command={bash_diagram_compilation_command}")
    # Generate global variable specifying max image width in pixels, in the
    # shell that compiles.
    os.environ["PLANTUML_LIMIT_SIZE"] = "16192"

    # Perform PlantUML compilation locally.
    if await_compilation:
        if verbose:
            subprocess.call(bash_diagram_compilation_command, shell=True)
        else:
            subprocess.call(
                bash_diagram_compilation_command,
                shell=True,
                stderr=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
            )
    else:
        if verbose:
            subprocess.Popen(bash_diagram_compilation_command, shell=True)
        else:
            subprocess.Popen(
                bash_diagram_compilation_command,
                shell=True,
                stderr=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
            )


def assert_diagram_compilation_requirements(
    jar_path_relative_from_root,
    relative_filepath_from_root,
):
    """
    Asserts that the PlantUML .jar file used for compilation exists, and that
    the diagram file with the .uml content for the diagram exists. Throws an
    error if either of two is missing.

    :param relative_filepath_from_root: Relative filepath as seen from root of
    file that is used in this function.
    :param output_dir_from_root: Relative directory as seen from root, to which
    files are outputted.
    :param jar_path_relative_from_root: The path as seen from root towards the
    PlantUML .jar file that compiles .uml files to .png files.

    Returns:
        Nothing

    Raises:
        Exception if PlantUML .jar file used to compile the .uml to .png files
        is missing.
        Exception if the file with the .uml content is missing.
    """
    abs_diagram_filepath = abspath(relative_filepath_from_root)
    abs_jar_path = abspath(jar_path_relative_from_root)
    if os.path.isfile(abs_diagram_filepath):
        if os.path.isfile(abs_jar_path):
            return abs_diagram_filepath, abs_jar_path
        else:
            raise Exception(
                f"The input diagram file:{abs_diagram_filepath} does not exist."
            )
    else:
        raise Exception(f"The input jar file:{abs_jar_path} does not exist.")
