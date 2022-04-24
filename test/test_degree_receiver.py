import unittest
import networkx as nx
from numpy import sort
from lava.magma.core.run_conditions import RunSteps
from lava.magma.core.run_configs import Loihi1SimCfg
from src.create_planar_triangle_free_graph import create_manual_graph_with_4_nodes
from src.helper import (
    fill_dictionary,
    get_a_in_for_degree_receiver,
    get_expected_amount_of_degree_receiver_neurons,
    get_wta_circuit_from_neuron_name,
    get_y_from_degree_receiver_x_y,
    print_neurons_properties,
    sort_neurons,
)
from test.contains_neurons_of_type_x import (
    get_n_neurons,
    assert_neurons_of_expected_type_are_all_present_in_snn,
)


from test.create_testobject import create_test_object
from test.helper_tests import perform_generic_neuron_property_asserts


class Test_degree_receiver(unittest.TestCase):
    """
    Tests whether the networks that are fed into networkx_to_snn are generating
    the correct snn networks.
    """

    # Initialize test object
    def __init__(self, *args, **kwargs):
        super(Test_degree_receiver, self).__init__(*args, **kwargs)

        # Moved into separate file to increase overview in this test file.
        self = create_test_object(self)
        # self = create_test_object(self, True, True)

    def test_degree_receiver_neuron_presence(
        self,
    ):
        """Tests whether the degree_receiver neurons are all present."""
        degree_receiver_neurons = (
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
        )
        get_n_neurons(
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
        # TODO: create stripped down function that just gets the degree_receiver neurons.
        degree_receiver_neurons = get_n_neurons(
            get_expected_amount_of_degree_receiver_neurons(self.G),
            self.neurons,
            self.neuron_dict,
            "degree_receiver_",
            self.sample_degree_receiver_neuron,
        )

        # Get the first neuron in the SNN to start the simulation
        starter_neuron = degree_receiver_neurons[0]

        # Create storage lists for previous neuron currents and voltages.
        previous_us = {}
        previous_vs = {}
        previous_us, previous_vs = fill_dictionary(
            self.neuron_dict, degree_receiver_neurons, previous_us, previous_vs
        )
        # previous_us = [0] * len(degree_receiver_neurons)
        # previous_vs = [0] * len(degree_receiver_neurons)

        # Simulate SNN and assert values inbetween timesteps.
        for t in range(1, 250):

            # Run the simulation for 1 timestep.
            starter_neuron.run(condition=RunSteps(num_steps=1), run_cfg=Loihi1SimCfg())

            # Print the values coming into the timestep.
            # Assert neuron values.
            self.verify_neuron_behaviour(
                previous_us,
                previous_vs,
                self.sample_degree_receiver_neuron,
                starter_neuron,
                t,
                degree_receiver_neurons,
            )
        # Terminate Loihi simulation.
        starter_neuron.stop()
        return degree_receiver_neurons

    def verify_neuron_behaviour(
        self,
        previous_us,
        previous_vs,
        sample_neuron,
        starter_neuron,
        t,
        degree_receiver_neurons,
    ):
        """Gets the neurons that are being tested: degree_receiver neurons. Then
        prints those neuron properties and performs the neuron behaviour tests
        for the given timestep t."""
        sorted_neurons = sort_neurons(degree_receiver_neurons, self.neuron_dict)
        print_neurons_properties(self.neuron_dict, sorted_neurons, t, descriptions=[])
        # Run test on each degree_receiver neuron in the SNN.
        for degree_receiver_neuron in sorted_neurons:

            # Get the name of the degree_receiver neuron and get which node is tested.
            degree_receiver_neuron_name = self.neuron_dict[degree_receiver_neuron]
            wta_circuit = get_wta_circuit_from_neuron_name(degree_receiver_neuron_name)
            # get degree_receiver_x_get_wta_circuit_from_neuron_namey
            y = get_y_from_degree_receiver_x_y(degree_receiver_neuron_name)

            # Perform test on degree_receiver neuron behaviour.
            (
                previous_us[degree_receiver_neuron_name],
                previous_vs[degree_receiver_neuron_name],
            ) = self.assert_degree_receiver_neuron_behaviour(
                previous_us[degree_receiver_neuron_name],
                previous_vs[degree_receiver_neuron_name],
                sample_neuron,
                degree_receiver_neuron,
                t,
                wta_circuit,
                y,
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
            self.sample_degree_receiver_neuron,
            t,
            wta_circuit,
            y,
        )
        # Compute expected selector neuron properties based on a_in previous.
        perform_generic_neuron_property_asserts(
            self,
            a_in,
            previous_u,
            self.sample_degree_receiver_neuron,
            degree_receiver_neuron,
        )

        return degree_receiver_neuron.u.get(), degree_receiver_neuron.v.get()
