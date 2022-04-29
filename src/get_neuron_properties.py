from lava.proc.monitor.process import Monitor
from src.helper import get_neuron_from_dict

from src.networkx_to_snn import convert_networkx_graph_to_snn_with_one_neuron
from test.create_testobject import add_monitor_to_dict


def neuron_spikes_at_t(get_degree, t, node_name):
    # Initialise new a_in for a time step.

    # Compute whether the neuron spikes or not.
    if t == 0:
        # Create dictionary with int t as key and bool spike as value.

        # Neurons can only spike after being simulated for 1 timestep, so
        # initialise to False.
        spikes = False
    elif t == 1:
        # No spikes have come in yet at t=1, so a_in is 0. Compute
        # whether or not the neuron spikes based on its init properties.
        pass
    elif t > 1:
        # Get the incoming edges to the neuron.
        # Get the left/input neurons of the incoming edges.
        # Check if the input neuron spiked in the previous round (t-1)
        pass
        # If input neuron spiked, compute the synaptic/edge weight and add it to a_in

    # Store the spike in a dictionary with t as keys in the node.


def create_neuron_monitors(test_object, sim_time):
    get_degree = test_object.get_degree
    for node_name in get_degree.nodes:
        # The connecting node does not interact with the snn, it serves merely
        # to connect the snn for simulation purposes.
        if node_name != "connecting_node":
            neuron = get_neuron_from_dict(
                test_object.neuron_dict, test_object.neurons, node_name
            )
            if neuron is None:
                raise Exception(
                    "Error, was not able to find the neuron for node:{node_name}"
                )

            # Create monitor
            monitor = Monitor()

            # Specify what the monitor monitors, and for how long.
            monitor.probe(neuron.s_out, sim_time)

            # Get monitor process id
            monitor_process_id = list(monitor.get_data())[0]

            # Read out the boolean spike (at time t, with 1=1 being after 1 second of running.) or no spike with:
            # s_out=monitor.get_data()[monitor_process_id]["s_out"][t]
            # You need to call this again after every timestep.

            # Store monitor in node attribute.
            get_degree.nodes[node_name]["neuron"] = neuron
            get_degree.nodes[node_name]["spike_monitor"] = monitor
            get_degree.nodes[node_name]["spike_monitor_id"] = monitor_process_id
