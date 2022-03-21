# Data export imports.
from .Export_manager import Export_manager
from .latex_export_code import export_code_to_latex
from .latex_compile import compile_latex
from .plantuml_generate import generate_all_dynamic_diagrams
from .plantuml_compile import compile_diagrams_in_dir_relative_to_root
from .plantuml_to_tex import export_diagrams_to_latex


def export_data(args):

    # Specify hardcoded data.
    print(f"Hi, I'll export some data, I'll let you know when I'm done.")
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

    import os

    print(os.getcwd())

    ## Export code to LaTex.
    if args.c2l:
        # TODO: verify whether the latex/{project_name}/Appendices folder exists before exporting.
        # TODO: verify whether the latex/{project_name}/Images folder exists before exporting.
        export_code_to_latex(main_latex_filename, False)
    elif args.ec2l:
        # TODO: verify whether the latex/{project_name}/Appendices folder exists before exporting.
        # TODO: verify whether the latex/{project_name}/Images folder exists before exporting.
        export_code_to_latex(main_latex_filename, append_export_code_to_latex)

    print(f"RUNNING COMPILE")
    import os

    print(os.getcwd())

    ## Compile the accompanying LaTex report.
    if args.l:
        compile_latex(True, True)
        print("")
    print(f"\n\nDone.")
