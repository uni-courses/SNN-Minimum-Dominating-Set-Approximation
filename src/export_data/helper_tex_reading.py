from .helper_dir_file_edit import (
    file_contains,
    get_all_files_in_dir_and_child_dirs,
    get_filename_from_dir,
    read_file,
)
from .helper_parsing import get_index_of_substring_in_list


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


def get_code_files_not_yet_included_in_appendices(
    code_filepaths, contained_codes, extension
):
    """Returns a list of filepaths that are not yet properly included in some appendix of this project.

    :param code_filepath: Absolute path to all the code files in  this project (source directory).
    (either python files or compiled jupyter notebook pdfs).
    :param contained_codes: list of  Appendix objects that include either python files or compiled jupyter notebook pdfs, which
    are already included in the appendix tex files. (Does not care whether those appendices are also actually
    included in the main or not.)
    :param extension: The file extension that is used/searched in this function. The file extension of the file that is sought in the appendix line. Either ".py" or ".pdf".
    :param code_filepaths:

    """
    contained_filepaths = list(
        map(lambda contained_file: contained_file.code_filepath, contained_codes)
    )
    not_contained = []
    for filepath in code_filepaths:
        if not filepath in contained_filepaths:
            not_contained.append(filepath)
    return not_contained


def get_index_of_auto_generated_appendices(appendix_dir, extension):
    """Returns the maximum index of auto generated appendices of
    a specific extension type.

    :param extension: The file extension that is used/searched in this function. The file extension of the file that is sought in the appendix line. Either ".py" or ".pdf".
    :param appendix_dir: Absolute path that contains the appendix .tex files.

    """
    max_index = -1
    appendices = get_auto_generated_appendix_filenames_of_specific_extension(
        appendix_dir, extension
    )
    for appendix in appendices:
        substring = f"Auto_generated_{extension[1:]}_App"
        # remove left of index
        remainder = appendix[appendix.rfind(substring) + len(substring) :]
        # remove right of index
        index = int(remainder[:-4])
        if index > max_index:
            max_index = index
    return max_index


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


def get_appendix_tex_code(main_latex_filename):
    """gets the latex appendix code from the main tex file.

    :param main_latex_filename: Name of the main latex document of this project number

    """
    main_tex_code = read_file(main_latex_filename)
    # print(f"main_tex_code={main_tex_code}")
    start = "\\begin{appendices}"
    end = "\end{appendices}"
    # TODO: if last 4 characters before \end{appendices} match }}\\fi then don't prepend it,
    # otherwise, do prepend it
    start_index = get_index_of_substring_in_list(main_tex_code, start) + 1
    end_index = get_index_of_substring_in_list(main_tex_code, end)
    return main_tex_code, start_index, end_index, main_tex_code[start_index:end_index]


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


def get_list_of_appendix_files(
    appendix_dir, absolute_notebook_filepaths, absolute_python_project_code_filepaths
):
    """Returns a list of Appendix objects that contain all the appendix files with .tex extension.

    :param appendix_dir: Absolute path that contains the appendix .tex files.
    :param absolute_notebook_filepaths: List of absolute paths to the compiled notebook pdf files.
    :param absolute_python_project_code_filepaths: List of absolute paths to the python files.

    """
    appendices = []
    appendices_paths = get_all_files_in_dir_and_child_dirs(".tex", appendix_dir)
    print(f"appendix_dir={appendix_dir}")
    print(f"appendices_paths={appendices_paths}")
    # exit()
    for appendix_filepath in appendices_paths:
        appendix_type = "no_code"
        appendix_filecontent = read_file(appendix_filepath)
        line_nr_python_file_inclusion = get_line_of_latex_command(
            appendix_filecontent, "\pythonexternal{"
        )
        line_nr_notebook_file_inclusion = get_line_of_latex_command(
            appendix_filecontent, "\includepdf[pages="
        )
        if line_nr_python_file_inclusion > -1:
            appendix_type = "python"
            # get python filename
            line = appendix_filecontent[line_nr_python_file_inclusion]
            filename = get_filename_from_latex_inclusion_command(
                line, ".py", "\pythonexternal{"
            )
            appendices.append(
                Appendix(
                    appendix_filepath,
                    appendix_filecontent,
                    appendix_type,
                    filename,
                    line,
                )
            )
        if line_nr_notebook_file_inclusion > -1:
            appendix_type = "notebook"
            line = appendix_filecontent[line_nr_notebook_file_inclusion]
            filename = get_filename_from_latex_inclusion_command(
                line, ".pdf", "\includepdf[pages="
            )
            appendices.append(
                Appendix(
                    appendix_filepath,
                    appendix_filecontent,
                    appendix_type,
                    filename,
                    line,
                )
            )
        else:
            appendices.append(
                Appendix(appendix_filepath, appendix_filecontent, appendix_type)
            )
    return appendices


def get_filename_from_latex_inclusion_command(
    appendix_line, extension, start_substring
):
    """returns the code/notebook filename in a latex command which includes that code in an appendix.
    The inclusion command includes a python code or jupiter notebook pdf.

    :param appendix_line: Line of latex code (in particular expected to be the latex code from an appendix.).
    :param extension: The file extension that is used/searched in this function. The file extension of the file that is sought in the appendix line. Either ".py" or ".pdf".
    :param start_substring: The substring that characterises the latex inclusion command.

    """
    start_index = appendix_line.index(start_substring)
    end_index = appendix_line.index(extension)
    return get_filename_from_dir(
        appendix_line[start_index : end_index + len(extension)]
    )


def get_code_files_already_included_in_appendices(
    absolute_code_filepaths, appendix_dir, extension, normalised_root_dir
):
    """Returns a list of code filepaths that are already properly included the latex appendix files of this project.

    :param absolute_code_filepaths: List of absolute paths to the code files (either python files or compiled jupyter notebook pdfs).
    :param appendix_dir: Absolute path that contains the appendix .tex files.
    :param extension: The file extension that is used/searched in this function. The file extension of the file that is sought in the appendix line. Either ".py" or ".pdf".
    :param project_name: The name of the project that is being executed/ran. The number  indicating which project this code pertains to.
    :param normalised_root_dir: The root directory of this repository.

    """
    appendix_files = get_all_files_in_dir_and_child_dirs(".tex", appendix_dir)
    contained_codes = []
    for code_filepath in absolute_code_filepaths:
        for appendix_filepath in appendix_files:
            appendix_filecontent = read_file(appendix_filepath)
            line_nr = check_if_appendix_contains_file(
                appendix_filecontent, code_filepath, extension, normalised_root_dir
            )
            if line_nr > -1:
                # add filepath to list of files that are already in the appendices
                contained_codes.append(
                    Appendix_with_code(
                        code_filepath,
                        appendix_filepath,
                        appendix_filecontent,
                        line_nr,
                        ".py",
                    )
                )
    return contained_codes


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
                commented = True
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


def get_missing_appendices(
    appendix_dir, compiled_notebook_pdf_filepaths, normalised_root_dir, python_filepaths
):
    # Check which files are already included in the latex appendicess.
    # TODO: update this method to scan the content of the files referred to in
    # the manual appendices.
    python_files_already_included_in_appendices = get_code_files_already_included_in_appendices(
        python_filepaths, appendix_dir, ".py", normalised_root_dir
    )
    notebook_pdf_files_already_included_in_appendices = get_code_files_already_included_in_appendices(
        compiled_notebook_pdf_filepaths, appendix_dir, ".ipynb", normalised_root_dir,
    )
    print(
        f"python_files_already_included_in_appendices={python_files_already_included_in_appendices}"
    )

    # Get which appendices are still missing.
    missing_python_files_in_appendices = get_code_files_not_yet_included_in_appendices(
        python_filepaths, python_files_already_included_in_appendices, ".py"
    )
    missing_notebook_files_in_appendices = get_code_files_not_yet_included_in_appendices(
        compiled_notebook_pdf_filepaths,
        notebook_pdf_files_already_included_in_appendices,
        ".pdf",
    )
    return missing_python_files_in_appendices, missing_notebook_files_in_appendices
