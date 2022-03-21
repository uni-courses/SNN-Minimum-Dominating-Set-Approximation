import os
import subprocess


def check_if_java_file_exists(relative_filepath):
    """
    Safe check to see if file exists or not.

    Args:
    :param relative_filepath: Path as seen from root towards a file.

    Returns:
        True if a file exists.
        False if a file does not exists.

    Raises:
        Nothing
    """
    if os.path.isfile(relative_filepath):
        return True
    else:
        return False


def got_java_file(relative_filepath):
    """
    Asserts if PlantUML .jar file exists. Tries to download is one time if it
    does not exist at the start of the function.

    Args:
    :param relative_filepath: Path as seen from root towards a file.

    Returns:
        True if a file exists.

    Raises:
        Exception if the PlantUML .jar file does not exist after downloading
        it.
    """
    # Check if the jar file exists, curl it if not.
    if not check_if_java_file_exists(relative_filepath):
        # The java file is not found, curl it
        request_file(
            "https://sourceforge.net/projects/plantuml/files/plantuml.jar/download",
            relative_filepath,
        )
    # Check if the jar file exists after curling it. Raise Exception if it is not found after curling.
    if not check_if_java_file_exists(relative_filepath):
        raise Exception(f"File:{relative_filepath} is not accessible")
    print(f"Got the Java file")
    return True


def request_file(url, output_filepath):
    """
    Downloads a file or file content.

    Args:
    :param url: Url towards a file that will be downloaded.
    :param relative_filepath: The path as seen from the root of this directory, in which files are outputted.

    Returns:
        Nothing

    Raises:
        Nothing
    """
    import requests

    # Request the file in the url
    response = requests.get(url)
    with open(output_filepath, "wb") as f:
        f.write(response.content)


def run_bash_command(bashCommand):
    """
    Unused method. TODO: verify it is unused and delete it.
    :param bashCommand: A string containing a bash command that can be executed.

    """
    # Verbose call.
    # subprocess.Popen(bashCommand, shell=True)
    # Silent call.
    # subprocess.Popen(bashCommand, shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

    # Await completion:
    # Verbose call.
    subprocess.call(bashCommand, shell=True)
    # Silent call.
    # subprocess.call(bashCommand, shell=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
