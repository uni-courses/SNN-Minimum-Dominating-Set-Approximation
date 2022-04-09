# Start by reading the TODO's.
import networkx as nx

# Instantiate Lava processes to build network
from lava.proc.dense.process import Dense
from lava.proc.lif.process import LIF
from src.helper_snns import connect_synapse, create_weighted_synapse


def convert_networkx_graph_to_snn(G, full_spec, bias=0, du=0, dv=0, weight=1, vth=1):
    """Converts an incoming graph into a spiking neural network for lava-nc.
    Input arguments are the default values if they are not specified.
    Throws error if full spec is required whilst one argument is missing.
    """
    neurons = []
    for node in G.nodes:
        print_node_properties(G, node)
        assert_all_neuron_properties_are_specified(G, node)
        bias, du, dv, vth = get_neuron_properties(G, node)
        neuron = LIF(bias=bias, du=du, dv=dv, vth=vth)
        neurons.append(neuron)

    # TODO: rewrite function to:
    # 0. start with first incoming neuron,
    # 1. Then get all edges of that neuron.
    # 2. Create all the neighbour neurons.
    # 3. recursively call that function on the neighbour neurons untill no
    # new neurons are discovered.
    # 4. Then return the first neuron.
    # 5. Create a verification that checks that all neurons in the incoming
    # graph are created.
    # 6. Create a verification that checks that all synapses in the incoming
    # graph are created.
    for edge in G.edges:
        print_edge_properties(G, edge)
        assert_all_synapse_properties_are_specified
        # TODO: change this from the graph node to the neuron.
        lhs_neuron = G.nodes[edge[0]]
        rhs_neuron = G.nodes[edge[1]]
        # Create synapse
        dense = create_weighted_synapse(lhs_neuron, rhs_neuron, G.edges[edge]["weight"])
        # Connect neurons using created synapse.
        neurons = connect_synapse(lhs_neuron, rhs_neuron, dense)
    raise Exception("Stop")


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
