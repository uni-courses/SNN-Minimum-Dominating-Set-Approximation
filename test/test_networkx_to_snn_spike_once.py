import unittest
import networkx as nx
from lava.magma.core.run_conditions import RunSteps
from lava.magma.core.run_configs import Loihi1SimCfg


from src.helper_network_structure import get_degree_graph, plot_graph
from src.helper_snns import create_spike_once_neuron, print_neuron_properties
from src.networkx_to_snn import (
    convert_networkx_graph_to_snn_with_one_neuron,
    get_node_belonging_to_neuron_from_list,
)
from test.helper_tests import neurons_contain_n_spike_once_neurons
from test.test_neuron_behaviour.test_spike_once import a_in_spike_once


class Test_networkx_to_snn(unittest.TestCase):
    """
    Tests whether the networks that are fed into networkx_to_snn are generating
    the correct snn networks.
    """

    # Initialize test object
    def __init__(self, *args, **kwargs):
        super(Test_networkx_to_snn, self).__init__(*args, **kwargs)
        self.example_spike_once = create_spike_once_neuron()
        self.du = self.example_spike_once.du.get()
        self.dv = self.example_spike_once.dv.get()
        self.bias = self.example_spike_once.bias.get()
        self.vth = self.example_spike_once.vth.get()
        # Generate a fully connected graph with n=4.
        self.G = nx.complete_graph(4)
        # print(f"Incoming G")
        # plot_graph(G) # TODO: There can be only one function plot_graph.

        # Convert the fully connected graph into a networkx graph that
        # stores the snn properties to create an snn that computes the degree
        # in the number of spikes into the degree_receiver neurons.
        self.get_degree = get_degree_graph(self.G)

        # Convert the get_degree network into an actual snn network.
        # convert_networkx_graph_to_snn(
        #    get_degree, True, bias=0, du=0, dv=0, weight=1, vth=1
        # )
        (
            self.converted_nodes,
            self.lhs_neuron,
            self.neurons,
            self.lhs_node,
        ) = convert_networkx_graph_to_snn_with_one_neuron(
            self.get_degree, True, bias=0, du=0, dv=0, weight=1, vth=1
        )

    def test_spike_once_neurons_in_get_degree(
        self,
    ):
        """Tests whether the neurons are all present.
        Verifies the neuron initial properties at t=0.
        Verifies the neuron properties over time.
        Assumes a spike occurs at t=1 in the spike_once neurons.
        """
        # Asserts all spike_once neurons are present in snn, and:
        # Asserts the initial properties for the spike_once neurons are
        # correct at t=0.
        # TODO: include expected values in this test explicitly, instead of in
        # spike_once neuron.
        spike_once_neurons = self.all_spike_once_neurons_are_present_in_snn(
            self.converted_nodes, self.G, self.get_degree, self.neurons
        )

        # TODO: include assert on recurrent synapse with weight -2 on spike_once_neuron.

        # TODO: Assert the spike_once_neurons spike at t=1
        # Simulate SNN and assert values inbetween timesteps.
        # for spike_once in spike_once_neurons:
        # Only run the tests on the first node.
        starter_neuron = spike_once_neurons[0]
        # spike_once= spike_once_neurons[3]
        print(f"self.converted_nodes={self.converted_nodes}")
        print(f"self.neurons={self.neurons}")
        for t in range(1, 100):

            # Run the simulation for 1 timestep.
            starter_neuron.run(condition=RunSteps(num_steps=1), run_cfg=Loihi1SimCfg())
            # Print the values coming into the timestep.
            # print(f"t={t}"), print_neuron_properties([starter_neuron])
            # Assert neuron values.
            self.redirect_tests(
                self.bias,
                self.du,
                self.dv,
                starter_neuron,
                t,
                self.vth,
                spike_once_neurons,
            )

        starter_neuron.stop()

        # TODO: Assert the neuron properties for the spike_once neurons are
        # correct at t>0

    def all_spike_once_neurons_are_present_in_snn(
        self, converted_nodes, G, get_degree, neurons
    ):
        """Assumes neurons are named spike_once_<index>. Where index represents
        the number of the node in the original graph G that they represent."""
        # Assert for each node in graph G, that a spike_once node exists in
        # get_degree.
        for node in G.nodes:
            # print(f"node={node}")
            # print(f"get_degree.nodes={get_degree.nodes}")
            self.assertTrue(f"spike_once_{node}" in get_degree.nodes)

        for node in converted_nodes:
            print(f"converted node={node}")

        # Assert no more than n spike_once nodes exist in get_degree.
        self.assertEqual(sum("spike_once" in string for string in get_degree.nodes), 4)
        self.assertEqual(
            sum("spike_once" in string for string in get_degree.nodes), len(G.nodes)
        )

        # Write a function that verifies n neurons exist with the
        # spike_once properties.
        (
            has_n_spike_once_neurons,
            spike_once_neurons,
        ) = neurons_contain_n_spike_once_neurons(
            self.example_spike_once.bias.get(),
            self.example_spike_once.du.get(),
            self.example_spike_once.dv.get(),
            neurons,
            len(G.nodes),
            self.example_spike_once.vth.get(),
        )
        self.assertTrue(has_n_spike_once_neurons)

        # TODO: Verify they have the correct amount of outgoing synapses.
        # This is currently tested implicitly by checking the spike_once
        # behaviour over time.

        # TODO: Verify the outgoing synapses have the correct weight.

        # TODO: Subtract those neurons from neuron group and return reduced
        #  group for remainder of tests.
        return spike_once_neurons

    def networkx_to_snn_weight_calculation(self):
        """
        TODO: create new test that verifies the incoming random spikes of
        neurons are added to the u(t) of the degree_receiver neurons.
        Verify that this also included the spike_once degree count in u(t).
        """
        pass

        # TODO: Write function that creates the random spiking neurons.
        # Specficy the range of their random values and use those as a
        # multiplication factor for the time window.
        # TODO: Assert the number of spikes is within the specified window.
        # TODO: Write function that creates the synapses between the
        # random spiking neurons and the degree_receiver neurons.

    def redirect_tests(self, bias, du, dv, spike_once, t, vth, spike_once_neurons):
        for some_neuron in spike_once_neurons:
            some_neuron_name = get_node_belonging_to_neuron_from_list(
                some_neuron, self.neurons, self.converted_nodes
            )
            print(f"t={t},some_neuron={some_neuron_name}")
            print_neuron_properties([some_neuron])
            if t == 1:
                self.asserts_for_spike_once_at_t_is_1(bias, du, dv, some_neuron, vth)
            elif t == 2:
                self.asserts_for_spike_once_at_t_is_2(bias, du, dv, some_neuron, vth)
            elif t == 3:
                self.asserts_for_spike_once_at_t_is_3(bias, du, dv, some_neuron, vth)
            elif t == 4:
                self.asserts_for_spike_once_at_t_is_4(bias, du, dv, some_neuron, vth)
            elif t > 4:
                self.asserts_for_spike_once_at_t_is_larger_than_4(
                    bias, du, dv, some_neuron, vth
                )

    def asserts_for_spike_once_at_t_is_0(self, bias, du, dv, spike_once, vth):
        """Assert the values of the spike_once neuron on t=0."""
        self.assertEqual(spike_once.u.get(), 0)  # Default initial value.
        self.assertEqual(spike_once.du.get(), du)  # Custom value.
        self.assertEqual(spike_once.v.get(), 0)  # Default initial value.
        self.assertEqual(spike_once.dv.get(), dv)  # Default initial value.
        self.assertEqual(spike_once.bias.get(), bias)  # Custom value.
        self.assertEqual(spike_once.vth.get(), vth)  # Default value.

    def asserts_for_spike_once_at_t_is_1(self, bias, du, dv, spike_once, vth):
        """Assert the values of the spike_once neuron on t=1. t=1 occurs after
        one timestep."""

        # u[t=1]=u[t=0]*(1-0)+a_in
        # u[t=1]=0*(1-0)+0
        # u[t=1]=0*1+0
        # u[t=1]=0
        self.assertEqual(spike_once.u.get(), 0)
        # v[t=1] = v[t=0] * (1-dv) + u[t=0] + bias
        # v[t=1] = 0 * (1-2) + 0 + 2
        # v[t=1]_before_spike = 2
        # SPIKES! After spiking, it goes back to 0 [V]:
        # v[t=1]_after_spike = 0
        self.assertEqual(spike_once.v.get(), 0)

        self.assertEqual(spike_once.du.get(), du)  # Custom Value.
        self.assertEqual(spike_once.dv.get(), dv)  # Custom value.
        self.assertEqual(spike_once.bias.get(), bias)  # Custom value.
        self.assertEqual(spike_once.vth.get(), vth)  # Default value.

    def asserts_for_spike_once_at_t_is_2(self, bias, du, dv, spike_once, vth):
        """Assert the values of the spike_once neuron on t=2."""

        # u[t=2]=u[t=1]*(1-du)+a_in
        # u[t=2]=0*(1-0)+-2
        # u[t=2]=0*1-2
        # u[t=2]=-2
        self.assertEqual(spike_once.u.get(), -2)
        # v[t=2] = v[t=1] * (1-dv) + u[t=0] + bias
        # v[t=1]_before_spike = 2
        # v[t=1]_after_spike = 0
        # v[t=2] = 0 * (1-2) + -2 + 2
        # v[t=2] = 0
        self.assertEqual(spike_once.v.get(), 0)

        self.assertEqual(spike_once.du.get(), du)  # Custom Value.
        self.assertEqual(spike_once.dv.get(), dv)  # Custom value.
        self.assertEqual(spike_once.bias.get(), bias)  # Custom value.
        self.assertEqual(spike_once.vth.get(), vth)  # Default value.

    def asserts_for_spike_once_at_t_is_3(self, bias, du, dv, spike_once, vth):
        """Assert the values of the spike_once neuron on t=3."""

        # u[t=3]=u[t=2]*(1-du)+a_in
        # u[t=3]=-2*(1-0)-0
        # u[t=3]=-2*1-0
        # u[t=3]=-2
        self.assertEqual(spike_once.u.get(), -2)
        # v[t=3] = v[t=2] * (1-dv) + u[t=2] + bias
        # v[t=3] = 0 * (1-0) -2 + 2
        # v[t=3] = 0
        self.assertEqual(spike_once.v.get(), 0)

        self.assertEqual(spike_once.du.get(), du)  # Custom Value.
        self.assertEqual(spike_once.dv.get(), dv)  # Custom value.
        self.assertEqual(spike_once.bias.get(), bias)  # Custom value.
        self.assertEqual(spike_once.vth.get(), vth)  # Default value.

    def asserts_for_spike_once_at_t_is_4(self, bias, du, dv, spike_once, vth):
        """Assert the values of the spike_once neuron on t=4."""

        # u[t=4]=u[t=3]*(1-du)+a_in
        # u[t=4]=0*(1-0)-1
        # u[t=4]=-2
        self.assertEqual(spike_once.u.get(), -2)
        # v[t=4] = v[t=3] * (1-dv) + u[t=2] + bias
        # v[t=4] = 0 * (1-0) -2 + 2
        # v[t=4] = 0
        self.assertEqual(spike_once.v.get(), 0)

        self.assertEqual(spike_once.du.get(), du)  # Custom Value.
        self.assertEqual(spike_once.dv.get(), dv)  # Custom value.
        self.assertEqual(spike_once.bias.get(), bias)  # Custom value.
        self.assertEqual(spike_once.vth.get(), vth)  # Default value.

    def asserts_for_spike_once_at_t_is_larger_than_4(
        self, bias, du, dv, spike_once, vth
    ):
        """Assert the values of the spike_once neuron on t=4."""
        # The current stays constant indefinitely.
        # u[t=x+1]=u[t=x]*(1-du)+a_in
        # u[t=x+1]=0*(1-0)-1
        # u[t=x+1]=-2
        self.assertEqual(spike_once.u.get(), -2)
        # The voltage stays constant indefinitely because the current
        # stays constant indefinitely whilst cancelling out the bias.
        # v[t=x+1] = v[t=x] * (1-dv) + u[t=2] + bias
        # v[t=x+1] = 0 * (1-0) -2 + 2
        # v[t=x+1] = 0
        self.assertEqual(spike_once.v.get(), 0)

        self.assertEqual(spike_once.du.get(), du)  # Custom Value.
        self.assertEqual(spike_once.dv.get(), dv)  # Custom value.
        self.assertEqual(spike_once.bias.get(), bias)  # Custom value.
        self.assertEqual(spike_once.vth.get(), vth)  # Default value.
