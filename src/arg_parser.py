# This is the main code of this project nr, and it manages running the code and
# outputting the results to latex.
import argparse

def parse_cli_args():
    # Instantiate the parser
    parser = argparse.ArgumentParser(description="Optional app description")

    ## Include argument parsing for default code.
    parser.add_argument(
        "--g",
        dest="graph_from_file",
        action="store_true",
        help="boolean flag, determines whether energy analysis graph is created from file ",
    )
    parser.add_argument("infile", nargs="?", type=argparse.FileType("r"))


    parser.set_defaults(
        infile=None, graph_from_file=False,
    )


    ## Include argument parsing for data exporting code.
    # Compile Latex
    parser.add_argument(
        "--l", action="store_true", help="Boolean indicating if code compiles latex"
    )

    # Generate, compile and export Dynamic PlantUML diagrams.
    parser.add_argument(
        "--dd",
        action="store_true",
        help="A boolean indicating if code generated diagrams are compiled and exported.",
    )
    # Generate, compile and export Static PlantUML diagrams.
    parser.add_argument(
        "--sd",
        action="store_true",
        help="A boolean indicating if static diagrams are compiled and exported.",
    )

    # Export the project code to latex.
    parser.add_argument(
        "--c2l",
        action="store_true",
        help="A boolean indicating if project code is exported to latex.",
    )

    # Export the exporting code to latex.
    parser.add_argument(
        "--ec2l",
        action="store_true",
        help="A boolean indicating if code that exports code is exported to latex.",
    )

    # Load the arguments that are given.
    args = parser.parse_args()
    return args