# This is the main code of this project nr, and it manages running the code and
# outputting the results to latex.
import argparse

# Project code imports.
from .create_planar_triangle_free_graph import get_graph
from .neumann import compute_mtds
from .neumann_a_t_0 import compute_mtds_a_t_0
from .arg_parser import parse_cli_args

# Export data import.
from .export_data.export_data import export_data


args = parse_cli_args()

# Run main code.
G = get_graph(args, False)
# compute_mtds(G)
compute_mtds_a_t_0(G)

print(f"Done with main code.")
# exit()

# Run data export code if any argument is given.
if not all(arg is None for arg in [args.l, args.dd, args.sd, args.c2l, args.ec2l]):
    export_data(args)
