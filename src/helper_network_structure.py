import copy
from gettext import npgettext
from pprint import pprint
import numpy as np
import networkx as nx
import pylab as plt
from networkx.drawing.nx_agraph import graphviz_layout
from src.create_planar_triangle_free_graph import plot_basic_graph
from src.export_data.Plot_to_tex import Plot_to_tex
from src.export_data.helper_tex_editing import export_python_export_code
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


def get_degree_graph_with_separate_wta_circuits(G, rand_nrs, rand_ceil, m):
    m = m + 1
    d = 0.25 * m  # specify grid distance size
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
    # Define list of m mappings for sets of tupples containing synapses
    left = [{} for _ in range(m)]
    right = [{} for _ in range(m)]

    # Create a node to make the graph connected. (Otherwise, recurrent snn builder can not span/cross the network.)
    get_degree.add_node(
        f"connecting_node",
        id=len(G.nodes),
        du=0,
        dv=0,
        bias=0,
        vth=1,
        pos=(float(-d), float(d)),
    )

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
            pos=(float(0), float(node * 4 * d)),
        )

        for neighbour in nx.all_neighbors(G, node):
            if node != neighbour:
                # One neuron per node named: degree_receiver_0-n.
                # get_degree.add_node(
                #    f"degree_receiver_{node}_{neighbour}",
                #    id=node,
                #    du=0,
                #    dv=1,
                #    bias=0,
                #    vth=1,
                #    pos=(float(1.0), get_y_position(G, node, neighbour)),
                # )

                for loop in range(0, m):
                    get_degree.add_node(
                        f"degree_receiver_{node}_{neighbour}_{loop}",
                        id=node,
                        du=0,
                        dv=1,
                        bias=0,
                        vth=1,
                        pos=(
                            float(4 * d + loop * 9 * d),
                            get_y_position(G, node, neighbour, d),
                        ),
                    )

        # One neuron per node named: rand
        if len(rand_nrs) < len(G):
            raise Exception(
                "The range of random numbers does not allow for randomness collision prevention."
            )

        for loop in range(0, m):
            get_degree.add_node(
                f"rand_{node}_{loop}",
                id=node,
                du=0,
                dv=0,
                bias=2,
                vth=1,
                pos=(float(d + loop * 9 * d), float(node * 4 * d) + d),
            )

        # Add winner selector node
        for loop in range(0, m):
            get_degree.add_node(
                f"selector_{node}_{loop}",
                id=node,
                du=0,
                dv=1,
                bias=5,
                vth=4,
                pos=(float(7 * d + loop * 9 * d), float(node * 4 * d + d)),
            )

        # Add winner selector node
        # for loop in range(0, m):
        get_degree.add_node(
            f"counter_{node}_{m-1}",
            id=node,
            du=0,
            dv=1,
            bias=0,
            vth=0,
            pos=(float(9 * d + loop * 9 * d), float(node * 4 * d)),
        )
        # for loop in range(0, m):
        #    get_degree.add_node(
        #        f"depleter_{node}_{loop}",
        #        id=node,
        #        du=1,
        #        dv=1,
        #        bias=0,
        #        vth=0,
        #        pos=(float(9 * d + loop * 9 * d), float(node * 4 * d) - d),
        #    )

        # Create next round connector neurons.
        for loop in range(1, m):
            get_degree.add_node(
                f"next_round_{loop}",
                id=node,
                du=0,
                dv=1,
                bias=0,
                vth=len(G.nodes) - 1,
                pos=(float(6 * d + (loop - 1) * 9 * d), -2 * d),
            )

            get_degree.add_node(
                f"d_charger_{loop}",
                id=node,
                du=0,
                dv=1,
                bias=0,
                vth=0,
                pos=(float(9 * d + (loop - 1) * 9 * d), -2 * d),
            )

            get_degree.add_node(
                f"delay_{loop}",
                id=node,
                du=0,
                dv=1,
                bias=0,
                vth=2 * (len(G)) - 1,
                pos=(float(12 * d + (loop - 1) * 9 * d), -2 * d),
            )

    # Ensure SNN graph is connected(Otherwise, recurrent snn builder can not span/cross the network.)
    for circuit in G.nodes:
        get_degree.add_edges_from(
            [
                (
                    f"connecting_node",
                    f"spike_once_{circuit}",
                )
            ],
            weight=0,
        )
    for node in G.nodes:
        for neighbour in nx.all_neighbors(G, node):
            if node != neighbour:
                for other_node in G.nodes:
                    if G.has_edge(neighbour, other_node):

                        get_degree.add_edges_from(
                            [
                                (
                                    f"spike_once_{other_node}",
                                    f"degree_receiver_{node}_{neighbour}_0",
                                )
                            ],
                            weight=rand_ceil,
                        )

                        for loop in range(0, m - 1):
                            # get_degree.add_edges_from(
                            #    [
                            #        (
                            #            f"counter_{other_node}_{loop}",
                            #            f"degree_receiver_{node}_{neighbour}_{loop+1}",
                            #        )
                            #    ],
                            #    weight=rand_ceil,
                            # )
                            # Create list of outgoing edges from a certain counter neuron.
                            if not f"counter_{other_node}_{loop}" in right[loop]:
                                right[loop][f"counter_{other_node}_{loop}"] = []
                            right[loop][f"counter_{other_node}_{loop}"].append(
                                f"degree_receiver_{node}_{neighbour}_{loop+1}"
                            )

    #    for node in G.nodes:
    #        print(f'node={node},neighbours={list(nx.all_neighbors(G, node))}')
    #        for other_node in G.nodes:
    #        #for neighbour in nx.all_neighbors(G, node):
    #            if node != other_node and G.has_edge(node, other_node):
    #                # This is a degree receiver in form:degree_receiver_{node}_{neighbour}
    #

    # Then create all edges between the nodes.
    for loop in range(1, m):
        get_degree.add_edges_from(
            [
                (
                    f"next_round_{loop}",
                    f"d_charger_{loop}",
                )
            ],
            weight=1,
        )
        get_degree.add_edges_from(
            [
                (
                    f"delay_{loop}",
                    f"d_charger_{loop}",
                )
            ],
            weight=-1,
        )
        get_degree.add_edges_from(
            [
                (
                    f"d_charger_{loop}",
                    f"delay_{loop}",
                )
            ],
            weight=+1,
        )

    for circuit in G.nodes:
        for loop in range(1, m):
            # TODO
            get_degree.add_edges_from(
                [
                    (
                        f"delay_{loop}",
                        f"selector_{circuit}_{loop}",
                    )
                ],
                weight=1,  # TODO: doubt.
            )

        # Add synapse between random node and degree receiver nodes.
        for circuit_target in G.nodes:
            if circuit != circuit_target:
                # Check if there is an edge from neighbour_a to neighbour_b.
                if circuit in nx.all_neighbors(G, circuit_target):
                    for loop in range(0, m):
                        get_degree.add_edges_from(
                            [
                                (
                                    f"rand_{circuit}_{loop}",
                                    f"degree_receiver_{circuit_target}_{circuit}_{loop}",
                                )
                            ],
                            weight=rand_nrs[circuit],
                        )

                    # for loop in range(0, m):
                    # TODO: change to degree_receiver_x_y_z and update synapses for loop from 1,m to 0,m.
                    for loop in range(1, m):
                        get_degree.add_edges_from(
                            [
                                (
                                    f"degree_receiver_{circuit_target}_{circuit}_{loop-1}",
                                    f"next_round_{loop}",
                                )
                            ],
                            weight=1,
                        )

        # for loop in range(0, m):
        #    get_degree.add_edges_from(
        #        [
        #            (
        #                f"next_round_{loop}",
        #                f"depleter_{circuit}_{loop}",
        #            )
        #        ],
        #        weight=+1,
        #    )
        # for loop in range(0, m):
        #    get_degree.add_edges_from(
        #        [
        #            (
        #                f"counter_{circuit}_{loop}",
        #                f"depleter_{circuit}_{loop}",
        #            )
        #        ],
        #        weight=+1,
        #    )
        #    get_degree.add_edges_from(
        #        [
        #            (
        #                f"depleter_{circuit}_{loop}",
        #                f"counter_{circuit}_{loop}",
        #            )
        #        ],
        #        weight=+len(G),
        #    )

        # Add synapse from degree_selector to selector node.
        for neighbour_b in nx.all_neighbors(G, circuit):
            if circuit != neighbour_b:
                get_degree.add_edges_from(
                    [
                        (
                            f"degree_receiver_{circuit}_{neighbour_b}_{m-1}",
                            f"counter_{neighbour_b}_{m-1}",
                        )
                    ],
                    weight=+1,  # to disable bias
                )
                print(
                    f"degree_receiver_{circuit}_{neighbour_b}_{m-1} to: counter_{neighbour_b}_{m-1} with loop={loop}"
                )
                for loop in range(0, m):
                    get_degree.add_edges_from(
                        [
                            (
                                f"degree_receiver_{circuit}_{neighbour_b}_{loop}",
                                f"selector_{circuit}_{loop}",
                            )
                        ],
                        weight=-5,  # to disable bias
                    )
                    # Create list of outgoing edges from a certain counter neuron.
                    if (
                        not f"degree_receiver_{circuit}_{neighbour_b}_{loop}"
                        in left[loop]
                    ):
                        left[loop][
                            f"degree_receiver_{circuit}_{neighbour_b}_{loop}"
                        ] = []
                    left[loop][
                        f"degree_receiver_{circuit}_{neighbour_b}_{loop}"
                    ].append(f"counter_{neighbour_b}_{loop}")

                # print(
                #    f"edge: degree_receiver_{circuit}_{neighbour_b}, selector_{circuit},weight=+1"
                # )
        # TODO:
        # Add synapse from selector node back into degree selector.
        for neighbour_b in nx.all_neighbors(G, circuit):
            if circuit != neighbour_b:
                for loop in range(0, m):
                    get_degree.add_edges_from(
                        [
                            (
                                f"selector_{circuit}_{loop}",
                                f"degree_receiver_{circuit}_{neighbour_b}_{loop}",
                            )
                        ],
                        weight=1,  # To increase u(t) at every timestep.
                    )
            # print(f"selector_{circuit} degree_receiver_{circuit}_{neighbour_b}")
    # pprint(f"left={left}")
    # pprint(f"right={right}")

    # Create replacement synapses.
    for id in range(m - 1):
        for l_key, l_value in left[id].items():
            for l_counter in l_value:
                for r_key, r_value in right[id].items():
                    for r_degree in r_value:
                        if l_counter == r_key:
                            get_degree.add_edges_from(
                                [
                                    (
                                        l_key,
                                        r_degree,
                                    )
                                ],
                                weight=rand_ceil,  # To increase u(t) at every timestep.
                            )

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


def plot_unstructured_graph(G, iteration, size, show=False):
    nx.draw(G, with_labels=True)
    if show:
        plt.show()
    plot_export = Plot_to_tex()
    plot_export.export_plot(plt, f"G_{size}_{iteration}")
    plt.clf()
    plt.close()


def plot_coordinated_graph(G, iteration, size, show=False):
    # Width=edge width.
    nx.draw(
        G,
        nx.get_node_attributes(G, "pos"),
        with_labels=True,
        node_size=8,
        font_size=5,
        width=0.2,
    )
    node_labels = nx.get_node_attributes(G, "")
    pos = {node: (x, y) for (node, (x, y)) in nx.get_node_attributes(G, "pos").items()}
    nx.draw_networkx_labels(G, pos, labels=node_labels)
    edge_labels = nx.get_edge_attributes(G, "weight")
    nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=5)

    plt.axis("off")
    axis = plt.gca()
    axis.set_xlim([1.2 * x for x in axis.get_xlim()])
    axis.set_ylim([1.2 * y for y in axis.get_ylim()])
    # f = plt.figure()
    # f.set_figwidth(10)
    # f.set_figheight(10)
    # plt.subplots_adjust(left=0.0, right=4.0, bottom=0.0, top=4.0)
    if show:
        plt.show()

    plot_export = Plot_to_tex()
    plot_export.export_plot(plt, f"snn_{size}_{iteration}")
    # plt.savefig()
    plt.clf()
    plt.close()
