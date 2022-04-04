# runs a jupyter notebook and converts it to pdf
import os

from .helper_tex_editing import (
    create_appendix_manager_files,
    export_python_export_code,
    export_python_project_code,
)

from .helper_tex_reading import verify_latex_supports_auto_generated_appendices

from .helper_dir_file_edit import (
    get_all_files_in_dir_and_child_dirs,
    get_filepaths_in_dir,
    remove_all_auto_generated_appendices,
    sort_filepaths_by_filename,
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
    path_to_main_latex_file = f"{latex_dir}{hd.main_latex_filename}"
    root_dir = script_dir + "/../../"
    normalised_root_dir = os.path.normpath(root_dir)
    src_dir = script_dir + "/../"

    # Verify the latex file supports auto-generated python appendices.
    verify_latex_supports_auto_generated_appendices(path_to_main_latex_file)

    # Get paths to files containing project python code.
    python_project_code_filepaths = get_filepaths_in_dir(
        "py", src_dir, ["__init__.py"]
    )

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
    export_python_project_code(
        hd,
        normalised_root_dir,
        sort_filepaths_by_filename(python_project_code_filepaths),
    )
    if include_export_code:
        export_python_export_code(
            hd,
            normalised_root_dir,
            sort_filepaths_by_filename(python_export_code_filepaths),
        )


def get_compiled_notebook_paths(script_dir):
    """Returns the list of jupiter notebook filepaths that were compiled successfully and that are
    included in the same dias this script (the src directory).

    :param script_dir: absolute path of this file.

    """
    notebook_filepaths = get_all_files_in_dir_and_child_dirs(
        ".ipynb", script_dir
    )
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
