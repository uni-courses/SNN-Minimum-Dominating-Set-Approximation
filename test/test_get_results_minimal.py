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
            # G = create_manual_graph_with_4_nodes()
            G = create_manual_graph_with_5_nodes()
            # G = create_manual_graph_with_6_nodes_symmetric() #>-<
            # G = create_manual_graph_with_6_nodes_y_shape()  # Y
        return G

    def test_snn_algorithm(self, adaptation=True, output_behaviour=True):

        # delete_dir_if_exists(f"latex/Images/graphs")
        delete_files_in_folder(f"latex/Images/graphs")
        monitors = None
        seed = 42

        for m in range(0, 1):
            plot_neuron_behaviour = True
            for iteration in range(0, 1, 1):
                for size in range(3, 4, 1):
                    rad_dam = Radiation_damage(size, seed, True)
                    G = self.get_graphs_for_this_test(size=size, seed=seed)
                    for adaptation in [False, True]:

                        # Start performance report.
                        latest_millis = int(round(time() * 1000))
                        latest_time, latest_millis = print_time(
                            "Create object.", datetime.now(), latest_millis
                        )

                        # Initialise paramers used for testing.
                        test_object = create_test_object(
                            adaptation, G, iteration, m, False, False
                        )

                        # Show alipour
                        # Compute the Alipour graph.
                        G_alipour = full_alipour(
                            test_object.delta,
                            test_object.inhibition,
                            iteration,
                            G,
                            test_object.rand_ceil,
                            test_object.rand_nrs,
                            test_object.m,
                            seed,
                            len(test_object.G),
                            export=True,
                        )

                        # Specify simulation duration.
                        sim_time = test_object.inhibition * (m + 1) + 10
                        # sim_time = 2

                        # Report performance.
                        latest_time, latest_millis = print_time(
                            "Created object.", latest_time, latest_millis
                        )

                        # Apply simulated brain adaptation to networkx graph and SNN, if desired.
                        if adaptation:
                            (
                                latest_time,
                                latest_millis,
                            ) = inject_adaptation_mechanism_to_networkx_and_snn(
                                G,
                                iteration,
                                latest_millis,
                                latest_time,
                                m,
                                rad_dam,
                                sim_time,
                                size,
                                test_object,
                            )

                        # Add spike monitors in networkx graph representing SNN.
                        # if output_behaviour:
                        create_neuron_monitors(test_object, sim_time)
                        # Report performance.
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
                            seed,
                            sim_time,
                            size,
                            test_object,
                        )

                        # Report performance.
                        latest_time, latest_millis = print_time(
                            "Ran simulation.", latest_time, latest_millis
                        )

                        # Get the counter neurons at the end of the simulation.
                        counter_neurons = get_counter_neurons_from_dict(
                            len(test_object.G), test_object.neuron_dict, m
                        )
                        latest_time, latest_millis = print_time(
                            "Got counter neurons.", latest_time, latest_millis
                        )

                        # Terminate loihi simulation for this run.
                        export_get_degree_graph(
                            adaptation,
                            test_object.G,
                            test_object.get_degree,
                            iteration,
                            m,
                            seed,
                            size,
                        )
                        # load_pickle_and_plot(adaptation, iteration, m, seed, sim_time, size)

                        # Check if expected counter nodes are selected.
                        self.perform_integration_test_on_end_result(
                            counter_neurons,
                            G,
                            iteration,
                            m,
                            iteration,
                            seed,
                            test_object,
                        )
                        latest_time, latest_millis = print_time(
                            "Performed integration test.", latest_time, latest_millis
                        )
                        starter_neuron.stop()

    def run_test_degree_receiver_neurons_over_time(
        self,
        adaptation,
        iteration,
        latest_millis,
        latest_time,
        m,
        neurons,
        output_behaviour,
        seed,
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

            if output_behaviour:
                # Store spike bools in networkx graph for plotting.
                store_spike_values_in_neurons(test_object.get_degree, t)
                plot_neuron_behaviour_over_time(
                    adaptation,
                    test_object.get_degree,
                    iteration,
                    seed,
                    size,
                    m,
                    t,
                    show=False,
                    current=True,
                )

        # raise Exception("Stop")
        return latest_time, neurons, starter_neuron

    def perform_integration_test_on_end_result(
        self, counter_neurons, G, iteration, m, retry, seed, test_object
    ):
        """Tests whether the SNN returns the same results as the Alipour algorithm."""
        # Compute the Alipour graph
        # delta, inhibition,iteration, G, rand_ceil, rand_nrs, m,seed,size, show=False, export=False.
        G_alipour = full_alipour(
            test_object.delta,
            test_object.inhibition,
            iteration,
            G,
            test_object.rand_ceil,
            test_object.rand_nrs,
            test_object.m,
            seed,
            len(test_object.G),
            export=True,
        )

        # Compare the counts per node and assert they are equal.
        print("G_alipour countermarks-SNN counter current")
        for node in G.nodes:
            print(
                f'{G_alipour.nodes[node]["countermarks"]}-{counter_neurons[node].u.get()}'
            )
        print(f"Now testing they are equal:")
        for node in G.nodes:
            self.assertEqual(
                G_alipour.nodes[node]["countermarks"],
                counter_neurons[node].u.get(),
            )
        write_results_to_file(m, G, retry, G_alipour, counter_neurons)
