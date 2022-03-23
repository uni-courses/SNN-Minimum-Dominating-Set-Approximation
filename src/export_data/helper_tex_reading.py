from .helper_dir_file_edit import (
    file_contains,
    get_all_files_in_dir_and_child_dirs,
    get_filename_from_dir,
    read_file,
)


def get_latex_inclusion_command(extension, code_filepath_relative_from_latex_dir):
    """Creates and returns a latex command that includes either a python file or a compiled jupiter
    notebook pdf (whereever the command is placed). The command is intended to be placed in the appendix.

    :param extension: The file extension that is used/searched in this function. The file extension of the file that is sought in the appendix line. Either ".py" or ".pdf".
    :param code_filepath_relative_from_latex_dir: The latex compilation requires a relative path towards code files
    that are included. Therefore, a relative path towards the code is given.

    """
    if extension == ".py":
        left = "\pythonexternal{"
        right = "}"
        latex_command = f"{left}{code_filepath_relative_from_latex_dir}{right}"
    elif extension == ".ipynb":

        left = "\includepdf[pages=-]{"
        right = "}"
        latex_command = f"{left}{code_filepath_relative_from_latex_dir}{right}"
    return latex_command


def get_auto_generated_appendix_filenames_of_specific_extension(
    appendix_dir, extension
):
    """Returns the list of auto generated appendices of
    a specific extension type.

    :param extension: The file extension that is used/searched in this function. The file extension of the file that is sought in the appendix line. Either ".py" or ".pdf".
    :param appendix_dir: Absolute path that contains the appendix .tex files.

    """
    appendices_of_extension_type = []

    # get all appendices
    appendix_files = get_all_files_in_dir_and_child_dirs(".tex", appendix_dir)

    # get appendices of particular extention type
    for appendix_filepath in appendix_files:
        right_of_slash = appendix_filepath[appendix_filepath.rfind("/") + 1 :]
        if (
            right_of_slash[: 15 + len(extension) - 1]
            == f"Auto_generated_{extension[1:]}"
        ):
            appendices_of_extension_type.append(appendix_filepath)
    return appendices_of_extension_type


def verify_latex_supports_auto_generated_appendices(path_to_main_latex_file):
    # TODO: change verification to complete tex block(s) for appendices.
    # TODO: Also verify related boolean and if statement creations.
    determining_overleaf_home_line = "\def\overleafhome{/tmp}% change as appropriate"
    begin_apendices_line = "\\begin{appendices}"
    print(f"determining_overleaf_home_line={determining_overleaf_home_line}")
    print(f"begin_apendices_line={begin_apendices_line}")

    if not file_contains(path_to_main_latex_file, determining_overleaf_home_line):
        raise Exception(
            f"Error, {path_to_main_latex_file} does not contain:\n\n{determining_overleaf_home_line}\n\n so this Python code cannot export the code as latex appendices."
        )
    if not file_contains(path_to_main_latex_file, determining_overleaf_home_line):
        raise Exception(
            f"Error, {path_to_main_latex_file} does not contain:\n\n{begin_apendices_line}\n\n so this Python code cannot export the code as latex appendices."
        )


def get_filename_from_latex_appendix_line(appendices, appendix_line):
    """Returns the first filename from a list of incoming filenames that
    occurs in a latex code line.

    :param appendices: List of Appendix objects
    :param appendix_line: latex code (in particular expected to be the code from main that is used to include appendix latex files.)

    """
    for filename in list(map(lambda appendix: appendix.appendix_filename, appendices)):
        if filename in appendix_line:
            if not line_is_commented(appendix_line, filename):
                return filename


def get_appendix_from_filename(appendices, appendix_filename):
    """Returns the first Appendix object with an appendix filename that matches the incoming appendix_filename.
    The Appendix objects are selected from an incoming list of Appendix objects.

    :param appendices: List of Appendix objects
    :param appendix_filename: name of a latex appendix file, ends in .tex,

    """
    for appendix in appendices:
        if appendix_filename == appendix.appendix_filename:
            return appendix


def check_if_appendix_contains_file(
    appendix_content, code_filepath, extension, normalised_root_dir
):
    """Scans an appendix content to determine whether it contains a substring that
    includes a code file (of either python or compiled notebook=pdf extension).

    :param appendix_content: content in an appendix latex file.
    :param code_filepath: Absolute path to a code file (either python files or compiled jupyter notebook pdfs).
    :param extension: The file extension that is used/searched in this function. The file extension of the file that is sought in the appendix line. Either ".py" or ".pdf".
    :param project_name: The name of the project that is being executed/ran. The number  indicating which project this code pertains to.
    :param normalised_root_dir: The root directory of this repository.

    """
    # convert code_filepath to the inclusion format in latex format

    code_filepath_relative_from_latex_dir = (
        f"latex/../../{code_filepath[len(normalised_root_dir):]}"
    )
    print(f"code_filepath={code_filepath}")
    print(
        f"code_filepath_relative_from_latex_dir={code_filepath_relative_from_latex_dir}"
    )
    latex_command = get_latex_inclusion_command(
        extension, code_filepath_relative_from_latex_dir
    )
    return get_line_of_latex_command(appendix_content, latex_command)


def get_line_of_latex_command(appendix_content, latex_command):
    """Returns the line number of a latex command if it is found. Returns -1 otherwise.

    :param appendix_content: content in an appendix latex file.
    :param latex_command: A line of latex code. (Expected to come from some appendix)

    """
    # check if the file is in the latex code
    line_nr = 0
    for line in appendix_content:
        if latex_command in line:
            if line_is_commented(line, latex_command):
                pass
            else:
                return line_nr
        line_nr = line_nr + 1
    return -1


def line_is_commented(line, target_substring):
    """Returns True if a latex code line is commented, returns False otherwise

    :param line: A line of latex code that contains a relevant command (target substring).
    :param target_substring: Used to determine whether the command that is found is commented or not.

    """
    left_of_command = line[: line.rfind(target_substring)]
    if "%" in left_of_command:
        return True
    return False
