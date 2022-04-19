import unittest
import networkx as nx
from lava.magma.core.run_conditions import RunSteps
from lava.magma.core.run_configs import Loihi1SimCfg
from src.create_planar_triangle_free_graph import create_manual_graph_with_4_nodes
from src.helper import (
    get_a_in_for_spike_once,
    get_wta_circuit_from_neuron_name,
    print_degree_neurons,
)
from test.contains_neurons_of_type_x import (
    get_n_neurons,
    neurons_of_expected_type_are_all_present_in_snn,
)


from test.create_testobject import create_test_object


class Test_rand(unittest.TestCase):
    """
    Tests whether the networks that are fed into networkx_to_snn are generating
    the correct snn networks.
    """

    # Initialize test object
    def __init__(self, *args, **kwargs):
        super(Test_rand, self).__init__(*args, **kwargs)

        # Moved into separate file to increase overview in this test file.
        self = create_test_object(self)
        # self = create_test_object(self, True, True)

    def test_rand_neuron_presence(
        self,
    ):
        """Tests whether the degree_receiver neurons are all present."""
        rand_neurons = neurons_of_expected_type_are_all_present_in_snn(
            self,
            len(self.G),
            self.G,
            self.get_degree,
            self.neuron_dict,
            "rand_",
            self.neurons,
            self.sample_rand_neuron,
        )
        get_n_neurons(
            len(self.G),
            self.neurons,
            self.neuron_dict,
            "rand_",
            self.sample_rand_neuron,
        )

        # TODO: Explicitly verify the neurons have the correct amount of
        # outgoing synapses.
        # TODO: Explcititly verify the outgoing synapses have the correct
        # weight.
        # This is currently both tested implicitly by checking the neuron
        # behaviour over time.

    def test_rand_neurons_over_time(self):
        """Verifies the neuron properties over time."""
        # TODO: create stripped down function that just gets the rand neurons.
        rand_neurons = get_n_neurons(
            len(self.G),
            self.neurons,
            self.neuron_dict,
            "rand_",
            self.sample_rand_neuron,
        )

        # Get the first neuron in the SNN to start the simulation
        starter_neuron = rand_neurons[0]

        # Create storage lists for previous neuron currents and voltages.
        previous_us = [0] * len(rand_neurons)
        previous_vs = [0] * len(rand_neurons)

        # Simulate SNN and assert values inbetween timesteps.
        for t in range(1, 25):

            # Run the simulation for 1 timestep.
            starter_neuron.run(condition=RunSteps(num_steps=1), run_cfg=Loihi1SimCfg())

            # Print the values coming into the timestep.
            # Assert neuron values.
            self.verify_neuron_behaviour(
                previous_us,
                previous_vs,
                self.sample_rand_neuron,
                starter_neuron,
                t,
                rand_neurons,
            )
        # Terminate Loihi simulation.
        starter_neuron.stop()
        return rand_neurons

    def verify_neuron_behaviour(
        self,
        previous_us,
        previous_vs,
        sample_neuron,
        starter_neuron,
        t,
        rand_neurons,
    ):
        """Gets the neurons that are being tested: rand neurons. Then
        prints those neuron properties and performs the neuron behaviour tests
        for the given timestep t."""

        # Run test on each rand neuron in the SNN.
        for rand_neuron in rand_neurons:

            # Get the name of the rand neuron and get which node is tested.
            rand_neuron_name = self.neuron_dict[rand_neuron]
            wta_circuit = get_wta_circuit_from_neuron_name(rand_neuron_name)
            print(f"wta_circuit={wta_circuit}")

            # Print neuron properties of rand node and degree_receiver_x_y neurons.
            # TODO: rename from print_degree_neurons, to print_tested_neurons.
            # TODO: allow variable to pass which neurons are printed.
            if self.neuron_dict[rand_neuron] == "rand_1":
                print_degree_neurons(
                    self.G,
                    self.neuron_dict,
                    wta_circuit,
                    t,
                    extra_neuron=rand_neuron,
                )
            # Perform test on rand neuron behaviour.
            (
                previous_us[wta_circuit],
                previous_vs[wta_circuit],
            ) = self.assert_rand_neuron_behaviour(
                previous_us[wta_circuit],
                previous_vs[wta_circuit],
                sample_neuron,
                rand_neuron,
                t,
                wta_circuit,
            )

    def assert_rand_neuron_behaviour(
        self, previous_u, previous_v, sample_neuron, rand_neuron, t, wta_circuit
    ):
        """Assert the values of the rand_neuron neuron on t=4."""

        a_in = get_a_in_for_spike_once(t)

        # The current stays constant indefinitely.
        # u[t=x+1]=u[t=x]*(1-du)+a_in
        # TODO: Include the u(t-1)
        self.assertEqual(
            rand_neuron.u.get(),
            previous_u * (1 - rand_neuron.du.get()) + a_in,
        )
        # The voltage stays constant indefinitely because the current
        # stays constant indefinitely whilst cancelling out the bias.
        # v[t=x+1] = v[t=x] * (1-dv) + u[t=2] + bias
        if sample_neuron.bias + rand_neuron.u.get() > 1:
            expected_voltage = 0  # It spikes
        else:
            expected_voltage = sample_neuron.bias + rand_neuron.u.get()  # no spike
        self.assertEqual(rand_neuron.v.get(), expected_voltage)

        self.assertEqual(rand_neuron.du.get(), sample_neuron.du)  # Custom Value.
        self.assertEqual(rand_neuron.dv.get(), sample_neuron.dv)  # Custom value.
        self.assertEqual(rand_neuron.bias.get(), sample_neuron.bias)  # Custom value.
        self.assertEqual(rand_neuron.vth.get(), sample_neuron.vth)  # Default value.
        return rand_neuron.u.get(), rand_neuron.v.get()
