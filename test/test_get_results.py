import copy
from pprint import pprint
import unittest
import networkx as nx
from numpy import sort
from lava.magma.core.run_conditions import RunSteps
from lava.magma.core.run_configs import Loihi1SimCfg
from src.create_planar_triangle_free_graph import (
    create_manual_graph_with_4_nodes,
    create_manual_graph_with_5_nodes,
    create_manual_graph_with_6_nodes,
    create_triangle_free_planar_graph,
)
from src.helper import (
    degree_receiver_x_y_is_connected_to_counter_z,
    delete_files_in_folder,
    get_a_in_for_degree_receiver,
    get_degree_reciever_neurons_per_wta_circuit,
    get_grouped_neurons,
    get_wta_circuit_from_neuron_name,
    get_y_from_degree_receiver_x_y,
    print_neuron_behaviour,
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

    def get_graphs_for_this_test(self, size=None, random=None):
        # Get list of planer triangle free graphs.
        if not size is None and not random is None:
            G = create_triangle_free_planar_graph(size, 0.6, 42, False)
        else:
            # G = create_manual_graph_with_4_nodes()
            # G = create_manual_graph_with_5_nodes()
            G = create_manual_graph_with_6_nodes()
        return G

    def perform_integration_test_on_end_result(
        self, counter_neurons, G, m, retry, test_object
    ):
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
        # Terminate Loihi simulation

    # Initialize test object
    def __init__(self, *args, **kwargs):
        super(Test_counter, self).__init__(*args, **kwargs)

    def test_multiple_tests(self):

        # delete_dir_if_exists(f"latex/Images/graphs")
        delete_files_in_folder(f"latex/Images/graphs")

        for m in range(1, 2):
            plot_neuron_behaviour = True
            for retry in range(0, 1, 1):
                for size in range(5, 6, 1):
                    G = self.get_graphs_for_this_test(size=None, random=None)

                    # Initialise paramers used for testing.
                    test_object = create_test_object(G, retry, m, False, False)

                    # Run default tests on neurons and get counted degree from
                    # neurons after inhibition time.
                    (
                        counter_neurons,
                        starter_neuron,
                    ) = self.run_test_degree_receiver_neurons_over_time(
                        m,
                        plot_neuron_behaviour,
                        retry,
                        test_object,
                        extraction_time=test_object.inhibition + 1,
                    )

                    # Check if expected counter nodes are selected.
                    self.perform_integration_test_on_end_result(
                        self, counter_neurons, G, m, retry, test_object
                    )

                    # Terminate loihi simulation for this run.
                    starter_neuron.stop()

    def run_test_degree_receiver_neurons_over_time(
        self, m, plot_neuron_behaviour, retry, test_object, extraction_time=None
    ):
        """Verifies the neuron properties over time."""

        # TODO: Generalise to work on all neurons (Also allow redundant neurons).
        # Get a dictionary of neuron_naming_sceme and the accompanying sorted neurons.
        grouped_neurons = get_grouped_neurons(m, test_object)

        # Get the first neuron in the SNN to start the simulation
        starter_neuron = grouped_neurons["spike_once_x_0"][0]

        # TODO: Generalise to work on all neurons.
        # Create storage lists for previous neuron currents and voltages.
        (
            degree_receiver_has_spiked,
            degree_receiver_previous_us,
            degree_receiver_previous_vs,
        ) = get_degree_receiver_previous_property_dicts(
            test_object, grouped_neurons["degree_receiver_neurons_x_y_0"]
        )
        (
            selector_previous_a_in,
            selector_previous_us,
            selector_previous_vs,
        ) = get_selector_previous_property_dicts(
            test_object, grouped_neurons["selector_neurons_x_0"]
        )

        (
            counter_previous_a_in,
            counter_previous_us,
            counter_previous_vs,
        ) = get_counter_previous_property_dicts(
            test_object, grouped_neurons[f"counter_neurons_x_{m}"]
        )

        # Simulate SNN and assert values inbetween timesteps.
        # Simulate till extraction time+10 sec.
        for t in range(1, test_object.sim_time):

            # Run the simulation for 1 timestep.
            starter_neuron.run(condition=RunSteps(num_steps=1), run_cfg=Loihi1SimCfg())

            # Print the values coming into the timestep.
            # if t > 44 and t < 49:

            if plot_neuron_behaviour:
                spike_dict = print_neuron_behaviour(test_object, grouped_neurons, t)
                test_object = get_node_names(
                    grouped_neurons, test_object.neuron_dict, spike_dict, t, test_object
                )
                plot_neuron_behaviour_over_time(
                    test_object.get_degree,
                    retry,
                    len(test_object.G),
                    grouped_neurons,
                    m,
                    spike_dict,
                    t,
                    show=False,
                )

            # TODO: Get args from create object.
            self.verify_neuron_behaviour(
                test_object,
                degree_receiver_has_spiked,
                degree_receiver_previous_us,
                degree_receiver_previous_vs,
                test_object.sample_degree_receiver_neuron,
                counter_previous_a_in,
                counter_previous_us,
                counter_previous_vs,
                selector_previous_a_in,
                selector_previous_us,
                selector_previous_vs,
                grouped_neurons[f"counter_neurons_x_{m}"],
                grouped_neurons["degree_receiver_neurons_x_y_0"],
                grouped_neurons["selector_neurons_x_0"],
                starter_neuron,
                t,
            )
            if not extraction_time is None and t == extraction_time:
                extracted_neurons = grouped_neurons[f"counter_neurons_x_{m}"]

        # raise Exception("Stop")
        if not extraction_time:
            return extracted_neurons, starter_neuron
        else:
            return grouped_neurons[f"counter_neurons_x_{m}"], starter_neuron

    def verify_neuron_behaviour(
        self,
        test_object,
        degree_receiver_has_spiked,
        degree_receiver_previous_us,
        degree_receiver_previous_vs,
        sample_neuron,
        counter_previous_a_in,
        counter_previous_us,
        counter_previous_vs,
        selector_previous_a_in,
        selector_previous_us,
        selector_previous_vs,
        sorted_counter_neurons,
        sorted_degree_receiver_neurons,
        sorted_selector_neurons,
        starter_neuron,
        t,
    ):
        """Gets the neurons that are being tested: degree_receiver neurons. Then
        prints those neuron properties and performs the neuron behaviour tests
        for the given timestep t."""

        # Run test on each degree_receiver neuron in the SNN.
        for degree_receiver_neuron in sorted_degree_receiver_neurons:

            # Get the name of the degree_receiver neuron and get which node is tested.
            degree_receiver_neuron_name = test_object.neuron_dict[
                degree_receiver_neuron
            ]
            wta_circuit = get_wta_circuit_from_neuron_name(degree_receiver_neuron_name)
            # get degree_receiver_x_get_wta_circuit_from_neuron_namey
            y = get_y_from_degree_receiver_x_y(degree_receiver_neuron_name)

            # Perform test on degree_receiver neuron behaviour.
            (
                degree_receiver_has_spiked[degree_receiver_neuron_name],
                degree_receiver_previous_us[degree_receiver_neuron_name],
                degree_receiver_previous_vs[degree_receiver_neuron_name],
            ) = self.assert_degree_receiver_neuron_behaviour(
                test_object,
                degree_receiver_has_spiked[degree_receiver_neuron_name],
                degree_receiver_previous_us[degree_receiver_neuron_name],
                degree_receiver_previous_vs[degree_receiver_neuron_name],
                sample_neuron,
                degree_receiver_neuron,
                t,
                wta_circuit,
                y,
            )
        # Verify selector neurons behave as expected.
        self.run_test_on_selector_neurons(
            test_object,
            test_object.sample_selector_neuron,
            selector_previous_a_in,
            selector_previous_us,
            selector_previous_vs,
            sorted_degree_receiver_neurons,
            sorted_selector_neurons,
            t,
        )

        # # Verify counter neurons behave as expected.
        # self.run_test_on_counter_neurons(
        #     test_object,
        #     test_object.sample_counter_neuron,
        #     counter_previous_a_in,
        #     counter_previous_us,
        #     counter_previous_vs,
        #     sorted_degree_receiver_neurons,
        #     sorted_counter_neurons,
        #     t,
        # )

    def run_test_on_selector_neurons(
        self,
        test_object,
        sample_selector_neuron,
        selector_previous_a_in,
        selector_previous_us,
        selector_previous_vs,
        sorted_degree_receiver_neurons,
        sorted_selector_neurons,
        t,
    ):
        # Run tests on selector.
        for selector_neuron in sorted_selector_neurons:
            selector_neuron_name = test_object.neuron_dict[selector_neuron]
            wta_circuit = int(selector_neuron_name.split("_")[1])
            # print(f"wta_circuit={wta_circuit}")
            # print(f"selector_neuron_name={selector_neuron_name}")
            # print(
            #    f"selector_previous_a_in[selector_neuron_name]={selector_previous_a_in[selector_neuron_name]}"
            # )
            (
                selector_previous_a_in[selector_neuron_name],
                selector_previous_us[selector_neuron_name],
                selector_previous_vs[selector_neuron_name],
            ) = self.get_selector_a_in_and_call_asserts(
                test_object,
                selector_previous_a_in[selector_neuron_name],
                selector_previous_us[selector_neuron_name],
                selector_previous_vs[selector_neuron_name],
                sample_selector_neuron,
                selector_neuron,
                sorted_degree_receiver_neurons,
                t,
                wta_circuit,
            )

    def run_test_on_counter_neurons(
        self,
        test_object,
        sample_counter_neuron,
        counter_previous_a_in,
        counter_previous_us,
        counter_previous_vs,
        sorted_degree_receiver_neurons,
        sorted_counter_neurons,
        t,
    ):
        # Run tests on counter.
        for counter_neuron in sorted_counter_neurons:
            counter_neuron_name = test_object.neuron_dict[counter_neuron]
            wta_circuit = int(counter_neuron_name.split("_")[1])
            (
                counter_previous_a_in[counter_neuron_name],
                counter_previous_us[counter_neuron_name],
                counter_previous_vs[counter_neuron_name],
            ) = self.assert_counter_neuron_behaviour(
                test_object,
                counter_previous_a_in[counter_neuron_name],
                counter_previous_us[counter_neuron_name],
                counter_previous_vs[counter_neuron_name],
                sample_counter_neuron,
                counter_neuron,
                sorted_degree_receiver_neurons,
                t,
                wta_circuit,
            )

    def assert_degree_receiver_neuron_behaviour(
        self,
        test_object,
        previous_has_spiked,
        previous_u,
        previous_v,
        sample_neuron,
        degree_receiver_neuron,
        t,
        wta_circuit,
        y,
    ):
        """Assert the values of the degree_receiver_neuron neuron on t=4."""

        a_in = get_a_in_for_degree_receiver(
            test_object.G,
            test_object.found_winner,
            test_object.found_winner_at_t,
            wta_circuit,
            previous_u,
            previous_v,
            test_object.rand_nrs,
            test_object.rand_ceil * test_object.delta + 1,
            test_object.sample_degree_receiver_neuron,
            t,
            wta_circuit,
            y,
        )
        # print(f'before previous_has_spiked={previous_has_spiked}')
        if previous_has_spiked:
            a_in = a_in - 20
        if (
            test_object.sample_degree_receiver_neuron.bias
            + degree_receiver_neuron.u.get()
            > test_object.sample_degree_receiver_neuron.vth
        ):
            previous_has_spiked = True
        else:
            previous_has_spiked = False
        # print(f'after previous_has_spiked={previous_has_spiked}')

        perform_generic_neuron_property_asserts(
            self, test_object, a_in, previous_u, sample_neuron, degree_receiver_neuron
        )
        return (
            previous_has_spiked,
            degree_receiver_neuron.u.get(),
            degree_receiver_neuron.v.get(),
        )

    def get_selector_a_in_and_call_asserts(
        self,
        test_object,
        previous_a_in,
        previous_u,
        previous_v,
        sample_selector_neuron,
        selector_neuron,
        sorted_degree_receiver_neurons,
        t,
        wta_circuit,
    ):
        self.assertTrue(True)

        # Compute expected selector neuron properties based on a_in previous.
        perform_generic_neuron_property_asserts(
            self,
            test_object,
            previous_a_in,
            previous_u,
            sample_selector_neuron,
            selector_neuron,
        )

        # TODO: disentangle u[t-1] and previous_a_in.
        # Compute what the a_in for selector_x will be in next round(/time this function is called).
        # Get degree_receiver neurons from wta circuits.
        wta_degree_receiver_neurons = get_degree_reciever_neurons_per_wta_circuit(
            sorted_degree_receiver_neurons, test_object.neuron_dict, wta_circuit
        )
        # Loop over relevant degree_receiver neurons
        for wta_degree_receiver_neuron in wta_degree_receiver_neurons:

            # Determine if degree_receiver neuron has spiked.
            if (
                wta_degree_receiver_neuron.bias.get()
                + wta_degree_receiver_neuron.u.get()
                > wta_degree_receiver_neuron.vth.get()
            ):
                # degree_receiver neuron has spiked, so selector neuron get's -5 as input in next round.
                previous_a_in = previous_a_in - 5
            else:
                previous_a_in = previous_a_in  # no spike

        return previous_a_in, previous_u, previous_v

    def assert_counter_neuron_behaviour(
        self,
        test_object,
        previous_a_in,
        previous_u,
        previous_v,
        sample_counter_neuron,
        counter_neuron,
        sorted_degree_receiver_neurons,
        t,
        wta_circuit,
    ):

        # Compute expected counter neuron properties based on a_in previous.
        perform_generic_neuron_property_asserts(
            self,
            test_object,
            previous_a_in,
            previous_u,
            sample_counter_neuron,
            counter_neuron,
        )

        # the current u[t-1] which was included in previous_a_in for the
        # selector neuron, is leaked for counter neurons, so a_in is
        # a_in without what a_in was in the previous round.
        current_a_in = 0

        for node in test_object.G.nodes:
            # Get degree_receiver neurons from wta circuits.
            node_degree_receiver_neurons = get_degree_reciever_neurons_per_wta_circuit(
                sorted_degree_receiver_neurons, test_object.neuron_dict, node
            )

            # Loop over relevant degree_receiver neurons
            for wta_degree_receiver_neuron in node_degree_receiver_neurons:

                # Determine if degree_receiver neuron has spiked.
                if (
                    wta_degree_receiver_neuron.bias.get()
                    + wta_degree_receiver_neuron.u.get()
                    > wta_degree_receiver_neuron.vth.get()
                ):
                    # degree_receiver neuron has spiked.
                    # Get x,y in degree_receiver_x_y
                    if degree_receiver_x_y_is_connected_to_counter_z(
                        counter_neuron,
                        wta_degree_receiver_neuron,
                        test_object.G,
                        test_object.neuron_dict,
                    ):
                        current_a_in = current_a_in + 1
                    else:
                        current_a_in = current_a_in  # no spike

        return current_a_in, counter_neuron.u.get(), counter_neuron.v.get()
