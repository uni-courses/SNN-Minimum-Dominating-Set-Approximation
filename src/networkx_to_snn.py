# Start by reading the TODO's.
import networkx as nx

# Instantiate Lava processes to build network
from lava.proc.dense.process import Dense
from lava.proc.lif.process import LIF
from src.helper import add_neuron_to_dict
from src.helper_network_structure import plot_coordinated_graph
from src.helper_snns import (
    connect_synapse,
    connect_synapse_left_to_right,
    connect_synapse_right_to_left,
    create_weighted_synapse,
)


def convert_networkx_graph_to_snn_with_one_neuron(G):
    # TODO: rewrite function to:
    # 0. Verify the graph is connected (no lose nodes exist).
    # 1. Start with first incoming node.
    first_node = list(G.nodes)[0]
    # print(f"G.nodes[0]={list(G.nodes)[0]}")
    # converted_nodes, lhs_neuron, neurons, lhs_node = build_snn(G, [], [], first_node)

    # Append dictionary as property to G.
    # G = nx.Graph(neuron_dict={})
    neuron_dict = {}
    # G.graph['neuron_dict']["something"]=3
    # print(f'something in dict={G.graph["neuron_dict"]["something"]} is 3')
    # exit()

    (
        converted_nodes,
        lhs_neuron,
        neurons,
        lhs_node,
        neuron_dict,
        visited_nodes,
    ) = retry_build_snn(G, [], [], first_node, [], neuron_dict)

    # 5. Create a verification that checks that all neurons in the incoming
    # graph are created.
    # 6. Create a verification that checks that all synapses in the incoming
    # graph are created.
    return converted_nodes, lhs_neuron, neurons, lhs_node, neuron_dict


def retry_build_snn(
    G, converted_nodes, neurons, lhs_node, visited_nodes, neuron_dict={}
):
    # Verify prerequisites
    # print_node_properties(G, lhs_node)
    assert_all_neuron_properties_are_specified(G, lhs_node)
    # TODO: assert graph G is connected.

    visited_nodes.append(lhs_node)

    # Incoming node, if it is not yet converted, then convert to neuron.
    if not node_is_converted(G, converted_nodes, neurons, lhs_node):
        converted_nodes, lhs_neuron, neurons, lhs_node = create_neuron_from_node(
            G, converted_nodes, neurons, lhs_node
        )
    else:
        lhs_neuron = get_neuron_belonging_to_node_from_list(
            neurons, lhs_node, converted_nodes
        )

    # For all edges of node, if synapse does not yet  exists:
    # Needs to be a set  because bi-directional edges create neighbour duplicates.
    for neighbour in set(nx.all_neighbors(G, lhs_node)):
        if neighbour not in visited_nodes:

            # Ensure target neuron is created.
            if not node_is_converted(G, converted_nodes, neurons, neighbour):
                (
                    converted_nodes,
                    rhs_neuron,
                    neurons,
                    rhs_node,
                ) = create_neuron_from_node(G, converted_nodes, neurons, neighbour)
            else:
                lhs_neuron = get_neuron_belonging_to_node_from_list(
                    neurons, lhs_node, converted_nodes
                )
                rhs_neuron = get_neuron_belonging_to_node_from_list(
                    neurons, neighbour, converted_nodes
                )

            # Create a neuron dictionary which returns the node name if you input a neuron.
            # print(f"lhs_node={lhs_node},neighbour={neighbour},rhs_neuron={rhs_neuron}")
            neuron_dict = add_neuron_to_dict(neighbour, neuron_dict, rhs_neuron)

            # 5. Add synapse
            # print(
            #    f"add_synapse from:{lhs_node},with neighbour={neighbour}, connect to to: {neuron_dict[rhs_neuron]}"
            # )
            lhs_neuron = add_synapse_between_nodes(
                G, lhs_neuron, lhs_node, neighbour, rhs_neuron, neighbour
            )
        if len(visited_nodes) == 1:
            # print(f'ADD{lhs_node}')
            neuron_dict = add_neuron_to_dict(lhs_node, neuron_dict, lhs_neuron)

    # 6. recursively call that function on the neighbour neurons until no
    # new neurons are discovered.
    for neighbour in nx.all_neighbors(G, lhs_node):
        if neighbour not in visited_nodes:
            if neighbour not in visited_nodes:
                (
                    converted_nodes,
                    discarded_neuron,
                    neurons,
                    discarded_node,
                    neuron_dict,
                    visited_nodes,  # TODO: determine if this should be elimintated.
                ) = retry_build_snn(
                    G, converted_nodes, neurons, neighbour, visited_nodes, neuron_dict
                )
    return converted_nodes, lhs_neuron, neurons, lhs_node, neuron_dict, visited_nodes


def get_neuron_belonging_to_node_from_list(neurons, node, nodes):
    index = nodes.index(node)
    return neurons[index]


def get_node_belonging_to_neuron_from_list(neuron, neurons, nodes):
    index = neurons.index(neuron)
    return nodes[index]


def get_edge_if_exists(G, lhs_node, rhs_node):
    """Returns the edge object if the graph G has an edge between the two
    nodes. Returns None otherwise."""
    if G.has_edge(lhs_node, rhs_node):
        for edge in G.edges:
            if edge == (lhs_node, rhs_node):
                # print_edge_properties(G, edge)
                return edge
        # Verify at least an edge the other way round exists.
        if not G.has_edge(rhs_node, lhs_node):
            raise Exception(
                "Would expect an edge between a node and its neighbour in the other direction."
            )
    # Verify at least an edge the other way round exists.
    if not G.has_edge(rhs_node, lhs_node):
        raise Exception(
            "Would expect an edge between a node and its neighbour in the other direction."
        )


def create_neuron_from_node(G, converted_nodes, neurons, node):

    bias, du, dv, vth = get_neuron_properties(G, node)

    neuron = LIF(bias=bias, du=du, dv=dv, vth=vth)

    # If spike_once_neuron, create recurrent synapse
    if node[0:11] == "spike_once_" or node[0:5] == "rand_":
        neuron = create_recurrent_synapse(neuron, -2)
    if node[0:15] == "red_spike_once_" or node[0:9] == "red_rand_":
        neuron = create_recurrent_synapse(neuron, -2)

    if node[0:16] == "degree_receiver_" or node[0:20] == "red_degree_receiver_":
        neuron = create_recurrent_synapse(neuron, -20)
    # if node[0:6] == "count_":
    #    neuron = create_recurrent_synapse(neuron, -1)
    if node[0:6] == "delay_" or node[0:10] == "red_delay_":
        neuron = create_recurrent_synapse(neuron, -(len(G) * 2 - 1) - 2)  # TODO: or -1?

    neurons.append(neuron)
    converted_nodes.append(node)
    return converted_nodes, neuron, neurons, node


def create_recurrent_synapse(neuron, weight):
    dense = create_weighted_synapse(weight)

    # Connect neuron to itself.
    neuron = connect_synapse(neuron, neuron, dense)
    return neuron


def node_is_converted(G, converted_nodes, neurons, node):
    """Verifies that the incoming node is not converted into
    a neuron yet."""
    return node in converted_nodes


def print_node_properties(G, node):
    # Dictionary with node attributes and values.
    print(f"key value pairs of node:{node} are: {G.nodes[node]}")
    # value of attribute du of node
    print(f'Value of attribute:"du" of node:{node} is:{G.nodes[node]["du"]}')


def print_edge_properties(G, edge):
    # Dictionary with edge attributes and values.
    print(f"key value pairs of edge:{edge} are: {G.edges[edge]}")
    # value of attribute du of edge
    print(f'Value of attribute:"weight" of edge:{edge} is:{G.edges[edge]["weight"]}')


def assert_all_neuron_properties_are_specified(G, node):
    if not all_neuron_properties_are_specified(G, node):
        raise Exception(
            f"Not all neuron prpoerties of node: {node} are"
            + f" specified. It only contains attributes:{get_neuron_property_names(G,node)}"
        )


def all_neuron_properties_are_specified(G, node):
    neuron_property_names = get_neuron_property_names(G, node)
    # if ['bias', 'du', 'dv','vth'] in neuron_properties:
    if "bias" in neuron_property_names:
        if "du" in neuron_property_names:
            if "dv" in neuron_property_names:
                if "vth" in neuron_property_names:
                    return True
    return False


def get_neuron_property_names(G, node):
    return G.nodes[node].keys()


def get_neuron_properties(G, node):
    bias = G.nodes[node]["bias"]
    du = G.nodes[node]["du"]
    dv = G.nodes[node]["dv"]
    vth = G.nodes[node]["vth"]
    return bias, du, dv, vth


def assert_all_synapse_properties_are_specified(G, edge):
    if not all_synapse_properties_are_specified(G, edge):
        raise Exception(
            f"Not all synapse prpoerties of edge: {edge} are"
            + f" specified. It only contains attributes:{get_synapse_property_names(G,edge)}"
        )


def all_synapse_properties_are_specified(G, edge):
    synapse_property_names = get_synapse_property_names(G, edge)
    if "weight" in synapse_property_names:
        # if 'delay' in synapse_property_names:
        # TODO: implement delay using a chain of neurons in series since this
        # is not yet supported by lava-nc.
        return True
    return False


def get_synapse_property_names(G, edge):
    return G.edges[edge].keys()


def get_synapse_properties(G, edge):
    weight = G.edges[edge]["weight"]
    # TODO: implement delay using a chain of neurons in series since this
    # is not yet supported by lava-nc.
    # delay=G.edges[edge]['delay']
    return weight


def add_synapse_between_nodes(G, lhs_neuron, lhs_node, neighbour, rhs_neuron, rhs_node):
    # TODO: ensure the synapses are created in both directions.
    lhs_neuron = add_synapse_left_to_right(
        G, lhs_neuron, lhs_node, neighbour, rhs_neuron, rhs_node
    )
    lhs_neuron = add_synapse_right_to_left(
        G, lhs_neuron, lhs_node, neighbour, rhs_neuron, rhs_node
    )
    return lhs_neuron


def add_synapse_left_to_right(G, lhs_neuron, lhs_node, neighbour, rhs_neuron, rhs_node):
    # 3. Get the edge between lhs and rhs nodes. They are neighbours
    # so they have an edge by definition.However it is a directed graph.
    edge = get_edge_if_exists(G, lhs_node, neighbour)

    if not edge is None:
        # 3. Assert the synapses are fully specified.
        assert_all_synapse_properties_are_specified(G, edge)

        # 4. Create synapse between incoming node and neighbour.
        dense = create_weighted_synapse(G.edges[edge]["weight"])

        # 5. Connect neurons using created synapse.
        # TODO: write function that checks if synapse is created or not.
        lhs_neuron = connect_synapse_left_to_right(lhs_neuron, rhs_neuron, dense)
        # print(
        #   f'connecting: lhs_node={lhs_node} to:rhs_node={rhs_node} with weight:{G.edges[edge]["weight"]}\n'
        # )
    return lhs_neuron


def add_synapse_right_to_left(G, lhs_neuron, lhs_node, neighbour, rhs_neuron, rhs_node):
    # 3. Get the edge between lhs and rhs nodes. They are neighbours
    # so they have an edge by definition.However it is a directed graph.
    edge = get_edge_if_exists(G, neighbour, lhs_node)

    if not edge is None:
        # 3. Assert the synapses are fully specified.
        assert_all_synapse_properties_are_specified(G, edge)

        # 4. Create synapse between incoming node and neighbour.
        dense = create_weighted_synapse(G.edges[edge]["weight"])

        # 5. Connect neurons using created synapse.
        # TODO: write function that checks if synapse is created or not.
        lhs_neuron = connect_synapse_right_to_left(lhs_neuron, rhs_neuron, dense)
        # print(
        #   f'connecting:rhs_node={rhs_node} to:  lhs_node={lhs_node} with weight:{G.edges[edge]["weight"]}\n'
        # )
    return lhs_neuron
