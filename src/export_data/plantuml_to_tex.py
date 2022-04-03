from posixpath import abspath
from shutil import copyfile
import shutil
import os.path

from .helper_dir_file_edit import get_dir_filelist_based_on_extension
from .helper_dir_file_edit import create_dir_relative_to_root_if_not_exists


def export_diagrams_to_latex(
    input_dir_relative_to_root, extension, output_dir_relative_to_root
):
    """Loops through the files in a directory and exports them to the latex /Images
    directory.

    :param dir: The directory in which the Gantt charts are being searched.
    :param extension: The file extension that is used/searched in this function. The filetypes that are being exported.
    :param input_dir_relative_to_root: Relative path as seen from the root dir of this project, containing files that modified in this function.
    :param output_dir_relative_to_root: Relative path as seen from the root dir of this project, to which modified files are outputted.

    """
    diagram_filenames = get_dir_filelist_based_on_extension(
        input_dir_relative_to_root, extension
    )
    if len(diagram_filenames) > 0:
        # Ensure output directory is created.
        create_dir_relative_to_root_if_not_exists(output_dir_relative_to_root)

    for diagram_filename in diagram_filenames:
        diagram_filepath_relative_from_root = (
            f"{input_dir_relative_to_root}/{diagram_filename}"
        )

        export_gantt_to_latex(
            diagram_filepath_relative_from_root, output_dir_relative_to_root
        )


def export_gantt_to_latex(
    relative_filepath_from_root, output_dir_relative_to_root
):
    """
    Takes an input filepath and an output directory as input and copies the
    file towards the output directory.

    :param relative_filepath_from_root: Relative filepath as seen from root of
    file that is used in this function.
    :param output_dir_relative_to_root: Relative path as seen from the root dir of this project, to which modified files are outputted.

    Returns:
        Nothing.

    Raises:
        Exception if the output directory does not exist.
        Exception if the input file is not found.
    """
    if os.path.isfile(relative_filepath_from_root):
        if os.path.isdir(output_dir_relative_to_root):
            shutil.copy(
                relative_filepath_from_root, output_dir_relative_to_root
            )
        else:
            raise Exception(
                f"The output directory:{output_dir_relative_to_root} does not exist."
            )
    else:
        raise Exception(
            f"The input file:{relative_filepath_from_root} does not exist."
        )
