import unittest
import networkx as nx
from lava.magma.core.run_conditions import RunSteps
from lava.magma.core.run_configs import Loihi1SimCfg
from src.create_planar_triangle_free_graph import create_manual_graph_with_4_nodes
from src.helper import (
    get_a_in_for_selector_neuron_retry,
    get_node_from_selector_neuron_name,
    is_selector_neuron_dict,
    print_degree_neurons,
)

from test.contains_selector_neurons import (
    all_selector_neurons_are_present_in_snn,
    get_n_selector_neurons,
)
from test.create_testobject import create_test_object


class Test_selector(unittest.TestCase):
    """
    Tests whether the networks that are fed into networkx_to_snn are generating
    the correct snn networks.
    """

    # Initialize test object
    def __init__(self, *args, **kwargs):
        super(Test_selector, self).__init__(*args, **kwargs)

        # Moved into separate file to increase overview in this test file.
        self = create_test_object(self)
        # self = create_test_object(self, True, True)

    def test_selector_neuron_presence(
        self,
    ):
        """Tests whether the degree_receiver neurons are all present."""
        selector_neurons = all_selector_neurons_are_present_in_snn(
            self, self.converted_nodes, self.G, self.get_degree, self.neurons
        )

        # TODO: Explicitly verify the neurons have the correct amount of
        # outgoing synapses.
        # TODO: Explcititly verify the outgoing synapses have the correct
        # weight.
        # This is currently both tested implicitly by checking the neuron
        # behaviour over time.
        return selector_neurons

    def test_selector_neuron_presence(self):
        """Verifies the neuron properties over time."""
        # TODO: create stripped down function that just gets the selector neurons.
        selector_neurons = get_n_selector_neurons(
            self.neurons,
            len(self.G),
            self.sample_selector_neuron,
        )

        # Get the first neuron in the SNN to start the simulation
        starter_neuron = selector_neurons[0]

        # Simulate SNN and assert values inbetween timesteps.
        for t in range(1, 100):

            # Run the simulation for 1 timestep.
            starter_neuron.run(condition=RunSteps(num_steps=1), run_cfg=Loihi1SimCfg())
            # Print the values coming into the timestep.
            # Assert neuron values.
            self.redirect_tests(
                self.sample_selector_neuron,
                starter_neuron,
                t,
                selector_neurons,
            )

        starter_neuron.stop()

        return selector_neurons

    def redirect_tests(self, sample_neuron, starter_neuron, t, selector_neurons):
        for selector_neuron in selector_neurons:
            selector_neuron_name = self.neuron_dict[selector_neuron]

            if is_selector_neuron_dict(selector_neuron, self.neuron_dict):
                wta_circuit = get_node_from_selector_neuron_name(selector_neuron_name)
                if t > -1:
                    if self.neuron_dict[selector_neuron] == "selector_1":
                        print_degree_neurons(
                            self.G,
                            self.neuron_dict,
                            wta_circuit,
                            t,
                            extra_neuron=selector_neuron,
                        )

                if t == 1:
                    self.asserts_for_selector_at_t_is_1(
                        sample_neuron,
                        selector_neuron,
                    )
                elif t == 2:
                    self.asserts_for_selector_at_t_is_2(
                        sample_neuron,
                        selector_neuron,
                        t,
                        wta_circuit,
                    )
                elif t == 3:
                    self.asserts_for_selector_at_t_is_3(
                        sample_neuron,
                        selector_neuron,
                        t,
                        wta_circuit,
                    )
                elif t == 4:
                    self.asserts_for_selector_at_t_is_4(
                        sample_neuron,
                        selector_neuron,
                        t,
                        wta_circuit,
                    )
                elif t > 4:
                    self.asserts_for_selector_at_t_is_larger_than_4(
                        sample_neuron,
                        selector_neuron,
                        t,
                        wta_circuit,
                    )
            else:
                print(f"Not a degree_receiver neuron:{selector_neuron_name}")
                exit()

    def asserts_for_selector_at_t_is_0(
        self,
        sample_neuron,
        selector_neuron,
    ):
        """Assert the values of the selector_neuron neuron on t=0."""
        self.assertEqual(selector_neuron.u.get(), 0)  # Default initial value.
        self.assertEqual(selector_neuron.du.get(), 0)  # Custom value.
        self.assertEqual(selector_neuron.v.get(), 0)  # Default initial value.
        self.assertEqual(
            selector_neuron.dv.get(), sample_neuron.dv
        )  # Default initial value.
        self.assertEqual(
            selector_neuron.bias.get(), sample_neuron.bias
        )  # Custom value.
        self.assertEqual(selector_neuron.vth.get(), sample_neuron.vth)  # Default value.

    def asserts_for_selector_at_t_is_1(
        self,
        sample_neuron,
        selector_neuron,
    ):
        """Assert the values of the selector_neuron neuron on t=1. t=1 occurs after
        one timestep."""

        # u[t=1]=u[t=0]*(1-1)+a_in
        # u[t=1]=0*(1-1)+0
        # u[t=1]=0*0+0
        # u[t=1]=0
        self.assertEqual(selector_neuron.u.get(), 0)
        # v[t=1] = v[t=0] * (1-dv) + u[t=0] + bias
        # v[t=1] = 0 * (1-1) + 0 + 0
        # v[t=1] = 0
        self.assertEqual(selector_neuron.v.get(), 0)

        self.assertEqual(selector_neuron.du.get(), sample_neuron.du)  # Custom Value.
        self.assertEqual(selector_neuron.dv.get(), sample_neuron.dv)  # Custom value.
        self.assertEqual(
            selector_neuron.bias.get(), sample_neuron.bias
        )  # Custom value.
        self.assertEqual(selector_neuron.vth.get(), sample_neuron.vth)  # Default value.

    def asserts_for_selector_at_t_is_2(
        self, sample_neuron, selector_neuron, t, wta_circuit
    ):
        """Assert the values of the selector_neuron neuron on t=2."""
        # Compute what the expected summed input spike values are.

        a_in = get_a_in_for_selector_neuron_retry(
            self.G,
            self.delta,
            self.incoming_selector_weight,
            wta_circuit,
            self.rand_nrs,
            t,
        )
        # u[t=2]=u[t=1]*(1-du)+a_in, a_in=
        # u[t=2]=0*(1-1)+0
        # u[t=2]=0*0+0
        # u[t=2]=-0
        # TODO: determine why the u.get is 15+3=18 V=selector_neuron_3_1 (or selector_neuron_2_1)
        # instead of selector_neuron_3_0=82+3=85 as computed by a_in.
        # TODO: verify whether selector_neuron is the correct neuron.
        self.assertEqual(selector_neuron.u.get(), a_in)
        # v[t=2] = v[t=1] * (1-dv) + u[t=0] + bias
        # v[t=1]_before_spike = 2
        # v[t=1]_after_spike = 0
        # v[t=2] = 0 * (1-2) + -a_in + 2
        # v[t=2] = 0
        self.assertEqual(selector_neuron.v.get(), selector_neuron.u.get())

        self.assertEqual(selector_neuron.du.get(), sample_neuron.du)  # Custom Value.
        self.assertEqual(selector_neuron.dv.get(), sample_neuron.dv)  # Custom value.
        self.assertEqual(
            selector_neuron.bias.get(), sample_neuron.bias
        )  # Custom value.
        self.assertEqual(selector_neuron.vth.get(), sample_neuron.vth)  # Default value.

    def asserts_for_selector_at_t_is_3(
        self,
        sample_neuron,
        selector_neuron,
        t,
        wta_circuit,
    ):
        """Assert the values of the selector_neuron neuron on t=3."""
        a_in = get_a_in_for_selector_neuron_retry(
            self.G,
            self.delta,
            self.incoming_selector_weight,
            wta_circuit,
            self.rand_nrs,
            t,
        )
        # u[t=3]=u[t=2]*(1-du)+a_in
        # u[t=3]=3*(1-0)-0
        # u[t=3]=3*1-0
        # u[t=3]=3
        self.assertEqual(selector_neuron.u.get(), a_in)
        # v[t=3] = v[t=2] * (1-dv) + u[t=2] + bias
        # v[t=3] = 0 * (1-0) -2 + 2
        # v[t=3] = 0
        self.assertEqual(selector_neuron.v.get(), selector_neuron.u.get())

        self.assertEqual(selector_neuron.du.get(), sample_neuron.du)  # Custom Value.
        self.assertEqual(selector_neuron.dv.get(), sample_neuron.dv)  # Custom value.
        self.assertEqual(
            selector_neuron.bias.get(), sample_neuron.bias
        )  # Custom value.
        self.assertEqual(selector_neuron.vth.get(), sample_neuron.vth)  # Default value.

    def asserts_for_selector_at_t_is_4(
        self, sample_neuron, selector_neuron, t, wta_circuit
    ):
        """Assert the values of the selector_neuron neuron on t=4."""
        a_in = get_a_in_for_selector_neuron_retry(
            self.G,
            self.delta,
            self.incoming_selector_weight,
            wta_circuit,
            self.rand_nrs,
            t,
        )
        # u[t=4]=u[t=3]*(1-du)+a_in
        # u[t=4]=3*(1-0)+0
        # u[t=4]=3
        self.assertEqual(selector_neuron.u.get(), a_in)
        # v[t=4] = v[t=3] * (1-dv) + u[t=2] + bias
        # v[t=4] = 0 * (1-0) -2 + 2
        # v[t=4] = 0
        # TODO: Compute voltage based on whether it spiked or not.
        self.assertEqual(selector_neuron.v.get(), selector_neuron.u.get())

        self.assertEqual(selector_neuron.du.get(), sample_neuron.du)  # Custom Value.
        self.assertEqual(selector_neuron.dv.get(), sample_neuron.dv)  # Custom value.
        self.assertEqual(
            selector_neuron.bias.get(), sample_neuron.bias
        )  # Custom value.
        self.assertEqual(selector_neuron.vth.get(), sample_neuron.vth)  # Default value.

    def asserts_for_selector_at_t_is_larger_than_4(
        self, sample_neuron, selector_neuron, t, wta_circuit
    ):
        """Assert the values of the selector_neuron neuron on t=4."""
        # a_in = get_a_in_for_selector_neuron(
        #    self.G, self.incoming_selector_weight, wta_circuit, self.rand_nrs, t
        # )
        a_in = get_a_in_for_selector_neuron_retry(
            self.G,
            self.delta,
            self.incoming_selector_weight,
            wta_circuit,
            self.rand_nrs,
            t,
        )

        # The current stays constant indefinitely.
        # u[t=x+1]=u[t=x]*(1-du)+a_in
        # u[t=x+1]=3*(1-0)+0
        # u[t=x+1]=3
        # print(f"a_in={a_in}")
        self.assertEqual(selector_neuron.u.get(), a_in)
        # The voltage stays constant indefinitely because the current
        # stays constant indefinitely whilst cancelling out the bias.
        # v[t=x+1] = v[t=x] * (1-dv) + u[t=2] + bias
        # v[t=x+1] = 0 * (1-0) -2 + 2
        # v[t=x+1] = 0
        if sample_neuron.bias + selector_neuron.u.get() > 1:
            expected_voltage = 0  # It spikes
        elif selector_neuron.u.get() < self.incoming_selector_weight:
            expected_voltage = sample_neuron.bias + selector_neuron.u.get()  # no spike
        else:
            expected_voltage = sample_neuron.bias + selector_neuron.u.get()  # no spike
        # expected_voltage = get_expected_voltage_of_first_spike(self.rand_nrs, t, a_in)
        # print(f"expected_voltage={expected_voltage}")
        # self.assertEqual(selector_neuron.v.get(), selector_neuron.u.get())
        self.assertEqual(selector_neuron.v.get(), expected_voltage)

        self.assertEqual(selector_neuron.du.get(), sample_neuron.du)  # Custom Value.
        self.assertEqual(selector_neuron.dv.get(), sample_neuron.dv)  # Custom value.
        self.assertEqual(
            selector_neuron.bias.get(), sample_neuron.bias
        )  # Custom value.
        self.assertEqual(selector_neuron.vth.get(), sample_neuron.vth)  # Default value.
