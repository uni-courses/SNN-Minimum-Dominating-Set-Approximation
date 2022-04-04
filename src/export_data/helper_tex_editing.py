import os
from .helper_dir_file_edit import (
    append_line_to_file,
    append_lines_to_file,
    convert_filepath_to_filepath_from_root,
    delete_file_if_exists,
    get_filename_from_dir,
)


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
            "Error, a file can't be both project code, and export code at"
            + " same time."
        )
    if not is_project_code and not is_export_code:
        raise Exception(
            "Error, don't know what to do with files that are neither project"
            + " code, nor export code."
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


def create_appendix_filecontent(
    latex_object_name, filename, filepath_from_root, from_root
):
    # Latex titles should escape underscores.
    filepath_from_root_without_underscores = filepath_from_root.replace(
        "_", "\_"
    )
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


def export_python_project_code(
    hd, normalised_root_dir, python_project_code_filepaths
):
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
            hd,
            filepath,
            normalised_root_dir,
            True,
            is_export_code,
            is_project_code,
        )


def export_python_export_code(
    hd, normalised_root_dir, python_export_code_filepaths
):
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
            hd,
            filepath,
            normalised_root_dir,
            True,
            is_export_code,
            is_project_code,
        )


def create_appendices(
    hd,
    filepath,
    normalised_root_dir,
    from_root,
    is_export_code,
    is_project_code,
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
        appendix_inclusion_command,
        from_root,
        hd,
        is_export_code,
        is_project_code,
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
