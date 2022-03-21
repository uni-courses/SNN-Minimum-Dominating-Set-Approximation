import os
import shutil
import glob


def delete_directory_contents(self, folder):
    """

    :param folder: Directory that is being deleted.

    """
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print("Failed to delete %s. Reason: %s" % (file_path, e))


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


def delete_dir_relative_to_root_if_not_exists(dir_relative_to_root):
    """

    :param dir_relative_to_root: A relative directory as seen from the root dir of this project.

    """
    if os.path.exists(dir_relative_to_root):
        # Remove directory and its content.
        shutil.rmtree(dir_relative_to_root)


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
    current_path=os.getcwd()
    os.chdir(path)
    for file in glob.glob(f"*.{extension}"):
        print(file)
        if (excluded_files is None) or (
            (not excluded_files is None) and (not file in excluded_files)
        ):
            filepaths.append(f"{path}/{file}")
    os.chdir(current_path)
    return filepaths
