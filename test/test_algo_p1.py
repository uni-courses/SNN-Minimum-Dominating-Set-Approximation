import copy
import unittest
import networkx as nx
from numpy import sort
from lava.magma.core.run_conditions import RunSteps
from lava.magma.core.run_configs import Loihi1SimCfg
from src.create_planar_triangle_free_graph import (
    create_manual_graph_with_4_nodes,
    create_triangle_free_planar_graph,
)
from src.export_data.helper_dir_file_edit import delete_dir_if_exists
from src.helper import (
    degree_receiver_x_y_is_connected_to_counter_z,
    get_a_in_for_degree_receiver,
    get_degree_reciever_neurons_per_wta_circuit,
    get_expected_amount_of_degree_receiver_neurons,
    get_wta_circuit_from_neuron_name,
    get_y_from_degree_receiver_x_y,
    print_neurons_properties,
)
from src.neumann import partial_alipour, full_alipour
from test.contains_neurons_of_type_x import (
    get_n_neurons,
    assert_neurons_of_expected_type_are_all_present_in_snn,
)


from test.create_testobject import (
    create_test_object,
    get_counter_neurons,
    get_counter_previous_property_dicts,
    get_degree_receiver_neurons,
    get_degree_receiver_previous_property_dicts,
    get_selector_neurons,
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

    def test_multiple_tests(self):

        # delete_dir_if_exists(f"latex/Images/graphs")

        # Get list of planer triangle free graphs.
        m = 0

        for retry in range(0, 1, 1):
            graphs = []
            for size in range(3, 4, 1):
                graphs.append(create_triangle_free_planar_graph(size, 0.6, 42, False))
            for G in graphs:
                # G = create_manual_graph_with_4_nodes()
                # Initialise paramers used for testing.
                test_object = create_test_object(G, retry, m, False, False)

                # Run default tests on neurons
                # and get counted degree from neurons after inhibition time.
                (
                    counter_neurons,
                    starter_neuron,
                ) = self.run_test_degree_receiver_neurons_over_time(
                    test_object, extraction_time=test_object.inhibition + 1
                )

                # Compute degree count using Alipour algorithm
                # G_alipour = partial_alipour(
                #     test_object.delta,
                #     test_object.inhibition,
                #     G,
                #     test_object.rand_ceil,
                #     test_object.rand_nrs,
                # )

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
                        "G_alipour countermarks", G_alipour.nodes[node]["countermarks"]
                    )
                    print("SNN counter current", counter_neurons[node].u.get())
                    self.assertEqual(
                        G_alipour.nodes[node]["countermarks"],
                        counter_neurons[node].u.get(),
                    )
                # Terminate Loihi simulation.
                starter_neuron.stop()

    def run_test_degree_receiver_neurons_over_time(
        self, test_object, extraction_time=None
    ):
        """Verifies the neuron properties over time."""

        # Collect the neurons of a particular type and get a starter neuron for
        # SNN simulation.
        # TODO: Move into create object.
        (
            test_object,
            sorted_degree_receiver_neurons,
            starter_neuron,
        ) = get_degree_receiver_neurons(test_object)
        (
            test_object,
            sorted_selector_neurons,
            selector_starter_neuron,
        ) = get_selector_neurons(test_object)
        (
            test_object,
            sorted_counter_neurons,
            counter_starter_neuron,
        ) = get_counter_neurons(test_object)
        # TODO: Move into create object.
        # Create storage lists for previous neuron currents and voltages.
        (
            degree_receiver_has_spiked,
            degree_receiver_previous_us,
            degree_receiver_previous_vs,
        ) = get_degree_receiver_previous_property_dicts(
            test_object, sorted_degree_receiver_neurons
        )
        (
            selector_previous_a_in,
            selector_previous_us,
            selector_previous_vs,
        ) = get_selector_previous_property_dicts(test_object, sorted_selector_neurons)

        (
            counter_previous_a_in,
            counter_previous_us,
            counter_previous_vs,
        ) = get_counter_previous_property_dicts(test_object, sorted_counter_neurons)

        # Simulate SNN and assert values inbetween timesteps.
        # Simulate till extraction time+10 sec.
        for t in range(1, test_object.sim_time):

            # Run the simulation for 1 timestep.
            starter_neuron.run(condition=RunSteps(num_steps=1), run_cfg=Loihi1SimCfg())

            # Print the values coming into the timestep.
            # Assert neuron values.
            self.print_neuron_properties(
                test_object,
                sorted_counter_neurons,
                sorted_degree_receiver_neurons,
                sorted_selector_neurons,
                t,
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
                sorted_counter_neurons,
                sorted_degree_receiver_neurons,
                sorted_selector_neurons,
                starter_neuron,
                t,
            )
            if not extraction_time is None and t == extraction_time:
                extracted_neurons = sorted_counter_neurons

        # raise Exception("Stop")
        if not extraction_time:
            return extracted_neurons, starter_neuron
        else:
            return sorted_counter_neurons, starter_neuron

    def print_neuron_properties(
        self,
        test_object,
        sorted_counter_neurons,
        sorted_degree_receiver_neurons,
        sorted_selector_neurons,
        t,
    ):
        #
        print_neurons_properties(
            test_object,
            test_object.neuron_dict,
            sorted_degree_receiver_neurons,
            t,
            descriptions=[],
        )
        print_neurons_properties(
            test_object,
            test_object.neuron_dict,
            sorted_selector_neurons,
            t,
            descriptions=[],
        )
        print_neurons_properties(
            test_object,
            test_object.neuron_dict,
            sorted_counter_neurons,
            t,
            descriptions=[],
        )

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
            a_in = a_in - 2
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
        print(f"t={t}")
        print(f"testing:{test_object.neuron_dict[counter_neuron]}")
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
                        print(f"FOUND SPIKE FOR COUNTER, current_a_in={current_a_in}")
                    else:
                        current_a_in = current_a_in  # no spike

        return current_a_in, counter_neuron.u.get(), counter_neuron.v.get()
