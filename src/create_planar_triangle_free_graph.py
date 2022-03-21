# This code creates a planar graph without triangles.
# Planar implies that it fits on a 2D plane, without any edges crossing.
# Triangle free means there are no triangles in the graph.

import networkx as nx

import matplotlib.pyplot as plt


def get_graph(args, show_graph):
    if args.infile and not args.graph_from_file:
        try:
            graph = nx.read_graphml(args.infile.name)
        except Exception as exc:
            raise Exception(
                "Supplied input file is not a gml networkx graph object."
            ) from exc
    else:
        graph = create_manual_test_graph()
    if show_graph:
        show_graph(graph)
    return graph


def create_manual_test_graph():
    """
    creates manual test graph with 7 undirected nodes.
    """

    graph = nx.Graph()
    graph.add_nodes_from(
        ["a", "b", "c", "d", "e", "f", "g"],
        x=0,
        color="w",
        dynamic_degree=0,
        delta_two=0,
        p=0,
        xds=0,
    )
    graph.add_edges_from(
        [
            ("a", "b"),
            ("a", "c"),
            ("b", "c"),
            ("b", "d"),
            ("c", "d"),
            ("d", "e"),
            ("b", "e"),
            ("b", "f"),
            ("f", "g"),
        ]
    )
    return graph


# TODO: move to helper
def show_graph(G):
    options = {"with_labels": True, "node_color": "white", "edgecolors": "blue"}
    nx.draw_networkx(G, **options)
    plt.show()
    plt.clf()
