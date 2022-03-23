import os
import shutil
import glob


def file_contains(filepath, substring):
    with open(filepath) as f:
        if substring in f.read():
            return True


def get_dir_filelist_based_on_extension(dir_relative_to_root, extension):
    """

    :param dir_relative_to_root: A relative directory as seen from the root dir of this project.
    :param extension: The file extension that is used/searched in this function.

    """
    selected_filenames = []
    # TODO: assert directory exists
    for filename in os.listdir(dir_relative_to_root):
        if filename.endswith(extension):
            selected_filenames.append(filename)
    return selected_filenames


def create_dir_relative_to_root_if_not_exists(dir_relative_to_root):
    """

    :param dir_relative_to_root: A relative directory as seen from the root dir of this project.

    """
    if not os.path.exists(dir_relative_to_root):
        os.makedirs(dir_relative_to_root)


def dir_relative_to_root_exists(dir_relative_to_root):
    """

    :param dir_relative_to_root: A relative directory as seen from the root dir of this project.

    """
    if not os.path.exists(dir_relative_to_root):
        return False
    elif os.path.exists(dir_relative_to_root):
        return True
    else:
        raise Exception(
            "Directory relative to root: {dir_relative_to_root} did not exist, nor did it exist."
        )


def get_all_files_in_dir_and_child_dirs(extension, path, excluded_files=None):
    """Returns a list of the relative paths to all files within the some path that match
    the given file extension. Also includes files in child directories.

    :param extension: The file extension that is used/searched in this function. The file extension of the file that is sought in the appendix line. Either ".py" or ".pdf".
    :param path: Absolute filepath in which files are being sought.
    :param excluded_files: Default value = None) Files that will not be included even if they are found.

    """
    filepaths = []
    for r, d, f in os.walk(path):
        for file in f:
            if file.endswith(extension):
                if (excluded_files is None) or (
                    (not excluded_files is None) and (not file in excluded_files)
                ):
                    filepaths.append(r + "/" + file)
    return filepaths


def get_filepaths_in_dir(extension, path, excluded_files=None):
    """Returns a list of the relative paths to all files within the some path that match
    the given file extension. Does not include files in child_directories.

    :param extension: The file extension that is used/searched in this function. The file extension of the file that is sought in the appendix line. Either ".py" or ".pdf".
    :param path: Absolute filepath in which files are being sought.
    :param excluded_files: Default value = None) Files that will not be included even if they are found.

    """
    filepaths = []
    current_path = os.getcwd()
    os.chdir(path)
    for file in glob.glob(f"*.{extension}"):
        print(file)
        if (excluded_files is None) or (
            (not excluded_files is None) and (not file in excluded_files)
        ):
            # Append normalised filepath e.g. collapses b/src/../d to b/d.
            filepaths.append(os.path.normpath(f"{path}/{file}"))
    os.chdir(current_path)
    return filepaths


def sort_filepaths_by_filename(filepaths):
    # filepaths.sort(key = lambda x: x.split()[1])
    filepaths.sort(key=lambda x: x[x.rfind("/") + 1 :])
    for filepath in filepaths:
        print(f"{filepath}")
    return filepaths


def get_filename_from_dir(path):
    """Returns a filename from an absolute path to a file.

    :param path: path to a file of which the name is queried.

    """
    return path[path.rfind("/") + 1 :]


def delete_file_if_exists(filepath):
    try:
        os.remove(filepath)
    except OSError:
        pass


def convert_filepath_to_filepath_from_root(filepath, normalised_root_path):
    normalised_filepath = os.path.normpath(filepath)
    filepath_relative_from_root = normalised_filepath[len(normalised_root_path) :]
    return filepath_relative_from_root


def append_lines_to_file(filepath, lines):
    with open(filepath, "a") as the_file:
        for line in lines:
            the_file.write(f"{line}\n")


def append_line_to_file(filepath, line):
    with open(filepath, "a") as the_file:
        the_file.write(f"{line}\n")
        the_file.close()


def remove_all_auto_generated_appendices(hd):

    # TODO: move identifier into hardcoded.
    all_appendix_files = get_all_files_in_dir_and_child_dirs(
        ".tex", hd.appendix_dir_from_root, excluded_files=None
    )
    for file in all_appendix_files:
        if "Auto_generated" in file:
            delete_file_if_exists(file)
