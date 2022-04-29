import copy
from src.helper_network_structure import plot_coordinated_graph


def implement_adaptation_mechanism(G, get_degree, m, retry, size, test_object):
    original_nodes = copy.deepcopy(get_degree.nodes)
    for node_name in original_nodes:
        # Get input synapses as dictionaries, one per node, store as node attribute.
        store_input_synapses(get_degree, node_name)

        # Get output synapses as dictionaries, one per node, store as node attribute.
        store_output_synapses(get_degree, node_name)

        # Create redundant neurons.
        # TODO: specify position.
        get_degree.add_nodes_from([f"red_{node_name}"])

    # Start new loop before adding edges, because all reduundant neurons need
    # to exist before creating synapses.
    for node_name in original_nodes:
        # Add input synapses to redundant node.
        add_input_synapses(get_degree, node_name)

        # Add output synapses  to redundant node.
        add_output_synapses(get_degree, node_name)

        # Add inhibitory synapse from node to redundant node.
        add_inhibitory_synapse(get_degree, node_name)

        # Add recurrent self inhibitory synapse for some redundant nodes.

    # Visualise new graph.
    plot_coordinated_graph(get_degree, retry, size, show=True)
    raise Exception("STOP")
    return get_degree


def store_input_synapses(G, node_name):
    input_edges = []
    for edge in G.edges:
        if edge[1] == node_name:
            input_edges.append(edge)
    G.nodes[node_name]["input_edges"] = input_edges


def store_output_synapses(G, node_name):
    output_edges = []
    for edge in G.edges:
        if edge[0] == node_name:
            output_edges.append(edge)
    G.nodes[node_name]["output_edges"] = output_edges


def add_input_synapses(get_degree, node_name):
    get_degree.add_edges_from(get_degree.nodes[node_name]["input_edges"])
    # TODO: set edge weight


def add_output_synapses(get_degree, node_name):
    get_degree.add_edges_from(get_degree.nodes[node_name]["output_edges"])
    # TODO: set edge weight


def add_inhibitory_synapse(get_degree, node_name):
    get_degree.add_edges_from([(node_name, f"red_{node_name}")])
    # TODO: set edge weight
