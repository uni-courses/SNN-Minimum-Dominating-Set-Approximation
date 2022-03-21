import subprocess


def run_bash_command(await_compilation, bash_command, verbose):
    if await_compilation:
        if verbose:
            subprocess.call(bash_command, shell=True)
        else:
            subprocess.call(
                bash_command,
                shell=True,
                stderr=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
            )
    else:
        if verbose:
            subprocess.Popen(bash_command, shell=True)
        else:
            subprocess.Popen(
                bash_command,
                shell=True,
                stderr=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
            )
