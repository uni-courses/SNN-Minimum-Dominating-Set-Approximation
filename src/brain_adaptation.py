import copy
from src.helper import print_time
from src.helper_network_structure import plot_coordinated_graph
from src.networkx_to_snn import convert_networkx_graph_to_snn_with_one_neuron
from test.create_testobject import add_monitor_to_dict


def inject_adaptation_mechanism_to_networkx_and_snn(
    G,
    iteration,
    latest_millis,
    latest_time,
    m,
    rad_dam,
    size,
    test_object,
):
    # Implement brain adaptation on networkx graph.
    implement_adaptation_mechanism(
        G, test_object.get_degree, iteration, m, rad_dam, size, test_object
    )
    latest_time, latest_millis = print_time(
        f"Get adapted networkx Graph.", latest_time, latest_millis
    )

    # Convert the graph with brain adaptation to an SNN.
    test_object = convert_new_graph_to_snn(test_object)
    latest_time, latest_millis = print_time(
        f"Got adapted SNN.", latest_time, latest_millis
    )
    return latest_time, latest_millis


def implement_adaptation_mechanism(
    G, get_degree, iteration, m, rad_dam, size, test_object
):
    d = 0.25 * (
        m + 1
    )  # Hardcoded duplicate of d in get_degree_graph_with_separate_wta_circuits.
    original_nodes = copy.deepcopy(get_degree.nodes)

    for node_name in original_nodes:
        # Get input synapses as dictionaries, one per node, store as node attribute.
        store_input_synapses(get_degree, node_name)

        # Get output synapses as dictionaries, one per node, store as node attribute.
        store_output_synapses(get_degree, node_name)

        # Create redundant neurons.
        create_redundant_node(d, get_degree, node_name)

    # Start new loop before adding edges, because all reduundant neurons need
    # to exist before creating synapses.
    for node_name in original_nodes:
        # Add input synapses to redundant node.
        add_input_synapses(get_degree, node_name)

        # Add output synapses  to redundant node.
        add_output_synapses(get_degree, node_name)

        # Add inhibitory synapse from node to redundant node.
        # TODO: set edge weight
        add_inhibitory_synapse(get_degree, node_name)

        # Add recurrent self inhibitory synapse for some redundant nodes.

    # Inject radiation
    inject_radiation(get_degree, rad_dam)

    # Visualise new graph.
    plot_coordinated_graph(get_degree, iteration, size, show=False)
    return get_degree


def store_input_synapses(get_degree, node_name):
    input_edges = []
    for edge in get_degree.edges:
        if edge[1] == node_name:
            input_edges.append(edge)
    get_degree.nodes[node_name]["input_edges"] = input_edges


def store_output_synapses(get_degree, node_name):
    output_edges = []
    for edge in get_degree.edges:
        if edge[0] == node_name:
            output_edges.append(edge)
    get_degree.nodes[node_name]["output_edges"] = output_edges


def create_redundant_node(d, get_degree, node_name):
    """Create neuron and set coordinate position."""
    vth = compute_vth_for_delay(get_degree, node_name)
    get_degree.add_node(
        f"red_{node_name}",
        du=get_degree.nodes[node_name]["du"],
        dv=get_degree.nodes[node_name]["dv"],
        bias=get_degree.nodes[node_name]["bias"],
        vth=vth,
        pos=(
            float(get_degree.nodes[node_name]["pos"][0] + 0.25 * d),
            float(get_degree.nodes[node_name]["pos"][1] - 0.25 * d),
        ),
        spike={},
        is_redundant=True,
    )


def compute_vth_for_delay(get_degree, node_name):
    """Increases vth with 1 to realise a delay of t=1 for
    the redunant spike_once neurons, rand neurons and selector neurons.
    Returns dv of default node otherwise."""
    if (
        node_name[:11] == "spike_once_"
        or node_name[:5] == "rand_"
        or node_name[:9] == "selector_"
        or node_name[:16] == "degree_receiver_"
    ):
        vth = get_degree.nodes[node_name]["vth"] + 1
        if node_name == "spike_once_0":
            vth = 9999
    else:
        vth = get_degree.nodes[node_name]["vth"]
    return vth


def add_input_synapses(get_degree, node_name):
    for edge in get_degree.nodes[node_name]["input_edges"]:
        # Compute set edge weight
        left_node = edge[0]
        right_node = f"red_{node_name}"
        weight = get_degree[edge[0]][edge[1]]["weight"]

        # Create edge
        get_degree.add_edge(left_node, right_node, weight=weight, is_redundant=True)


def add_output_synapses(get_degree, node_name):
    get_degree.add_edges_from(get_degree.nodes[node_name]["output_edges"])
    for edge in get_degree.nodes[node_name]["output_edges"]:
        # Compute set edge weight
        left_node = f"red_{node_name}"
        right_node = edge[1]
        weight = get_degree[edge[0]][edge[1]]["weight"]

        # Create edge
        get_degree.add_edge(left_node, right_node, weight=weight, is_redundant=True)


def add_inhibitory_synapse(get_degree, node_name):
    # TODO: compute what minimum inhibitory weight should be in network to
    # prevent all neurons from spiking.
    get_degree.add_edges_from([(node_name, f"red_{node_name}")], weight=-100)
    # TODO: set edge weight


def convert_new_graph_to_snn(test_object):
    ## Convert the snn networkx graph into a Loihi implementation.
    (
        test_object.converted_nodes,
        test_object.lhs_neuron,
        test_object.neurons,
        test_object.lhs_node,
        test_object.neuron_dict,
    ) = convert_networkx_graph_to_snn_with_one_neuron(test_object.get_degree)

    # Create monitor dict
    test_object.monitor_dict = {}
    for neuron in test_object.neurons:
        test_object.monitor_dict = add_monitor_to_dict(
            neuron, test_object.monitor_dict, test_object.sim_time
        )
    return test_object
