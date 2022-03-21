# This is the main code of this project nr, and it manages running the code and
# outputting the results to latex.
import argparse

# Project code imports.
from .create_planar_triangle_free_graph import get_graph
from .neumann import compute_mtds
from .neumann_a_t_0 import compute_mtds_a_t_0

# Data export imports.
from .export_data.Export_manager import Export_manager
from .export_data.latex_export_code import export_code_to_latex
from .export_data.latex_compile import compile_latex
from .export_data.plantuml_generate import generate_all_dynamic_diagrams
from .export_data.plantuml_compile import compile_diagrams_in_dir_relative_to_root
from .export_data.plantuml_to_tex import export_diagrams_to_latex


# TODO: move into separate argument parser.
# Instantiate the parser
parser = argparse.ArgumentParser(description="Optional app description")

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

# Load the arguments that are given.
args = parser.parse_args()

# Run main code.
G = get_graph(args, True)
#compute_mtds(G)
compute_mtds_a_t_0(G)

print(f"Done with main code.")
exit()

# TODO: move to export_data
# Specify hardcoded data.
print(f"Hi, I'll be running the main code, and I'll let you know when I'm done.")
root_dir = "new_whitepaper"
main_latex_filename = "report.tex"
export_data_dirname = "export_data"
path_to_export_data = f"src/{export_data_dirname}"
append_export_code_to_latex = True

# Specify code configuration details
comile_locally = False
await_compilation = True
verbose = True
gantt_extension = ".uml"
diagram_extension = ".png"

# Specify paths relative to root.
jar_path_relative_from_root = f"{path_to_export_data}/plantuml.jar"
path_to_dynamic_gantts = f"{path_to_export_data}/Diagrams/Dynamic"
path_to_static_gantts = f"{path_to_export_data}/Diagrams/Static"
dynamic_diagram_output_dir_relative_to_root = f"latex/Images/Diagrams"

## Run main code.
export_manager = Export_manager()

## PlantUML
# Generate PlantUML diagrams dynamically (using code).
if args.dd:
    generate_all_dynamic_diagrams(f"{path_to_export_data}/Diagrams/Dynamic")

    # Compile dynamically generated PlantUML diagrams to images.
    compile_diagrams_in_dir_relative_to_root(
        await_compilation,
        gantt_extension,
        jar_path_relative_from_root,
        path_to_dynamic_gantts,
        verbose,
    )

    # Export dynamic PlantUML text files to LaTex.
    export_diagrams_to_latex(
        path_to_dynamic_gantts,
        gantt_extension,
        dynamic_diagram_output_dir_relative_to_root,
    )

    # Export dynamic PlantUML diagram images to LaTex.
    export_diagrams_to_latex(
        path_to_dynamic_gantts,
        diagram_extension,
        dynamic_diagram_output_dir_relative_to_root,
    )

if args.sd:
    # Compile statically generated PlantUML diagrams to images.
    compile_diagrams_in_dir_relative_to_root(
        await_compilation,
        gantt_extension,
        jar_path_relative_from_root,
        path_to_static_gantts,
        verbose,
    )

    # Export static PlantUML text files to LaTex.
    export_diagrams_to_latex(
        path_to_static_gantts,
        gantt_extension,
        dynamic_diagram_output_dir_relative_to_root,
    )

    # Export static PlantUML diagram images to LaTex.
    export_diagrams_to_latex(
        path_to_static_gantts,
        diagram_extension,
        dynamic_diagram_output_dir_relative_to_root,
    )


## Plotting
# Generate plots.

# Export plots to LaTex.


## Export code to LaTex.
if args.ec2l:
    # TODO: verify whether the latex/{project_name}/Appendices folder exists before exporting.
    # TODO: verify whether the latex/{project_name}/Images folder exists before exporting.
    export_code_to_latex(main_latex_filename, False)
elif args.ec2l:
    # TODO: verify whether the latex/{project_name}/Appendices folder exists before exporting.
    # TODO: verify whether the latex/{project_name}/Images folder exists before exporting.
    export_code_to_latex(main_latex_filename, append_export_code_to_latex)


## Compile the accompanying LaTex report.
if args.l:
    compile_latex(True, True)
    print("")
print(f"\n\nDone.")
