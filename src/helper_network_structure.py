import copy
from gettext import npgettext
import numpy as np
import networkx as nx
import pylab as plt
from networkx.drawing.nx_agraph import graphviz_layout
from src.create_planar_triangle_free_graph import plot_basic_graph
from src.helper import get_y_position


def get_weight_receiver_synapse_paths_fully_connected(G):
    # Set weight receiver synapse path attribute (as a list) for each node in
    # graph G.
    # nx.set_node_attributes(G, set(), "wr_paths")

    for node in G.nodes:
        G.nodes[node]["wr_paths"] = set()
    for node in G.nodes:
        for neighbour in nx.all_neighbors(G, node):
            for target in nx.all_neighbors(G, node):
                if neighbour != node and target != node and target != neighbour:
                    G.nodes[node]["wr_paths"].add((neighbour, target))
    return G


def get_degree_graph_with_separate_wta_circuits(G, rand_nrs):
    """Returns a networkx graph that represents the snn that computes the
    spiking degree in the degree_receiver neurons.
    One node in the graph represents one neuron.
    A directional edge in the graph represents a synapse between two
    neurons.

    One spike once neuron is created per node in graph G.
    One degree_receiver neuron is created per node in graph G.
    A synapse is created from each spike_once neuron that represents node A
    to each of the degree_receiver that represents a neighbour of node A.
    """
    get_degree = nx.DiGraph()
    # First create all the nodes in the get_degree graph.
    for node in G.nodes:

        # One neuron per node named: spike_once_0-n
        get_degree.add_node(
            f"spike_once_{node}",
            id=node,
            du=0,
            dv=0,
            bias=2,
            vth=1,
            pos=(float(0), float(node)),
        )

        for neighbour in nx.all_neighbors(G, node):
            if node != neighbour:
                # One neuron per node named: degree_receiver_0-n.
                get_degree.add_node(
                    f"degree_receiver_{node}_{neighbour}",
                    id=node,
                    du=0,
                    dv=1,
                    bias=0,
                    vth=1,
                    pos=(float(1.0), get_y_position(G, node, neighbour)),
                )
            # print(f"created:degree_receiver_{node}_{neighbour}")

        # One neuron per node named: rand
        if len(rand_nrs) < len(G):
            raise Exception(
                "The range of random numbers does not allow for randomness collision prevention."
            )

        get_degree.add_node(
            f"rand_{node}",
            id=node,
            du=0,
            dv=0,
            bias=2,
            vth=1,
            pos=(float(0.25), float(node) + 0.5),
        )

        # Add winner selector node
        get_degree.add_node(
            f"selector_{node}",
            id=node,
            du=0,
            dv=1,
            bias=5,  # Always spike unless inhibitied by u[t]
            vth=4,
            pos=(float(1.25), float(node)),
        )

        # Add winner selector node
        get_degree.add_node(
            f"counter_{node}",
            id=node,
            du=0,
            dv=0,
            bias=2,  # Always spike unless inhibitied by u[t]
            vth=1,
            pos=(float(1.5), float(node)),
        )

    # Then create all edges between the nodes.
    for circuit in G.nodes:
        # For each neighbour of node, named degree_receiver:
        for neighbour_a in G.nodes:
            if neighbour_a in nx.all_neighbors(G, circuit) or neighbour_a == circuit:
                for neighbour_b in nx.all_neighbors(G, circuit):
                    if circuit != neighbour_b and neighbour_a != neighbour_b:

                        # Check if there is an edge from neighbour_a to neighbour_b.
                        if neighbour_a in nx.all_neighbors(G, neighbour_b):
                            get_degree.add_edges_from(
                                [
                                    (
                                        f"spike_once_{circuit}",
                                        f"degree_receiver_{neighbour_a}_{neighbour_b}",
                                    )
                                ],
                                weight=+1,
                            )

        # Add synapse between random node and degree receiver nodes.
        for circuit_target in G.nodes:
            if circuit != circuit_target:
                # Check if there is an edge from neighbour_a to neighbour_b.
                if circuit in nx.all_neighbors(G, circuit_target):
                    get_degree.add_edges_from(
                        [
                            (
                                f"rand_{circuit}",
                                f"degree_receiver_{circuit_target}_{circuit}",
                            )
                        ],
                        weight=rand_nrs[circuit],
                    )
                    # print(
                    #    f"edge: rand_{circuit_target}, degree_receiver_{circuit_target}_{circuit}, weight={rand_nrs[circuit]}"
                    # )

        # Add synapse from degree_selector to selector node.
        for neighbour_b in nx.all_neighbors(G, circuit):
            if circuit != neighbour_b:
                get_degree.add_edges_from(
                    [
                        (
                            f"degree_receiver_{circuit}_{neighbour_b}",
                            f"selector_{circuit}",
                        )
                    ],
                    weight=-5,  # to disable bias
                )
                # print(
                #    f"edge: degree_receiver_{circuit}_{neighbour_b},selector_{circuit}, weight=-5"
                # )
                # TODO: UPDATE TO Go from degree_receiver_x_y to counter_y.
                get_degree.add_edges_from(
                    [
                        (
                            f"degree_receiver_{circuit}_{neighbour_b}",
                            f"counter_{neighbour_b}",
                        )
                    ],
                    weight=+1,  # to disable bias
                )
                # print(
                #    f"edge: degree_receiver_{circuit}_{neighbour_b}, selector_{circuit},weight=+1"
                # )
        # TODO:
        # Add synapse from selector node back into degree selector.
        for neighbour_b in nx.all_neighbors(G, circuit):
            if circuit != neighbour_b:
                get_degree.add_edges_from(
                    [
                        (
                            f"selector_{circuit}",
                            f"degree_receiver_{circuit}_{neighbour_b}",
                        )
                    ],
                    weight=1,  # To increase u(t) at every timestep.
                )
            # print(f"selector_{circuit} degree_receiver_{circuit}_{neighbour_b}")

    return get_degree


def get_weight_receiver_synapse_paths(G):
    # Set weight receiver synapse path attribute (as a list) for each node in
    # graph G.
    # nx.set_node_attributes(G, set(), "wr_paths")

    for node in G.nodes:
        G.nodes[node]["wr_paths"] = set()
    for node in G.nodes:
        for neighbour in nx.all_neighbors(G, node):
            for target in nx.all_neighbors(G, node):
                if neighbour != node and target != node and target != neighbour:
                    G.nodes[node]["wr_paths"].add((neighbour, target))
    return G


def plot_unstructured_graph(G):
    # nx.draw(G, pos=graphviz_layout(G),with_labels = True)
    #
    # edge_labels = nx.get_edge_attributes(G,'weight')
    # print(f'edge_labels={edge_labels}')
    # pos = nx.spring_layout(G)
    ##nx.draw_networkx_edge_labels(G, pos, labels=edge_labels)
    # nx.draw_networkx_edge_labels(G,pos, edge_labels)
    # pos = nx.spring_layout(G)
    # pos = nx.graphviz_layout(G)
    # nx.draw(G, pos)
    nx.draw(G, pos=graphviz_layout(G), with_labels=True)
    node_labels = nx.get_node_attributes(G, "")
    nx.draw_networkx_labels(G, pos=graphviz_layout(G), labels=node_labels)
    edge_labels = nx.get_edge_attributes(G, "weight")
    nx.draw_networkx_edge_labels(G, graphviz_layout(G), edge_labels)
    # plt.savefig('this.png')

    plt.show()
    plt.clf()


def plot_coordinated_graph(G):
    nx.draw(G, nx.get_node_attributes(G, "pos"), with_labels=True, node_size=1)
    node_labels = nx.get_node_attributes(G, "")
    pos = {node: (x, y) for (node, (x, y)) in nx.get_node_attributes(G, "pos").items()}
    nx.draw_networkx_labels(G, pos, labels=node_labels)
    edge_labels = nx.get_edge_attributes(G, "weight")
    nx.draw_networkx_edge_labels(G, pos, edge_labels)

    plt.show()
    plt.clf()
