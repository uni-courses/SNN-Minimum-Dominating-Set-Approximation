## Entry point for this project, runs the project code and exports data if
# export commmands are given to the cli command that invokes this script.


## Import used functions.
# Project code imports.
from .create_planar_triangle_free_graph import get_graph
from .neumann import compute_mtds
from .neumann_a_t_0 import compute_mtds_a_t_0
from .arg_parser import parse_cli_args

# Export data import.
from .export_data.export_data import export_data


## Parse command line interface arguments to determine what this script does.
args = parse_cli_args()


## Run main code.
G = get_graph(args, False)
# compute_mtds(G)
compute_mtds_a_t_0(G)


## Run data export code if any argument is given.
if not all(arg is None for arg in [args.l, args.dd, args.sd, args.c2l, args.ec2l]):
    export_data(args)
