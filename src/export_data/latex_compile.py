# Compiles the latex report using the compile script.
from .helper_bash_commands import run_bash_command


def compile_latex(await_compilation, verbose):
    """
    Compiles the LaTex report of this project using its compile script.

    :param await_compilation: Make python wait untill the PlantUML compilation
    is completed.
    :param project_name: The name of the project that is being executed/ran.
    :param verbose: True, ensures compilation output is printed to terminal,
    False means compilation is silent.

    Returns:
        Nothing.

    Raises:
        Nothing.
    """
    # Ensure compile script is runnable.
    bash_make_compile_script_runnable_command = (
        "chmod +x latex/compile_script.sh",
    )
    run_bash_command(
        await_compilation,
        bash_make_compile_script_runnable_command,
        verbose,
    )

    # Run latex compilation script to compile latex project.
    bash_compilation_command = "latex/compile_script.sh"
    run_bash_command(await_compilation, bash_compilation_command, verbose)
