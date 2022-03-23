from .helper_dir_file_edit import (
    file_contains,
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
