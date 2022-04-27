import unittest
import networkx as nx
from numpy import sort
from lava.magma.core.run_conditions import RunSteps
from lava.magma.core.run_configs import Loihi1SimCfg
from src.create_planar_triangle_free_graph import create_manual_graph_with_4_nodes
from src.helper import (
    degree_receiver_x_y_is_connected_to_counter_z,
    get_a_in_for_degree_receiver,
    get_degree_reciever_neurons_per_wta_circuit,
    get_expected_amount_of_degree_receiver_neurons,
    get_wta_circuit_from_neuron_name,
    get_y_from_degree_receiver_x_y,
    print_neurons_properties,
)
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
    Tests whether the networks that are fed into networkx_to_snn are generating
    the correct snn networks.
    """

    # Initialize test object
    def __init__(self, *args, **kwargs):
        super(Test_counter, self).__init__(*args, **kwargs)

        # Moved into separate file to increase overview in this test file.
        self = create_test_object(self)
        # self = create_test_object(self, True, True)

    def test_degree_receiver_neuron_presence(
        self,
    ):
        """# TODO: move to functie elders.
        Tests whether the degree_receiver neurons are all present."""
        assert_neurons_of_expected_type_are_all_present_in_snn(
            self,
            get_expected_amount_of_degree_receiver_neurons(self.G),
            self.G,
            self.get_degree,
            self.neuron_dict,
            "degree_receiver_",
            self.neurons,
            self.sample_degree_receiver_neuron,
        )
        degree_receiver_neurons = get_n_neurons(
            get_expected_amount_of_degree_receiver_neurons(self.G),
            self.neurons,
            self.neuron_dict,
            "degree_receiver_",
            self.sample_degree_receiver_neuron,
        )

        # TODO: Explicitly verify the neurons have the correct amount of
        # outgoing synapses.
        # TODO: Explcititly verify the outgoing synapses have the correct
        # weight.
        # This is currently both tested implicitly by checking the neuron
        # behaviour over time.

    def test_degree_receiver_neurons_over_time(self):
        """Verifies the neuron properties over time."""

        # Collect the neurons of a particular type and get a starter neuron for
        # SNN simulation.
        # TODO: Move into create object.
        (
            self,
            sorted_degree_receiver_neurons,
            starter_neuron,
        ) = get_degree_receiver_neurons(self)
        self, sorted_selector_neurons, selector_starter_neuron = get_selector_neurons(
            self
        )
        self, sorted_counter_neurons, counter_starter_neuron = get_counter_neurons(self)
        # TODO: Move into create object.
        # Create storage lists for previous neuron currents and voltages.
        (
            degree_receiver_previous_us,
            degree_receiver_previous_vs,
        ) = get_degree_receiver_previous_property_dicts(
            self, sorted_degree_receiver_neurons
        )
        (
            selector_previous_a_in,
            selector_previous_us,
            selector_previous_vs,
        ) = get_selector_previous_property_dicts(self, sorted_selector_neurons)

        (
            counter_previous_a_in,
            counter_previous_us,
            counter_previous_vs,
        ) = get_counter_previous_property_dicts(self, sorted_counter_neurons)

        # Simulate SNN and assert values inbetween timesteps.
        for t in range(1, 30):

            # Run the simulation for 1 timestep.
            starter_neuron.run(condition=RunSteps(num_steps=1), run_cfg=Loihi1SimCfg())

            # Print the values coming into the timestep.
            # Assert neuron values.
            # TODO: Get args from create object.
            self.verify_neuron_behaviour(
                degree_receiver_previous_us,
                degree_receiver_previous_vs,
                self.sample_degree_receiver_neuron,
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
        # Terminate Loihi simulation.
        starter_neuron.stop()
        # raise Exception("Stop")
        return sorted_degree_receiver_neurons

    def verify_neuron_behaviour(
        self,
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
        #
        print_neurons_properties(
            self.neuron_dict, sorted_degree_receiver_neurons, t, descriptions=[]
        )
        print_neurons_properties(
            self.neuron_dict, sorted_selector_neurons, t, descriptions=[]
        )
        print_neurons_properties(
            self.neuron_dict, sorted_counter_neurons, t, descriptions=[]
        )
        # Run test on each degree_receiver neuron in the SNN.
        for degree_receiver_neuron in sorted_degree_receiver_neurons:

            # Get the name of the degree_receiver neuron and get which node is tested.
            degree_receiver_neuron_name = self.neuron_dict[degree_receiver_neuron]
            wta_circuit = get_wta_circuit_from_neuron_name(degree_receiver_neuron_name)
            # get degree_receiver_x_get_wta_circuit_from_neuron_namey
            y = get_y_from_degree_receiver_x_y(degree_receiver_neuron_name)

            # Perform test on degree_receiver neuron behaviour.
            (
                degree_receiver_previous_us[degree_receiver_neuron_name],
                degree_receiver_previous_vs[degree_receiver_neuron_name],
            ) = self.assert_degree_receiver_neuron_behaviour(
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
            self.sample_selector_neuron,
            selector_previous_a_in,
            selector_previous_us,
            selector_previous_vs,
            sorted_degree_receiver_neurons,
            sorted_selector_neurons,
            t,
        )

        # Verify counter neurons behave as expected.
        self.run_test_on_counter_neurons(
            self.sample_counter_neuron,
            counter_previous_a_in,
            counter_previous_us,
            counter_previous_vs,
            sorted_degree_receiver_neurons,
            sorted_counter_neurons,
            t,
        )

    def run_test_on_selector_neurons(
        self,
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
            selector_neuron_name = self.neuron_dict[selector_neuron]
            wta_circuit = int(selector_neuron_name.split("_")[1])
            # print(f"wta_circuit={wta_circuit}")
            (
                selector_previous_a_in[selector_neuron_name],
                selector_previous_us[selector_neuron_name],
                selector_previous_vs[selector_neuron_name],
            ) = self.get_selector_a_in_and_call_asserts(
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
            counter_neuron_name = self.neuron_dict[counter_neuron]
            wta_circuit = int(counter_neuron_name.split("_")[1])
            (
                counter_previous_a_in[counter_neuron_name],
                counter_previous_us[counter_neuron_name],
                counter_previous_vs[counter_neuron_name],
            ) = self.assert_counter_neuron_behaviour(
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
            self.G,
            self.found_winner,
            self.found_winner_at_t,
            wta_circuit,
            previous_u,
            previous_v,
            self.rand_nrs,
            self.rand_ceil * self.delta + 1,
            self.sample_degree_receiver_neuron,
            t,
            wta_circuit,
            y,
        )

        perform_generic_neuron_property_asserts(
            self, a_in, previous_u, sample_neuron, degree_receiver_neuron
        )
        return degree_receiver_neuron.u.get(), degree_receiver_neuron.v.get()

    def get_selector_a_in_and_call_asserts(
        self,
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
            self, previous_a_in, previous_u, sample_selector_neuron, selector_neuron
        )

        # TODO: disentangle u[t-1] and previous_a_in.
        # Compute what the a_in for selector_x will be in next round(/time this function is called).
        # Get degree_receiver neurons from wta circuits.
        wta_degree_receiver_neurons = get_degree_reciever_neurons_per_wta_circuit(
            sorted_degree_receiver_neurons, self.neuron_dict, wta_circuit
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
            self, previous_a_in, previous_u, sample_counter_neuron, counter_neuron
        )

        # the current u[t-1] which was included in previous_a_in for the
        # selector neuron, is leaked for counter neurons, so a_in is
        # a_in without what a_in was in the previous round.
        previous_a_in = 0

        for node in self.G.nodes:
            # Get degree_receiver neurons from wta circuits.
            node_degree_receiver_neurons = get_degree_reciever_neurons_per_wta_circuit(
                sorted_degree_receiver_neurons, self.neuron_dict, node
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
                        self.G,
                        self.neuron_dict,
                    ):
                        previous_a_in = previous_a_in + 1
                        print(f"FOUND SPIKE FOR COUNTER, previous_a_in={previous_a_in}")
                    else:
                        previous_a_in = previous_a_in  # no spike

        return previous_a_in, previous_u, previous_v
