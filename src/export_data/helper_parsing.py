#from src.export_data.helper_tex_reading import line_is_commented
#from export_data.helper_tex_reading import line_is_commented
#from .helper_tex_reading import line_is_commented

import os
cwd = os.getcwd()


def get_index_of_substring_in_list(lines, target_substring):
    """Returns the index of the line in which the first character of a latex substring if it is found
    uncommented in the incoming list.

    :param lines: List of lines of latex code.
    :param target_substring: Some latex command/code that is sought in the incoming text.

    """
    for i in range(0, len(lines)):
        if target_substring in lines[i]:
            if not line_is_commented(lines[i], target_substring):
                return i
