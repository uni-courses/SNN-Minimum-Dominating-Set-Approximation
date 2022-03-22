# Data export imports.
from .Hardcoded_data import Hardcoded_data

from .create_dynamic_diagrams import create_dynamic_diagrams
from .create_static_diagrams import create_static_diagrams
from .latex_export_code import export_code_to_latex
from .latex_compile import compile_latex


def export_data(args):

    hd = Hardcoded_data()

    ## PlantUML
    create_dynamic_diagrams(args, hd)
    create_static_diagrams(args, hd)

    ## Plotting
    # Generate plots.
    # Export plots to LaTex.

    ## Export code to LaTex.
    if args.c2l:
        # TODO: verify whether the latex/{project_name}/Appendices folder exists before exporting.
        # TODO: verify whether the latex/{project_name}/Images folder exists before exporting.
        export_code_to_latex(hd, False)
    elif args.ec2l:
        # TODO: verify whether the latex/{project_name}/Appendices folder exists before exporting.
        # TODO: verify whether the latex/{project_name}/Images folder exists before exporting.
        export_code_to_latex(hd, True)

    ## Compile the accompanying LaTex report.
    if args.l:
        compile_latex(True, True)
        print("")
    print(f"\n\nDone exporting data.")
