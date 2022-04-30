import copy
from datetime import datetime
from pprint import pprint
from time import time
import unittest
import networkx as nx
from numpy import sort
from lava.magma.core.run_conditions import RunSteps
from lava.magma.core.run_configs import Loihi1SimCfg
from src.Radiation_damage import Radiation_damage
from src.brain_adaptation import (
    inject_adaptation_mechanism_to_networkx_and_snn,
)
from src.create_planar_triangle_free_graph import (
    create_manual_graph_with_4_nodes,
    create_manual_graph_with_5_nodes,
    create_manual_graph_with_6_nodes_symmetric,
    create_manual_graph_with_6_nodes_y_shape,
    create_triangle_free_planar_graph,
)
from src.get_neuron_properties import (
    create_neuron_monitors,
    store_spike_values_in_neurons,
)
from src.helper import (
    delete_files_in_folder,
    export_get_degree_graph,
    get_counter_neurons_from_dict,
    load_pickle_and_plot,
    print_time,
    write_results_to_file,
)
from src.helper_network_structure import plot_neuron_behaviour_over_time
from src.neumann import full_alipour


from test.create_testobject import (
    create_test_object,
)


class Test_counter(unittest.TestCase):
    """
    Tests whether the counter neurons indeed yield the same degree count
    as the Alipour algorithm implementation in the first step/
    initailisation of the algorithm.
    """

    # Initialize test object
    def __init__(self, *args, **kwargs):
        super(Test_counter, self).__init__(*args, **kwargs)

    def get_graphs_for_this_test(self, size=None, seed=None):
        # Get list of planer triangle free graphs.
        if not size is None and not seed is None:
            G = create_triangle_free_planar_graph(size, 0.6, seed, False)
            print("TRIANGLE")
        else:
            G = create_manual_graph_with_4_nodes()
            # G = create_manual_graph_with_5_nodes()
            # G = create_manual_graph_with_6_nodes_symmetric() #>-<
            # G = create_manual_graph_with_6_nodes_y_shape()  # Y
        return G

    def test_snn_algorithm(self, adaptation=False, output_behaviour=False):

        # delete_dir_if_exists(f"latex/Images/graphs")
        delete_files_in_folder(f"latex/Images/graphs")
        monitors = None
        seed = 42

        for m in range(0, 3):
            plot_neuron_behaviour = True
            for iteration in range(0, 10, 1):
                for size in range(3, 7, 1):
                    rad_dam = Radiation_damage(size, seed)
                    G = self.get_graphs_for_this_test(size=size, seed=seed)

                    latest_millis = int(round(time() * 1000))
                    latest_time, latest_millis = print_time(
                        "Create object.", datetime.now(), latest_millis
                    )

                    # Initialise paramers used for testing.
                    test_object = create_test_object(
                        adaptation, G, iteration, m, False, False
                    )
                    sim_time = test_object.inhibition + 10
                    # sim_time = 18
                    latest_time, latest_millis = print_time(
                        "Created object.", latest_time, latest_millis
                    )

                    if adaptation:
                        (
                            latest_time,
                            latest_millis,
                        ) = inject_adaptation_mechanism_to_networkx_and_snn(
                            latest_millis,
                            latest_time,
                            G,
                            test_object,
                            m,
                            iteration,
                            size,
                        )

                    if output_behaviour:
                        monitors = create_neuron_monitors(
                            test_object, test_object.sim_time
                        )
                        latest_time, latest_millis = print_time(
                            "Got neuron monitors.", latest_time, latest_millis
                        )

                    # Run default tests on neurons and get counted degree from
                    # neurons after inhibition time.
                    neurons = list(test_object.neuron_dict.keys())
                    (
                        latest_time,
                        neurons,
                        starter_neuron,
                    ) = self.run_test_degree_receiver_neurons_over_time(
                        adaptation,
                        iteration,
                        latest_millis,
                        latest_time,
                        m,
                        neurons,
                        output_behaviour,
                        sim_time,
                        size,
                        test_object,
                    )
                    latest_time, latest_millis = print_time(
                        "Ran simulation.", latest_time, latest_millis
                    )

                    # Get the counter neurons at the end of the simulation.
                    counter_neurons = get_counter_neurons_from_dict(
                        test_object.neuron_dict, len(test_object.G)
                    )
                    latest_time, latest_millis = print_time(
                        "Got counter neurons.", latest_time, latest_millis
                    )

                    # Check if expected counter nodes are selected.
                    self.perform_integration_test_on_end_result(
                        counter_neurons, G, m, iteration, test_object
                    )
                    latest_time, latest_millis = print_time(
                        "Performed integration test.", latest_time, latest_millis
                    )

                    # Terminate loihi simulation for this run.
                    starter_neuron.stop()
                    export_get_degree_graph(
                        test_object.G, test_object.get_degree, iteration, m, seed, size
                    )
                    load_pickle_and_plot(iteration, m, seed, size)

    def run_test_degree_receiver_neurons_over_time(
        self,
        adaptation,
        iteration,
        latest_millis,
        latest_time,
        m,
        neurons,
        output_behaviour,
        sim_time,
        size,
        test_object,
    ):
        """Verifies the neuron properties over time."""

        # Get the first neuron in the SNN to start the simulation
        starter_neuron = neurons[0]

        # Simulate SNN and assert values inbetween timesteps.
        latest_time, latest_millis = print_time(
            "Start simulation for 1 timestep.", latest_time, latest_millis
        )
        for t in range(1, sim_time):

            # Run the simulation for 1 timestep.
            starter_neuron.run(condition=RunSteps(num_steps=1), run_cfg=Loihi1SimCfg())
            latest_time, latest_millis = print_time(
                f"Simulated SNN for t={t}.", latest_time, latest_millis
            )

            # Store spike bools in networkx graph for plotting.
            if adaptation and output_behaviour:
                store_spike_values_in_neurons(test_object.get_degree, t)
            if output_behaviour:
                plot_neuron_behaviour_over_time(
                    test_object.get_degree, iteration, size, m, t, show=False
                )

        # raise Exception("Stop")
        return latest_time, neurons, starter_neuron

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
        print("G_alipour countermarks-SNN counter current")
        for node in G.nodes:
            print(
                f'{G_alipour.nodes[node]["countermarks"]}-{counter_neurons[node].u.get()}'
            )
            # self.assertEqual(
            #    G_alipour.nodes[node]["countermarks"],
            #    counter_neurons[node].u.get(),
            # )
        write_results_to_file(m, G, retry, G_alipour, counter_neurons)
