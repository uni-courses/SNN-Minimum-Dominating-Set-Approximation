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


def create_graph_of_network_degree_computation(G):
    """
    TODO: verify that for node A, the neuron B (winner neuron)
    keeps spiking at t=101. If this is verified, connect to the next round.
    """
    print(f"Incoming G")
    plot_basic_graph(G)
    get_degree = get_degree_graph(G)
    print(f"Outputted get_degree")
    plot_unstructured_graph(get_degree)
    WTA_circuits = convert_get_degree_into_wta(G, get_degree)
    # for node in G.nodes:
    #    print(f"WTA_circuit[{node}]:")
    #    plot_unstructured_graph(WTA_circuits[node])
    # TODO: Then verify that for node A, the neuron B (winner neuron)
    # keeps spiking at t=101. If this is verified, connect to the next round.


def get_degree_graph(G):
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

        # One neuron per node named: degree_receiver_0-n.
        get_degree.add_node(
            f"degree_receiver_{node}",
            id=node,
            du=0,
            dv=1,
            bias=0,
            vth=1,
            pos=(float(1.0), float(node)),
        )

    # Then create all edges between the nodes.
    for node in G.nodes:
        # For each neighbour of node, named degree_receiver:
        for neighbour in nx.all_neighbors(G, node):

            get_degree.add_edges_from(
                [(f"spike_once_{node}", f"degree_receiver_{neighbour}")], weight=+1
            )
    return get_degree


def get_degree_graph_with_rand_nodes(G, rand_limit):
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

        # One neuron per node named: degree_receiver_0-n.
        get_degree.add_node(
            f"degree_receiver_{node}",
            id=node,
            du=0,
            dv=1,
            bias=0,
            vth=1,
            pos=(float(1.0), float(node)),
        )

        # One neuron per node named: rand
        if rand_limit < len(G):
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
            pos=(float(0.75), float(node) + 0.5),
        )

    # Then create all edges between the nodes.
    for node in G.nodes:
        # For each neighbour of node, named degree_receiver:
        for neighbour in nx.all_neighbors(G, node):

            get_degree.add_edges_from(
                [(f"spike_once_{node}", f"degree_receiver_{neighbour}")], weight=+1
            )

        # TODO: include random weight, instead of node weight.
        get_degree.add_edges_from(
            [(f"rand_{node}", f"degree_receiver_{node}")], weight=node
        )

    return get_degree


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

    # Then create all edges between the nodes.
    for circuit in G.nodes:
        # For each neighbour of node, named degree_receiver:
        for neighbour_a in G.nodes:
            if neighbour_a in nx.all_neighbors(G, circuit) or neighbour_a == circuit:
                for neighbour_b in nx.all_neighbors(G, circuit):
                    if circuit != neighbour_b and neighbour_a != neighbour_b:
                        # TODO: verify no duplicate synapses are created!
                        # print(
                        #    f"circuit={circuit},neighbour_a={neighbour_a},neighbour_b={neighbour_b}"
                        # )

                        get_degree.add_edges_from(
                            [
                                (
                                    f"spike_once_{circuit}",
                                    f"degree_receiver_{neighbour_a}_{neighbour_b}",
                                )
                            ],
                            weight=+1,
                        )
        for circuit_target in G.nodes:
            if circuit != circuit_target:
                # TODO: include random weight, instead of node weight.
                get_degree.add_edges_from(
                    [
                        (
                            f"rand_{circuit}",
                            f"degree_receiver_{circuit_target}_{circuit}",
                        )
                    ],
                    weight=rand_nrs[circuit]
                    # [(f"rand_{node}", f"degree_receiver_{neighbour_a}_{neighbour_b}")], weight=circuit
                )
                print(
                    f"Add edge between: circuit_target={circuit_target}, circuit={circuit},weight={rand_nrs[circuit]}"
                )

    return get_degree


def convert_get_degree_into_wta(G, get_degree):
    """
    Converts an incoming get_degree graph into a list of winner-take-all
    (WTA) circuits. One WTA circuit is spawned for each node. The WTA
    identifies which neuron has the highest degree using a rate-coding
    approach. The degree_receiver neuron that is still firing after some
    fixed number of timesteps, e.g. t=100, indicates which node has the
    highest number of neighbours.

    This method can compute the maximum weight as well as the maximum
    degree using the same mechanism. To convert to maximum weight
    computation, a random spiking neuron should be added as input to
    the degree_receiver neurons.

    For node A, a WTA circuit is built by letting each degree_receiver
    neighbour of A inhibit all other degree_receiver neighbours of A. This
    should give all neighbours a negative current. A new neuron named
    selector neuron is created that keeps spiking with +1 to all
    degree_receiver neurons, untill a single one spikes. This spike then
    inhibits and terminates the selector neuron. The degree_neighbour
    neuron should then keep on spiking, untill some fixed timeframe
    e.g. t=100 at which it will be read of as winner. This winner then
    represents the node that has the highest degree/weight.
    """
    # First add the degree inhibitions for each WTA circuit.
    WTA_circuits = add_degree_receiver_inhibitions(G, get_degree)

    # Then add the selector neuron for each WTA circuit
    for represented_node in G.nodes:
        WTA_circuits[represented_node] = add_selector_node_to_wta_circuit(
            G, WTA_circuits[represented_node], represented_node
        )
    return WTA_circuits


def add_degree_receiver_inhibitions(G, get_degree):
    WTA_circuits = []
    # For each Node A in graph G:
    for node in G.nodes:
        # Create a new WTA circuit.
        WTA_circuits.append(copy.deepcopy(get_degree))
        # Let each neighbour of A inhibt all other neighbours of A.
        #  For each neighbour X of node A:
        for neighbour_x in nx.all_neighbors(G, node):
            # For each neighbour Y of node A in X where X!=Y:
            for neighbour_y in nx.all_neighbors(G, node):
                # Prevent neighbours from inhibiting themselves.
                if neighbour_x != neighbour_y:
                    # Synapse from X to Y with weight -1.
                    WTA_circuits[node].add_edge(
                        f"degree_receiver_{neighbour_x}",
                        f"degree_receiver_{neighbour_y}",
                        weight=-1,
                    )
                    print(f"node={node},x={neighbour_x},y={neighbour_y}")
    return WTA_circuits


def add_selector_node_to_wta_circuit(G, WTA_circuit, represented_node):
    """Create a neuron Selector_A with threshold 1 (that keeps spiking and raising
    u of neighbour neurons untill the first one spikes. Stops spiking upon
    receiving the first spike.)."""

    # First add the selector node to the WTA circuit.
    WTA_circuit.add_node(
        f"selector_{represented_node}", id=represented_node, du=0, dv=0, bias=0
    )

    # For each degree receiver neighbour X of the represented node (e.g.
    # node A), create a synapse to the selector node of this WTA circuit.
    for neighbour_x in nx.all_neighbors(G, represented_node):
        #        Synapse from degree_receiver X to Selector_A
        WTA_circuit.add_edges_from(
            [(f"degree_receiver_{neighbour_x}", f"selector_{represented_node}")]
        )

    print(f"WTA_circuit,represented_node={represented_node}")
    plot_unstructured_graph(WTA_circuit)


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
