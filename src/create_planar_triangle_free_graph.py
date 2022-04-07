# This code creates a planar graph without triangles.
# Planar implies that it fits on a 2D plane, without any edges crossing.
# Triangle free means there are no triangles in the graph.

import random
import networkx as nx

import matplotlib.pyplot as plt

from src.graph_properties import is_planar, is_triangle_free


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
        plot_graph(graph)
    return graph


def create_manual_triangle_free_graph():
    """
    creates manual test graph with 7 undirected nodes.
    """

    graph = nx.Graph()
    graph.add_nodes_from(
        ["a", "b", "c", "d", "e", "f", "g"],
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
            # ("b", "c"), # Triangle free
            # ("b", "d"),
            ("c", "d"),
            ("d", "e"),
            ("e", "g"),
            ("b", "e"),
            ("b", "f"),
            ("f", "g"),
        ]
    )
    return graph


def create_triangle_free_graph(show_graphs):
    seed = 42
    nr_of_nodes = 10
    probability_of_creating_an_edge = 0.85
    nr_of_triangles = 1  # Initialise at 1 to initiate while loop.
    while nr_of_triangles > 0:
        G = nx.fast_gnp_random_graph(nr_of_nodes, probability_of_creating_an_edge)
        nr_of_triangles = nx.triangles(G, 0)
        print(f"nr_of_triangles={nr_of_triangles}")
        if show_graphs:
            plot_graph(G)
    return G


def create_triangle_free_planar_graph(nr_nodes, edge_probability, seed, show_graph):
    G = nx.Graph()
    G.add_nodes_from(list(range(nr_nodes)))

    # Loop over all edge spaces:
    for u in G.nodes():
        for v in G.nodes():
            # Don't add an edge to a node itself.
            if u != v:

                # Add edge to compute implications.
                G.add_edge(u, v)

                # Check if adding edge yields a triangle free and planar graph.
                if is_triangle_free(G) and is_planar(G):

                    # Apply probability of creating edge
                    # TODO: Use 1-edge_probability to get bias against removing edges.
                    # TODO: Use seed to get certain list of random booleans.
                    if bool(random.getrandbits(1)):
                        G.remove_edge(u, v)
                else:
                    G.remove_edge(u, v)

    # Verify all nodes are connected to graph.
    if not nx.is_connected(G):
        G = add_connections_to_make_graph_connected(G)

    if show_graph:
        plot_graph(G)
    return G


def add_connections_to_make_graph_connected(G):
    # Loop over all edge spaces:
    for u in G.nodes():
        for v in G.nodes():
            # Don't add an edge to a node itself.
            if u != v:
                if not G.has_edge(u, v):

                    # Add edge to compute implications.
                    G.add_edge(u, v)

                    # Check if adding edge yields a triangle free and planar graph.
                    if is_triangle_free(G) and is_planar(G):
                        if nx.is_connected(G):
                            return G
                    else:
                        G.remove_edge(u, v)


# TODO: move to helper
def plot_graph(G):
    options = {
        "with_labels": True,
        "node_color": "white",
        "edgecolors": "blue",
    }
    nx.draw_networkx(G, **options)
    plt.show()
    plt.clf()
