# runs a jupyter notebook and converts it to pdf
import os
import shutil
import ntpath
from .helper_tex_editing import (
    code_filepath_to_tex_appendix_filename,
    create_appendices,
    create_appendices_latex_code,
    create_appendix_file,
    create_appendix_filecontent,
    create_appendix_manager_files,
    export_python_export_code,
    export_python_project_code,
    substitute_appendix_code,
    tex_appendix_filename_to_inclusion_command,
)

from .helper_tex_reading import (
    get_appendix_from_filename,
    get_appendix_tex_code,
    get_filename_from_latex_appendix_line,
    get_list_of_appendix_files,
    line_is_commented,
    verify_latex_supports_auto_generated_appendices,
)

from .helper_dir_file_edit import (
    convert_filepath_to_filepath_from_root,
    get_all_files_in_dir_and_child_dirs,
    get_filename_from_dir,
    overwrite_content_to_file,
    get_filepaths_in_dir,
    file_contains,
    remove_all_auto_generated_appendices,
)


def export_code_to_latex(hd, include_export_code):
    """This function exports the python files and compiled pdfs of jupiter notebooks into the
    latex of the same project number. First it scans which appendices (without code, without
    notebooks) are already manually included in the main latex code. Next, all appendices
    that contain the python code are eiter found or created in the following order:
    First, the __main__.py file is included, followed by the main.py file, followed by all
    python code files in alphabetic order. After this, all the pdfs of the compiled notebooks
    are added in alphabetic order of filename. This order of appendices is overwritten in the
    main tex file.

    :param main_latex_filename: Name of the main latex document of this project number
    :param project_name: The name of the project that is being executed/ran. The number  indicating which project this code pertains to.

    """
    script_dir = get_script_dir()
    latex_dir = script_dir + "/../../latex/"
    appendix_dir = f"{latex_dir}Appendices/"
    path_to_main_latex_file = f"{latex_dir}{hd.main_latex_filename}"
    root_dir = script_dir + "/../../"
    normalised_root_dir = os.path.normpath(root_dir)
    src_dir = script_dir + "/../"

    # Verify the latex file supports auto-generated python appendices.
    verify_latex_supports_auto_generated_appendices(path_to_main_latex_file)

    # Get paths to files containing project python code.
    python_project_code_filepaths = get_filepaths_in_dir("py", src_dir, ["__init__.py"])

    compiled_notebook_pdf_filepaths = get_compiled_notebook_paths(script_dir)
    print(f"python_project_code_filepaths={python_project_code_filepaths}")

    # Get paths to the files containing the latex export code
    if include_export_code:
        python_export_code_filepaths = get_filepaths_in_dir(
            "py", script_dir, ["__init__.py"]
        )

    remove_all_auto_generated_appendices(hd)

    # Create appendix file # ensure they are also deleted at the start of every run.
    create_appendix_manager_files(hd)

    # TODO: Sort main files.
    export_python_project_code(hd, normalised_root_dir, python_project_code_filepaths)
    if include_export_code:
        export_python_export_code(hd, normalised_root_dir, python_export_code_filepaths)

    
def filter_appendices_by_type(appendices, appendix_type):
    """Returns the list of all appendices of a certain appendix type, from the incoming list of Appendix objects.

    :param appendices: List of Appendix objects
    :param appendix_type: Can consist of "no_code", "python", or "notebook" and indicates different appendix types

    """
    return_appendices = []
    for appendix in appendices:
        if appendix.appendix_type == appendix_type:
            return_appendices.append(appendix)
    return return_appendices


def sort_python_appendices(appendices):
    """First puts __main__.py, followed by main.py followed by a-z code files.

    :param appendices: List of Appendix objects

    """
    return_appendices = []
    for appendix in appendices:  # first get appendix containing __main__.py
        if (appendix.code_filename == "__main__.py") or (
            appendix.code_filename == "__Main__.py"
        ):
            return_appendices.append(appendix)
            appendices.remove(appendix)
    for appendix in appendices:  # second get appendix containing main.py
        if (appendix.code_filename == "main.py") or (
            appendix.code_filename == "Main.py"
        ):
            return_appendices.append(appendix)
            appendices.remove(appendix)
    return_appendices

    # Filter remaining appendices in order of a-z
    filtered_remaining_appendices = [
        i for i in appendices if i.code_filename is not None
    ]
    appendices_sorted_a_z = sort_appendices_on_code_filename(
        filtered_remaining_appendices
    )
    return return_appendices + appendices_sorted_a_z


def sort_notebook_appendices_alphabetically(appendices):
    """Sorts notebook appendix objects alphabetic order of their pdf filenames.

    :param appendices: List of Appendix objects

    """
    return_appendices = []
    filtered_remaining_appendices = [
        i for i in appendices if i.code_filename is not None
    ]
    appendices_sorted_a_z = sort_appendices_on_code_filename(
        filtered_remaining_appendices
    )
    return return_appendices + appendices_sorted_a_z


def sort_appendices_on_code_filename(appendices):
    """Returns a list of Appendix objects that are sorted and  based on the property: code_filename.
    Assumes the incoming appendices only contain python files.

    :param appendices: List of Appendix objects

    """
    attributes = list(map(lambda x: x.code_filename, appendices))
    sorted_indices = sorted(range(len(attributes)), key=lambda k: attributes[k])
    sorted_list = []
    for i in sorted_indices:
        sorted_list.append(appendices[i])
    return sorted_list


def get_order_of_non_code_appendices_in_main(appendices, appendix_tex_code):
    """Scans the lines of appendices in the main code, and returns the lines
    of the appendices that do not contain code, in the order in which they were
    included in the main latex file.

    :param appendices: List of Appendix objects
    :param appendix_tex_code: latex code from the main latex file that includes the appendices

    """
    non_code_appendices = []
    non_code_appendix_lines = []
    appendix_tex_code = list(dict.fromkeys(appendix_tex_code))
    for line in appendix_tex_code:
        appendix_filename = get_filename_from_latex_appendix_line(appendices, line)

        # Check if line is not commented
        if not appendix_filename is None:
            if not line_is_commented(line, appendix_filename):
                appendix = get_appendix_from_filename(appendices, appendix_filename)
                if appendix.appendix_type == "no_code":
                    non_code_appendices.append(appendix)
                    non_code_appendix_lines.append(line)
    return non_code_appendices, non_code_appendix_lines


def get_compiled_notebook_paths(script_dir):
    """Returns the list of jupiter notebook filepaths that were compiled successfully and that are
    included in the same dias this script (the src directory).

    :param script_dir: absolute path of this file.

    """
    notebook_filepaths = get_all_files_in_dir_and_child_dirs(".ipynb", script_dir)
    compiled_notebook_filepaths = []

    # check if the jupyter notebooks were compiled
    for notebook_filepath in notebook_filepaths:

        # swap file extension
        notebook_filepath = notebook_filepath.replace(".ipynb", ".pdf")

        # check if file exists
        if os.path.isfile(notebook_filepath):
            compiled_notebook_filepaths.append(notebook_filepath)
    return compiled_notebook_filepaths


def get_script_dir():
    """returns the directory of this script regardles of from which level the code is executed"""
    return os.path.dirname(__file__)


class Appendix_with_code:
    """stores in which appendix file and accompanying line number in the appendix in which a code file is
    already included. Does not take into account whether this appendix is in the main tex file or not


    """

    def __init__(
        self,
        code_filepath,
        appendix_filepath,
        appendix_content,
        file_line_nr,
        extension,
    ):
        self.code_filepath = code_filepath
        self.appendix_filepath = appendix_filepath
        self.appendix_content = appendix_content
        self.file_line_nr = file_line_nr
        self.extension = extension


class Appendix:
    """stores in appendix files and type of appendix."""

    def __init__(
        self,
        appendix_filepath,
        appendix_content,
        appendix_type,
        code_filename=None,
        appendix_inclusion_line=None,
    ):
        self.appendix_filepath = appendix_filepath
        self.appendix_filename = get_filename_from_dir(self.appendix_filepath)
        self.appendix_content = appendix_content
        self.appendix_type = appendix_type  # TODO: perform validation of input values
        self.code_filename = code_filename
        self.appendix_inclusion_line = appendix_inclusion_line
