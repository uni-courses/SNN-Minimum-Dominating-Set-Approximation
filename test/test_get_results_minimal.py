import copy
from datetime import datetime
from pprint import pprint
import unittest
import networkx as nx
from numpy import sort
from lava.magma.core.run_conditions import RunSteps
from lava.magma.core.run_configs import Loihi1SimCfg
from src.brain_adaptation import (
    convert_new_graph_to_snn,
    implement_adaptation_mechanism,
)
from src.create_planar_triangle_free_graph import (
    create_manual_graph_with_4_nodes,
    create_manual_graph_with_5_nodes,
    create_manual_graph_with_6_nodes_symmetric,
    create_manual_graph_with_6_nodes_y_shape,
    create_triangle_free_planar_graph,
)
from src.get_neuron_properties import create_neuron_monitors
from src.helper import (
    degree_receiver_x_y_is_connected_to_counter_z,
    delete_files_in_folder,
    get_a_in_for_degree_receiver,
    get_counter_neurons_from_dict,
    get_degree_reciever_neurons_per_wta_circuit,
    get_grouped_neurons,
    get_wta_circuit_from_neuron_name,
    get_y_from_degree_receiver_x_y,
    print_neuron_behaviour,
    print_time,
    write_results_to_file,
)
from src.helper_network_structure import get_node_names, plot_neuron_behaviour_over_time
from src.neumann import full_alipour


from test.create_testobject import (
    create_test_object,
    get_counter_previous_property_dicts,
    get_degree_receiver_previous_property_dicts,
    get_selector_previous_property_dicts,
)
from test.helper_tests import perform_generic_neuron_property_asserts


class Test_counter(unittest.TestCase):
    """
    Tests whether the counter neurons indeed yield the same degree count
    as the Alipour algorithm implementation in the first step/
    initailisation of the algorithm.
    """

    # Initialize test object
    def __init__(self, *args, **kwargs):
        super(Test_counter, self).__init__(*args, **kwargs)

    def get_graphs_for_this_test(self, size=None, random=None):
        # Get list of planer triangle free graphs.
        if not size is None and not random is None:
            G = create_triangle_free_planar_graph(size, 0.6, 42, False)
            print("TRIANGLE")
        else:
            G = create_manual_graph_with_4_nodes()
            # G = create_manual_graph_with_5_nodes()
            # G = create_manual_graph_with_6_nodes_symmetric() #>-<
            # G = create_manual_graph_with_6_nodes_y_shape()  # Y
        return G

    def test_multiple_tests(self):

        # delete_dir_if_exists(f"latex/Images/graphs")
        delete_files_in_folder(f"latex/Images/graphs")

        for m in range(1, 2):
            plot_neuron_behaviour = True
            for retry in range(0, 1, 1):
                for size in range(5, 6, 1):
                    G = self.get_graphs_for_this_test(size=None, random=None)

                    latest_time = print_time("Create object.", datetime.now().time())
                    # Initialise paramers used for testing.
                    test_object = create_test_object(G, retry, m, False, False)
                    # sim_time=test_object.inhibition + 1
                    sim_time = 2
                    latest_time = print_time("Created object.", latest_time)

                    # Implement brain adaptation
                    ###implement_adaptation_mechanism(
                    ###    G, test_object.get_degree, m, retry, size, test_object
                    ###)
                    # latest_time = print_time("Get adapted networkx Graph.", latest_time)

                    # Create monitors to probe if neuron spiked or not.
                    ##test_object = convert_new_graph_to_snn(test_object)
                    # latest_time = print_time("Got adapted SNN.", latest_time)
                    # raise Exception("DONE")
                    # monitors = create_neuron_monitors(test_object, test_object.sim_time)
                    # latest_time = print_time("Got neuron monitors.", latest_time)
                    # raise Exception("STOP")

                    # Run default tests on neurons and get counted degree from
                    # neurons after inhibition time.
                    (
                        starter_neuron,
                        neurons,
                    ) = self.run_test_degree_receiver_neurons_over_time(
                        neurons,
                        sim_time,
                    )
                    latest_time = print_time("Ran simulation.", latest_time)

                    # Get the counter neurons at the end of the simulation.
                    counter_neurons = get_counter_neurons_from_dict(
                        test_object.neuron_dict, len(test_object.G)
                    )
                    latest_time = print_time("Got counter neurons.", latest_time)

                    # Check if expected counter nodes are selected.
                    self.perform_integration_test_on_end_result(
                        counter_neurons, G, m, retry, test_object
                    )
                    latest_time = print_time("Performed integration test.", latest_time)

                    # Terminate loihi simulation for this run.
                    starter_neuron.stop()

    def run_test_degree_receiver_neurons_over_time(self, neurons, sim_time):
        """Verifies the neuron properties over time."""

        # Get the first neuron in the SNN to start the simulation
        starter_neuron = neurons[0]

        # Simulate SNN and assert values inbetween timesteps.
        # Simulate till extraction time+10 sec.
        for t in range(1, sim_time):

            latest_time = print_time("Start simulation for 1 timestep.", latest_time)
            # Run the simulation for 1 timestep.
            starter_neuron.run(condition=RunSteps(num_steps=1), run_cfg=Loihi1SimCfg())
            latest_time = print_time(f"Simulated SNN for t={t}.", latest_time)

        # raise Exception("Stop")
        return starter_neuron, neurons

    def perform_integration_test_on_end_result(
        self, counter_neurons, G, m, retry, test_object
    ):
        """Tests whether the SNN returns the same results as the Alipour algorithm."""
        # Compute the Alipour graph.
        G_alipour = full_alipour(
            test_object.delta,
            test_object.inhibition,
            G,
            test_object.rand_ceil,
            test_object.rand_nrs,
            test_object.m,
        )

        # Compare the counts per node and assert they are equal.
        for node in G.nodes:
            print(
                "G_alipour countermarks",
                G_alipour.nodes[node]["countermarks"],
            )
            print("SNN counter current", counter_neurons[node].u.get())
            self.assertEqual(
                G_alipour.nodes[node]["countermarks"],
                counter_neurons[node].u.get(),
            )
        write_results_to_file(m, G, retry, G_alipour, counter_neurons)
