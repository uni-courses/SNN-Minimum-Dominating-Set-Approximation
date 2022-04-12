import unittest
import networkx as nx
from lava.magma.core.run_conditions import RunSteps
from lava.magma.core.run_configs import Loihi1SimCfg


from src.helper_network_structure import get_degree_graph, plot_graph
from src.helper_snns import print_neuron_properties
from src.networkx_to_snn import (
    convert_networkx_graph_to_snn_with_one_neuron,
    get_node_belonging_to_neuron_from_list,
)
from test.helper_tests import a_in_spike_once, neurons_contain_n_degree_receiver_neurons


class Test_networkx_to_snn_degree_receiver(unittest.TestCase):
    """
    Tests whether the networks that are fed into networkx_to_snn are generating
    the correct snn networks.
    """

    # Initialize test object
    def __init__(self, *args, **kwargs):
        super(Test_networkx_to_snn_degree_receiver, self).__init__(*args, **kwargs)
        self.du = 0
        self.dv = 1
        self.bias = 0
        self.vth = 1
        # Generate a fully connected graph with n=4.
        self.G = nx.complete_graph(4)
        # print(f"Incoming G")
        # plot_graph(self.G) # TODO: There can be only one function plot_graph.

        # Convert the fully connected graph into a networkx graph that
        # stores the snn properties to create an snn that computes the degree
        # in the number of spikes into the degree_receiver neurons.
        self.get_degree = get_degree_graph(self.G)
        (
            self.converted_nodes,
            self.lhs_neuron,
            self.neurons,
            self.lhs_node,
        ) = convert_networkx_graph_to_snn_with_one_neuron(
            self.get_degree, True, bias=0, du=0, dv=0, weight=1, vth=1
        )
        print(f"get_degree")
        plot_graph(self.get_degree)  # TODO: There can be only one function plot_graph.

    def testdegree_receiver_neurons_in_get_degree(
        self,
    ):
        """Tests whether the degree_receiver neurons are all present.
        Verifies the neuron initial properties at t=0.
        Verifies the neuron properties over time.
        Assumes a spike occurs at t=1 in the degree_receiver neurons.
        """
        # Asserts all degree_receiver neurons are present in snn, and:
        # Asserts the initial properties for the degree_receiver neurons are
        # correct at t=0.
        # TODO: include expected values in this test explicitly, instead of in
        # degree_receiver neuron.
        degree_receiver_neurons = self.all_degree_receiver_neurons_are_present_in_snn(
            self.converted_nodes, self.G, self.get_degree, self.neurons
        )

        # Simulate SNN and assert values inbetween timesteps.
        starter_neuron = degree_receiver_neurons[0]
        for t in range(1, 100):

            # Run the simulation for 1 timestep.
            starter_neuron.run(condition=RunSteps(num_steps=1), run_cfg=Loihi1SimCfg())
            # Print the values coming into the timestep.
            print(f"starter_neuron t={t}"), print_neuron_properties([starter_neuron])

            # Assert neuron values.
            self.redirect_tests(
                self.bias,
                self.du,
                self.dv,
                starter_neuron,
                t,
                self.vth,
                degree_receiver_neurons,
            )

        starter_neuron.stop()

        # TODO: Assert the neuron properties for the degree_receiver neurons are
        # correct at t>0

    def all_degree_receiver_neurons_are_present_in_snn(
        self, converted_nodes, G, get_degree, neurons
    ):
        """Assumes neurons are named degree_receiver_<index>. Where index represents
        the number of the node in the original graph G that they represent."""
        # Assert for each node in graph G, that a degree_receiver node exists in
        # get_degree.
        for node in G.nodes:
            # print(f"node={node}")
            # print(f"get_degree.nodes={get_degree.nodes}")
            self.assertTrue(f"degree_receiver_{node}" in get_degree.nodes)

        for node in converted_nodes:
            print(f"converted node={node}")

        # Assert no more than n degree_receiver nodes exist in get_degree.
        self.assertEqual(
            sum("degree_receiver" in string for string in get_degree.nodes), 4
        )
        self.assertEqual(
            sum("degree_receiver" in string for string in get_degree.nodes),
            len(G.nodes),
        )

        # Write a function that verifies n neurons exist with the
        # degree_receiver properties.
        (
            has_n_degree_receiver_neurons,
            degree_receiver_neurons,
        ) = neurons_contain_n_degree_receiver_neurons(
            self.bias,
            self.du,
            self.dv,
            neurons,
            len(G.nodes),
            self.vth,
        )
        self.assertTrue(has_n_degree_receiver_neurons)

        # TODO: Verify they have the correct amount of outgoing synapses.
        # This is currently tested implicitly by checking the degree_receiver
        # behaviour over time.

        # TODO: Verify the outgoing synapses have the correct weight.

        # TODO: Subtract those neurons from neuron group and return reduced
        #  group for remainder of tests.
        return degree_receiver_neurons

    def degree_receiver_neurons_in_get_degree(self, get_degree, t):
        """Tests whether the degree_receiver neurons are all present.
        Verifies the neuron initial properties at t=0.
        Verifies the neuron properties over time.
        Assumes a spike occurs at t=1 and comes in at t=2 in the degree_receiver
        neurons.
        """
        pass
        # TODO: Assert all degree_receiver neurons are present in the snn.

        # TODO: Assert the initial properties for the degree_receiver neurons are
        # correct at t=0.
        # TODO: Assert the current u(t) for the degree_receiver neurons is zero
        # at t=0.

        # TODO: Assert the current u(t) for the degree_receiver neurons is zero
        # at t=0.

        # TODO: Assert the degree_receiver neurons receive a spike at t=2
        # TODO: Assert the current u(t=2) of each.
        # degree_receiver neuron has the same value as the number of the
        # degrees that the node has that is represented by the respective
        # degree_receiver node.

        # TODO: Assert the neuron properties for the degree_receiver neurons are
        # correct at t>2.
        # TODO: assert the current u(t) of the degree_receiver neurons does not
        # increase after the initial spikes.

    def networkx_to_snn_weight_calculation(self):
        """
        TODO: create new test that verifies the incoming random spikes of
        neurons are added to the u(t) of the degree_receiver neurons.
        Verify that this also included the degree_receiver degree count in u(t).
        """
        pass

        # TODO: Write function that creates the random spiking neurons.
        # Specficy the range of their random values and use those as a
        # multiplication factor for the time window.
        # TODO: Assert the number of spikes is within the specified window.
        # TODO: Write function that creates the synapses between the
        # random spiking neurons and the degree_receiver neurons.

    def redirect_tests(
        self, bias, du, dv, degree_receiver, t, vth, degree_receiver_neurons
    ):
        for some_neuron in degree_receiver_neurons:
            some_neuron_name = get_node_belonging_to_neuron_from_list(
                some_neuron, self.neurons, self.converted_nodes
            )
            print(f"t={t},some_neuron={some_neuron_name}")
            print_neuron_properties([some_neuron])
        if t == 1:

            self.asserts_for_degree_receiver_at_t_is_1(
                bias, du, dv, degree_receiver, vth
            )
        elif t == 2:
            self.asserts_for_degree_receiver_at_t_is_2(
                bias, du, dv, degree_receiver, vth
            )
        elif t == 3:
            self.asserts_for_degree_receiver_at_t_is_3(
                bias, du, dv, degree_receiver, vth
            )
        elif t == 4:
            self.asserts_for_degree_receiver_at_t_is_4(
                bias, du, dv, degree_receiver, vth
            )
        elif t > 4:
            self.asserts_for_degree_receiver_at_t_is_larger_than_4(
                bias, du, dv, degree_receiver, vth
            )

    def asserts_for_degree_receiver_at_t_is_0(self, bias, du, dv, degree_receiver, vth):
        """Assert the values of the degree_receiver neuron on t=0."""
        self.assertEqual(degree_receiver.u.get(), 0)  # Default initial value.
        self.assertEqual(degree_receiver.du.get(), du)  # Custom value.
        self.assertEqual(degree_receiver.v.get(), 0)  # Default initial value.
        self.assertEqual(degree_receiver.dv.get(), dv)  # Default initial value.
        self.assertEqual(degree_receiver.bias.get(), bias)  # Custom value.
        self.assertEqual(degree_receiver.vth.get(), vth)  # Default value.

    def asserts_for_degree_receiver_at_t_is_1(self, bias, du, dv, degree_receiver, vth):
        """Assert the values of the degree_receiver neuron on t=1. t=1 occurs after
        one timestep."""

        # u[t=1]=u[t=0]*(1-1)+a_in
        # u[t=1]=0*(1-1)+0
        # u[t=1]=0*0+0
        # u[t=1]=0
        self.assertEqual(degree_receiver.u.get(), 0)
        # v[t=1] = v[t=0] * (1-dv) + u[t=0] + bias
        # v[t=1] = 0 * (1-1) + 0 + 0
        # v[t=1] = 0
        self.assertEqual(degree_receiver.v.get(), 0)

        self.assertEqual(degree_receiver.du.get(), du)  # Custom Value.
        self.assertEqual(degree_receiver.dv.get(), dv)  # Custom value.
        self.assertEqual(degree_receiver.bias.get(), bias)  # Custom value.
        self.assertEqual(degree_receiver.vth.get(), vth)  # Default value.

    def asserts_for_degree_receiver_at_t_is_2(self, bias, du, dv, degree_receiver, vth):
        """Assert the values of the degree_receiver neuron on t=2."""

        # u[t=2]=u[t=1]*(1-du)+a_in
        # u[t=2]=0*(1-1)+0
        # u[t=2]=0*0+0
        # u[t=2]=-0
        # TODO: get node index matching the neuron.
        # TODO: change expected value to degree of node.
        self.assertEqual(degree_receiver.u.get(), 3)
        # v[t=2] = v[t=1] * (1-dv) + u[t=0] + bias
        # v[t=1]_before_spike = 2
        # v[t=1]_after_spike = 0
        # v[t=2] = 0 * (1-2) + -2 + 2
        # v[t=2] = 0
        self.assertEqual(degree_receiver.v.get(), 0)

        self.assertEqual(degree_receiver.du.get(), du)  # Custom Value.
        self.assertEqual(degree_receiver.dv.get(), dv)  # Custom value.
        self.assertEqual(degree_receiver.bias.get(), bias)  # Custom value.
        self.assertEqual(degree_receiver.vth.get(), vth)  # Default value.

    def asserts_for_degree_receiver_at_t_is_3(self, bias, du, dv, degree_receiver, vth):
        """Assert the values of the degree_receiver neuron on t=3."""

        # u[t=3]=u[t=2]*(1-du)+a_in
        # u[t=3]=3*(1-0)-0
        # u[t=3]=3*1-0
        # u[t=3]=3
        self.assertEqual(degree_receiver.u.get(), 3)
        # v[t=3] = v[t=2] * (1-dv) + u[t=2] + bias
        # v[t=3] = 0 * (1-0) -2 + 2
        # v[t=3] = 0
        self.assertEqual(degree_receiver.v.get(), 0)

        self.assertEqual(degree_receiver.du.get(), du)  # Custom Value.
        self.assertEqual(degree_receiver.dv.get(), dv)  # Custom value.
        self.assertEqual(degree_receiver.bias.get(), bias)  # Custom value.
        self.assertEqual(degree_receiver.vth.get(), vth)  # Default value.

    def asserts_for_degree_receiver_at_t_is_4(self, bias, du, dv, degree_receiver, vth):
        """Assert the values of the degree_receiver neuron on t=4."""

        # u[t=4]=u[t=3]*(1-du)+a_in
        # u[t=4]=3*(1-0)+0
        # u[t=4]=3
        self.assertEqual(degree_receiver.u.get(), 3)
        # v[t=4] = v[t=3] * (1-dv) + u[t=2] + bias
        # v[t=4] = 0 * (1-0) -2 + 2
        # v[t=4] = 0
        self.assertEqual(degree_receiver.v.get(), 0)

        self.assertEqual(degree_receiver.du.get(), du)  # Custom Value.
        self.assertEqual(degree_receiver.dv.get(), dv)  # Custom value.
        self.assertEqual(degree_receiver.bias.get(), bias)  # Custom value.
        self.assertEqual(degree_receiver.vth.get(), vth)  # Default value.

    def asserts_for_degree_receiver_at_t_is_larger_than_4(
        self, bias, du, dv, degree_receiver, vth
    ):
        """Assert the values of the degree_receiver neuron on t=4."""
        # The current stays constant indefinitely.
        # u[t=x+1]=u[t=x]*(1-du)+a_in
        # u[t=x+1]=3*(1-0)+0
        # u[t=x+1]=3
        self.assertEqual(degree_receiver.u.get(), 3)
        # The voltage stays constant indefinitely because the current
        # stays constant indefinitely whilst cancelling out the bias.
        # v[t=x+1] = v[t=x] * (1-dv) + u[t=2] + bias
        # v[t=x+1] = 0 * (1-0) -2 + 2
        # v[t=x+1] = 0
        self.assertEqual(degree_receiver.v.get(), 0)

        self.assertEqual(degree_receiver.du.get(), du)  # Custom Value.
        self.assertEqual(degree_receiver.dv.get(), dv)  # Custom value.
        self.assertEqual(degree_receiver.bias.get(), bias)  # Custom value.
        self.assertEqual(degree_receiver.vth.get(), vth)  # Default value.
