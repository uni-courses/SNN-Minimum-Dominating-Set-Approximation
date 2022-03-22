import os
from .helper_dir_file_edit import (
    append_line_to_file,
    append_lines_to_file,
    convert_filepath_to_filepath_from_root,
    delete_file_if_exists,
    get_filename_from_dir,
    overwrite_content_to_file,
)
from .helper_tex_reading import (
    get_index_of_auto_generated_appendices,
    get_latex_inclusion_command,
)


def add_include_code_in_appendix(
    content,
    code_filepath_relative_from_root,
    extension,
    code_filepath_relative_from_latex_dir,
    normalised_root_dir,
):
    """Includes the latex code that includes code in the script.

    :param content: The latex content that is being written to an appendix.
    :param code_path_from_latex_main_path: the path to the code as seen from the folder that contains main.tex.
    :param extension: The file extension that is used/searched in this function. The file extension of the file that is sought in the appendix line. Either ".py" or ".pdf".
    :param code_filepath_relative_from_latex_dir: The latex compilation requires a relative path towards code files
    that are included. Therefore, a relative path towards the code is given.
    :param code_filepath_relative_from_root: param code_filepath_relative_from_latex_dir:
    :param project_name: The name of the project that is being executed/ran. param normalised_root_dir:
    :param code_filepath_relative_from_latex_dir: param normalised_root_dir:
    :param normalised_root_dir:

    """
    print(f"before={content}")

    # TODO: append if exists}
    content.append("%TESTCOMMENT")
    latex_path_to_python_file = "src/filename"
    print(f"code_filepath_relative_from_root={code_filepath_relative_from_root}")
    line = f"\IfFileExists{{{code_filepath_relative_from_latex_dir}}}{{"
    print(f"line={line}")
    content.append(line)
    # append current line
    content.append(
        get_latex_inclusion_command(extension, code_filepath_relative_from_latex_dir)
    )
    # TODO: append {}
    content.append(f"}}{{")
    # TODO: code_path_from latex line
    content.append(
        get_latex_inclusion_command(extension, code_filepath_relative_from_latex_dir)
    )
    # TODO: add closing bracket }
    content.append(f"}}")
    content.append("%TESTCOMMENTCLOSING")
    print(f"after={content}")
    return content


def create_appendices_with_code(
    appendix_dir, code_filepaths, extension, normalised_root_dir
):
    """Creates the latex appendix files in with relevant codes included.

    :param appendix_dir: Absolute path that contains the appendix .tex files.
    :param code_filepaths: Absolute path to code files that are not yet included in an appendix
    (either python files or compiled jupyter notebook pdfs).
    :param extension: The file extension that is used/searched in this function. The file extension of the file that is sought in the appendix line. Either ".py" or ".pdf".
    :param project_name: The name of the project that is being executed/ran. The number  indicating which project this code pertains to.
    :param normalised_root_dir: The root directory of this repository.

    """
    appendix_filenames = []
    appendix_reference_index = (
        get_index_of_auto_generated_appendices(appendix_dir, extension) + 1
    )
    print(f"\n\ncode_filepaths={code_filepaths}")
    for code_filepath in code_filepaths:
        normalised_code_filepath = os.path.normpath(code_filepath)
        code_filepath_relative_from_root = normalised_code_filepath[
            len(normalised_root_dir) :
        ]
        code_filepath_relative_from_latex_dir = (
            f"latex/..{code_filepath_relative_from_root}"
        )
        print(f"normalised_code_filepath={normalised_code_filepath}")
        print(f"code_filepath_relative_from_root={code_filepath_relative_from_root}")
        print(
            f"code_filepath_relative_from_latex_dir={code_filepath_relative_from_latex_dir}"
        )

        # code_filename=get_filename_from_dir(code_filepath)
        content = []
        filename = get_filename_from_dir(normalised_code_filepath)

        content = create_section(appendix_reference_index, filename, content)
        content = add_include_code_in_appendix(
            content,
            code_filepath_relative_from_root,
            extension,
            code_filepath_relative_from_latex_dir,
            normalised_root_dir,
        )

        print(f"content={content}")

        overwrite_content_to_file(
            content,
            f"{appendix_dir}Auto_generated_{extension[1:]}_App{appendix_reference_index}.tex",
            False,
        )
        appendix_filenames.append(
            f"Auto_generated_{extension[1:]}_App{appendix_reference_index}.tex"
        )
        appendix_reference_index = appendix_reference_index + 1
    return appendix_filenames


def create_section(appendix_reference_index, code_filename, content):
    """Creates the header of a latex appendix file, such that it contains a section that
    indicates the section is an appendix, and indicates which pyhon or notebook file is
    being included in that appendix.

    :param appendix_reference_index: A counter that is used in the label to ensure the appendix section labels are unique.
    :param code_filename: file name of the code file that is included
    :param content: A list of strings that make up the appendix, with one line per element.

    """
    # write section
    left = "\section{Appendix "
    middle = code_filename.replace("_", "\_")
    right = "}\label{app:"
    end = "}"  # TODO: update appendix reference index
    content.append(f"{left}{middle}{right}{appendix_reference_index}{end}")
    return content


def update_appendix_tex_code(appendix_filename, is_from_normalised_root_dir):
    """Returns the latex command that includes an appendix .tex file in an appendix environment
    as can be used in the main tex file.

    :param appendix_filename: Name of the appendix that is included by the generated command.
    :param project_name: The name of the project that is being executed/ran. The number indicating which project this code pertains to.
    :param is_from_normalised_root_dir:

    """
    if is_from_normalised_root_dir:
        left = f"\input{{latex/"
    else:
        left = "\input{"
    middle = "Appendices/"
    right = "} \\newpage\n"
    return f"{left}{middle}{appendix_filename}{right}"


def substitute_appendix_code(
    end_index, main_tex_code, start_index, updated_appendices_tex_code
):
    """Replaces the old latex code that included the appendices in the main.tex file with the new latex
    commands that include the appendices in the latex report.

    :param end_index: Index at which the appendix section ends right before the latex \end{appendix} line,
    :param main_tex_code: The code that is saved in the main .tex file.
    :param start_index: Index at which the appendix section starts right after the latex \begin{appendix} line,
    :param updated_appendices_tex_code: The newly created code that includes all the relevant appendices.
    (relevant being (in order): manually created appendices, python codes, pdfs of compiled jupiter notebooks).

    """
    start_of_main_tex_code_till_appendices = main_tex_code[0:start_index]
    tex_code_after_appendices = inject_closing_hide_source_conditional_close(
        main_tex_code[end_index:]
    )
    updated_main_tex_code = (
        start_of_main_tex_code_till_appendices
        + updated_appendices_tex_code
        + tex_code_after_appendices
    )
    print(f"start_index={start_index}")
    print(f"main_tex_code[end_index:] ={main_tex_code[end_index:]}")
    return updated_main_tex_code


def inject_closing_hide_source_conditional_close(tex_code_after_appendices):
    injected_string_to_close_conditional = "}}\\fi"

    # Get the line directly after the (autogenerated) appendices.
    line_closing_appendices = tex_code_after_appendices[0]
    # Get the first characters of that closing line to see if they match the
    # injected string that needs to be in.
    start_of_close = line_closing_appendices[
        : len(injected_string_to_close_conditional)
    ]

    # If the first 4 characters do not start with the close of the hide source
    # code conditional, then inject that close. Othwerise return tex code as is.
    if start_of_close == f"{injected_string_to_close_conditional}":
        return tex_code_after_appendices
    else:
        # Inject the string that closes the hidesourcecode conditional.
        tex_code_after_appendices[
            0
        ] = f"{injected_string_to_close_conditional}{tex_code_after_appendices[0]}"
        return tex_code_after_appendices


def create_appendices_latex_code(
    main_latex_filename,
    main_non_code_appendix_inclusion_lines,
    notebook_appendices,
    python_appendices,
):
    """Creates the latex code that includeds the appendices in the main latex file.

    :param main_non_code_appendix_inclusion_lines: latex code that includes the appendices that do not contain python code nor notebooks
    :param notebook_appendices: List of Appendix objects representing appendices that include the pdf files of compiled Jupiter notebooks
    :param project_name: The name of the project that is being executed/ran. The number indicating which project this code pertains to.
    :param python_appendices: List of Appendix objects representing appendices that include the python code files.
    :param main_latex_filename:

    """
    main_appendix_inclusion_lines = main_non_code_appendix_inclusion_lines
    print(f"BEFORE main_appendix_inclusion_lines={main_appendix_inclusion_lines}")

    appendices_of_all_types = [python_appendices, notebook_appendices]

    print(f"\n\n")
    main_appendix_inclusion_lines.append("\ifhidesourcecode{}\else{")
    main_appendix_inclusion_lines.append(
        f"\IfFileExists{{latex/{main_latex_filename}}}{{"
    )
    main_appendix_inclusion_lines = append_latex_inclusion_command(
        appendices_of_all_types, True, main_appendix_inclusion_lines,
    )
    main_appendix_inclusion_lines.append(f"}}{{")
    main_appendix_inclusion_lines = append_latex_inclusion_command(
        appendices_of_all_types, False, main_appendix_inclusion_lines,
    )
    print(f"AFTER main_appendix_inclusion_lines={main_appendix_inclusion_lines}")
    return main_appendix_inclusion_lines


def append_latex_inclusion_command(
    appendices_of_all_types, is_from_normalised_root_dir, main_appendix_inclusion_lines,
):
    """

    :param appendices_of_all_types: param is_from_normalised_root_dir:
    :param main_appendix_inclusion_lines: param project_name:
    :param is_from_normalised_root_dir: param project_name:
    :param project_name: The name of the project that is being executed/ran.

    """
    for appendix_type in appendices_of_all_types:
        for appendix in appendix_type:
            line = update_appendix_tex_code(
                appendix.appendix_filename, is_from_normalised_root_dir
            )
            print(f"appendix.appendix_filename={appendix.appendix_filename}")
            main_appendix_inclusion_lines.append(line)
    return main_appendix_inclusion_lines


def code_filepath_to_tex_appendix_line(code_filepath, from_root, hd, root_dir):
    pass


def code_filepath_to_tex_appendix_filename(
    filename, from_root, is_project_code, is_export_code
):

    # TODO: Include assert to verify filename ends at .py.
    # TODO: Include assert to verify filename doesn't end at .py anymore.
    filename_without_extension = os.path.splitext(filename)[0]

    # Create appendix filename identifier segment
    verify_input_code_type(is_export_code, is_project_code)
    if is_project_code:
        identifier = "Auto_generated_project_code_appendix_"
    elif is_export_code:
        identifier = "Auto_generated_export_code_appendix_"

    appendix_filename = f"{identifier}{filename_without_extension}"
    return appendix_filename


def verify_input_code_type(is_export_code, is_project_code):
    # Create appendix filename identifier segment
    if is_project_code and is_export_code:
        raise Exception(
            "Error, a file can't be both project code, and export code at same time."
        )
    if not is_project_code and not is_export_code:
        raise Exception(
            "Error, don't know what to do with files that are neither project code, nor export code."
        )


def tex_appendix_filename_to_inclusion_command(appendix_filename, from_root):
    # Create full appendix filename.
    if from_root:
        # Generate latex inclusion command for latex compilation from root dir.
        appendix_inclusion_command = (
            f"\input{{latex/Appendices/{appendix_filename}.tex}} \\newpage"
        )
        # \input{latex/Appendices/Auto_generated_py_App8.tex} \newpage
    else:
        # \input{Appendices/Auto_generated_py_App8.tex} \newpage
        appendix_inclusion_command = (
            f"\input{{Appendices/{appendix_filename}.tex}} \\newpage"
        )
    return appendix_inclusion_command


def tex_appendix_filepath_to_inclusion_command(appendix_filepath):
    # Generate latex inclusion command for latex compilation from root dir.
    appendix_inclusion_command = f"\input{{{appendix_filepath}}} \\newpage"
    return appendix_inclusion_command


def create_appendix_filecontent(
    latex_object_name, filename, filepath_from_root, from_root
):
    # Latex titles should escape underscores.
    filepath_from_root_without_underscores = filepath_from_root.replace("_", "\_")
    lines = []
    lines.append(
        f"\{latex_object_name}{{Appendix {filepath_from_root_without_underscores}}}\label{{app:{filename}}}"
    )
    if from_root:
        lines.append(f"\pythonexternal{{latex/..{filepath_from_root}}}")
    else:
        lines.append(f"\pythonexternal{{latex/..{filepath_from_root}}}")
    return lines


def create_appendix_manager_files(hd):
    # Verify target directory exists.
    if not os.path.exists(hd.appendix_dir_from_root):
        raise Exception(
            f"Error, the Appendices directory was not found at:{hd.appendix_dir_from_root}"
        )

    # Delete appendix manager files.
    list(
        map(
            lambda x: delete_file_if_exists(f"{hd.appendix_dir_from_root}{x}"),
            hd.automatic_appendices_manager_filenames,
        )
    )

    # Create new appendix_manager_files
    list(
        map(
            lambda x: open(f"{hd.appendix_dir_from_root}{x}", "a"),
            hd.automatic_appendices_manager_filenames,
        )
    )

    # Ensure manual appendix_manager_files are created.
    list(
        map(
            lambda x: open(f"{hd.appendix_dir_from_root}{x}", "a"),
            hd.manual_appendices_manager_filenames,
        )
    )


def create_appendix_file(
    hd,
    filename,
    filepath_from_root,
    latex_object_name,
    is_export_code,
    is_project_code,
):
    verify_input_code_type(is_export_code, is_project_code)
    filename_without_extension = os.path.splitext(filename)[0]
    if is_project_code:
        # Create the appendix for the case the latex is compiled from root.
        appendix_filepath = f"{hd.appendix_dir_from_root}/Auto_generated_project_code_appendix_{filename_without_extension}.tex"

        # Append latex_filepath to appendix manager.
        # append_lines_to_file(
        #    f"{hd.appendix_dir_from_root}{hd.project_code_appendices_filename}",
        #    [tex_appendix_filepath_to_inclusion_command(appendix_filepath)],
        # )

        # Get Appendix .tex content.
        appendix_lines_from_root = create_appendix_filecontent(
            latex_object_name, filename, filepath_from_root, True
        )

        # Write appendix to .tex file.
        append_lines_to_file(appendix_filepath, appendix_lines_from_root)
    elif is_export_code:
        # Create the appendix for the case the latex is compiled from root.
        appendix_filepath = f"{hd.appendix_dir_from_root}/Auto_generated_export_code_appendix_{filename_without_extension}.tex"

        # Append latex_filepath to appendix manager.
        # append_lines_to_file(
        #    f"{hd.appendix_dir_from_root}{hd.export_code_appendices_filename}",
        #    [tex_appendix_filepath_to_inclusion_command(appendix_filepath)],
        # )

        # Get Appendix .tex content.
        appendix_lines_from_root = create_appendix_filecontent(
            latex_object_name, filename, filepath_from_root, True
        )

        # Write appendix to .tex file.
        append_lines_to_file(appendix_filepath, appendix_lines_from_root)
    # TODO: verify files exist


def export_python_project_code(hd, normalised_root_dir, python_project_code_filepaths):
    is_project_code = True
    is_export_code = False
    from_root = False
    for filepath in python_project_code_filepaths:
        create_appendices(
            hd,
            filepath,
            normalised_root_dir,
            from_root,
            is_export_code,
            is_project_code,
        )
        create_appendices(
            hd, filepath, normalised_root_dir, True, is_export_code, is_project_code
        )


def export_python_export_code(hd, normalised_root_dir, python_export_code_filepaths):
    is_project_code = False
    is_export_code = True
    from_root = False
    for filepath in python_export_code_filepaths:
        create_appendices(
            hd,
            filepath,
            normalised_root_dir,
            from_root,
            is_export_code,
            is_project_code,
        )
        create_appendices(
            hd, filepath, normalised_root_dir, True, is_export_code, is_project_code
        )


def create_appendices(
    hd, filepath, normalised_root_dir, from_root, is_export_code, is_project_code
):
    # Get the filepath of a python file from the root dir of this project.
    filepath_from_root = convert_filepath_to_filepath_from_root(
        filepath, normalised_root_dir
    )
    print(f"from_root={from_root},filepath_from_root={filepath_from_root}")

    # Get the filename of a python filepath
    filename = get_filename_from_dir(filepath)

    # Get the filename for a latex appendix from a python filename.
    appendix_filename = code_filepath_to_tex_appendix_filename(
        filename, from_root, is_project_code, is_export_code
    )

    # Command to include the appendix in the appendices manager.
    appendix_inclusion_command = tex_appendix_filename_to_inclusion_command(
        appendix_filename, from_root
    )
    # if from_root:
    #    print(f'tex_appendix_filename_to_inclusion_command={appendix_inclusion_command}')
    #    exit()

    append_appendix_to_appendix_managers(
        appendix_inclusion_command, from_root, hd, is_export_code, is_project_code
    )

    # Create appendix .tex file content.
    # TODO: move "section" to hardcoded.
    appendix_lines = create_appendix_filecontent(
        "section", filename, filepath_from_root, from_root
    )

    # Create the appendix .tex file.
    # TODO: move "section" to hardcoded.
    if from_root:  # Appendix only contains files readable from root.
        create_appendix_file(
            hd,
            filename,
            filepath_from_root,
            "section",
            is_export_code,
            is_project_code,
        )


def append_appendix_to_appendix_managers(
    appendix_inclusion_command, from_root, hd, is_export_code, is_project_code
):
    # Append the appendix .tex file to the appendix manager.
    if is_project_code:
        if from_root:
            # print(f'from_root={from_root}Append to:{hd.project_code_appendices_filename_from_root}')
            append_line_to_file(
                f"{hd.appendix_dir_from_root}{hd.project_code_appendices_filename_from_root}",
                appendix_inclusion_command,
            )
        else:
            # print(f'from_root={from_root}Append to:{hd.project_code_appendices_filename}')
            append_line_to_file(
                f"{hd.appendix_dir_from_root}{hd.project_code_appendices_filename}",
                appendix_inclusion_command,
            )

    if is_export_code:
        if from_root:
            append_line_to_file(
                f"{hd.appendix_dir_from_root}{hd.export_code_appendices_filename_from_root}",
                appendix_inclusion_command,
            )
        else:
            append_line_to_file(
                f"{hd.appendix_dir_from_root}{hd.export_code_appendices_filename}",
                appendix_inclusion_command,
            )
