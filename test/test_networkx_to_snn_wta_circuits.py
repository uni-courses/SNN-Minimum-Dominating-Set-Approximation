import unittest
import networkx as nx
from lava.magma.core.run_conditions import RunSteps
from lava.magma.core.run_configs import Loihi1SimCfg
from src.helper import (
    generate_list_of_n_random_nrs,
    get_a_in_with_random_neurons,
    get_node_and_neighbour_from_degree,
    is_degree_receiver,
)


from src.helper_network_structure import (
    get_degree_graph_with_rand_nodes,
    get_degree_graph_with_separate_wta_circuits,
    plot_coordinated_graph,
)
from src.helper_snns import print_neuron_properties
from src.networkx_to_snn import (
    convert_networkx_graph_to_snn_with_one_neuron,
    get_node_belonging_to_neuron_from_list,
)
from test.helper_tests import (
    a_in_spike_once,
    compute_expected_number_of_degree_receivers,
    neurons_contain_n_degree_receiver_neurons,
)


class Test_networkx_to_snn_degree_receiver_rand_neurons(unittest.TestCase):
    """
    Tests whether the networks that are fed into networkx_to_snn are generating
    the correct snn networks.
    """

    # Initialize test object
    def __init__(self, *args, **kwargs):
        super(Test_networkx_to_snn_degree_receiver_rand_neurons, self).__init__(
            *args, **kwargs
        )
        self.du = 0
        self.dv = 1
        self.bias = 0
        self.vth = 1
        # Generate a fully connected graph with n=4.
        self.G = nx.complete_graph(4)
        self.rand_range = len(self.G) + 120
        self.rand_nrs = generate_list_of_n_random_nrs(
            self.G, max=self.rand_range, seed=42
        )
        print(f"self.rand_nrs={self.rand_nrs}")
        # TODO: Include passing self.random_values for testing purposes as optional argument.
        # print(f"Incoming G")
        # plot_unstructured_graph(self.G)

        # Convert the fully connected graph into a networkx graph that
        # stores the snn properties to create an snn that computes the degree
        # in the number of spikes into the degree_receiver neurons.
        # TODO: Include passing self.random_values for testing purposes as optional argument.
        self.get_degree = get_degree_graph_with_separate_wta_circuits(
            self.G, self.rand_nrs
        )

        plot_coordinated_graph(self.get_degree)
        (
            self.converted_nodes,
            self.lhs_neuron,
            self.neurons,
            self.lhs_node,
            self.neuron_dict,
        ) = convert_networkx_graph_to_snn_with_one_neuron(
            self.get_degree, True, bias=0, du=0, dv=0, weight=1, vth=1
        )

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
            for neighbour in nx.all_neighbors(G, node):
                # print(f"node={node}")
                # print(f"get_degree.nodes={get_degree.nodes}")
                self.assertTrue(
                    f"degree_receiver_{node}_{neighbour}" in get_degree.nodes
                )

        # Assert no more than n degree_receiver nodes exist in get_degree.
        self.assertEqual(
            sum("degree_receiver" in string for string in get_degree.nodes), 4 * 3
        )  # manual assert for fully connected graph of n=4.
        self.assertEqual(
            sum("degree_receiver" in string for string in get_degree.nodes),
            compute_expected_number_of_degree_receivers(G),
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
            compute_expected_number_of_degree_receivers(G),
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
        self, bias, du, dv, starter_neuron, t, vth, degree_receiver_neurons
    ):
        for some_neuron in degree_receiver_neurons:
            neuron_name = self.neuron_dict[some_neuron]
            if is_degree_receiver(some_neuron, self.neuron_dict):

                wta_circuit, neighbour = get_node_and_neighbour_from_degree(neuron_name)
                print_neuron_properties([some_neuron])
                print(f"Printed neuron properties of:{self.neuron_dict[some_neuron]}")
                print(f"with degree_receiver={starter_neuron}")
                if t == 1:
                    self.asserts_for_degree_receiver_at_t_is_1(
                        bias, du, dv, some_neuron, vth
                    )
                elif t == 2:
                    self.asserts_for_degree_receiver_at_t_is_2(
                        bias, du, dv, some_neuron, vth, wta_circuit, neighbour
                    )
                elif t == 3:
                    self.asserts_for_degree_receiver_at_t_is_3(
                        bias, du, dv, some_neuron, vth, wta_circuit, neighbour
                    )
                elif t == 4:
                    self.asserts_for_degree_receiver_at_t_is_4(
                        bias, du, dv, some_neuron, vth, wta_circuit, neighbour
                    )
                elif t > 4:
                    self.asserts_for_degree_receiver_at_t_is_larger_than_4(
                        bias, du, dv, some_neuron, vth, wta_circuit, neighbour
                    )
            else:
                print(f"Not a degree_receiver neuron:{neuron_name}")
                exit()

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

    def asserts_for_degree_receiver_at_t_is_2(
        self, bias, du, dv, degree_receiver, vth, wta_circuit, neighbour
    ):
        """Assert the values of the degree_receiver neuron on t=2."""
        # Compute what the expected summed input spike values are.
        a_in = get_a_in_with_random_neurons(
            self.G, neighbour, wta_circuit, self.rand_nrs, multiplier=1
        )
        print(f"self.rand_nrs={self.rand_nrs}")
        print(f"wta_circuit={wta_circuit}")
        print(f"neighbour={neighbour}")
        print(f"a_in={a_in}")
        # u[t=2]=u[t=1]*(1-du)+a_in, a_in=
        # u[t=2]=0*(1-1)+0
        # u[t=2]=0*0+0
        # u[t=2]=-0
        print(f"degree_receiver={degree_receiver}")
        # TODO: determine why the u.get is 15+3=18 V=degree_receiver_3_1 (or degree_receiver_2_1)
        # instead of degree_receiver_3_0=82+3=85 as computed by a_in.
        # TODO: verify whether degree_receiver is the correct neuron.
        self.assertEqual(degree_receiver.u.get(), a_in)
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

    def asserts_for_degree_receiver_at_t_is_3(
        self, bias, du, dv, degree_receiver, vth, wta_circuit, neighbour
    ):
        """Assert the values of the degree_receiver neuron on t=3."""
        a_in = get_a_in_with_random_neurons(
            self.G, neighbour, wta_circuit, self.rand_nrs, multiplier=1
        )
        # u[t=3]=u[t=2]*(1-du)+a_in
        # u[t=3]=3*(1-0)-0
        # u[t=3]=3*1-0
        # u[t=3]=3
        self.assertEqual(degree_receiver.u.get(), a_in)
        # v[t=3] = v[t=2] * (1-dv) + u[t=2] + bias
        # v[t=3] = 0 * (1-0) -2 + 2
        # v[t=3] = 0
        self.assertEqual(degree_receiver.v.get(), 0)

        self.assertEqual(degree_receiver.du.get(), du)  # Custom Value.
        self.assertEqual(degree_receiver.dv.get(), dv)  # Custom value.
        self.assertEqual(degree_receiver.bias.get(), bias)  # Custom value.
        self.assertEqual(degree_receiver.vth.get(), vth)  # Default value.

    def asserts_for_degree_receiver_at_t_is_4(
        self, bias, du, dv, degree_receiver, vth, wta_circuit, neighbour
    ):
        """Assert the values of the degree_receiver neuron on t=4."""
        a_in = get_a_in_with_random_neurons(
            self.G, neighbour, wta_circuit, self.rand_nrs, multiplier=1
        )
        # u[t=4]=u[t=3]*(1-du)+a_in
        # u[t=4]=3*(1-0)+0
        # u[t=4]=3
        self.assertEqual(degree_receiver.u.get(), a_in)
        # v[t=4] = v[t=3] * (1-dv) + u[t=2] + bias
        # v[t=4] = 0 * (1-0) -2 + 2
        # v[t=4] = 0
        self.assertEqual(degree_receiver.v.get(), 0)

        self.assertEqual(degree_receiver.du.get(), du)  # Custom Value.
        self.assertEqual(degree_receiver.dv.get(), dv)  # Custom value.
        self.assertEqual(degree_receiver.bias.get(), bias)  # Custom value.
        self.assertEqual(degree_receiver.vth.get(), vth)  # Default value.

    def asserts_for_degree_receiver_at_t_is_larger_than_4(
        self, bias, du, dv, degree_receiver, vth, wta_circuit, neighbour
    ):
        """Assert the values of the degree_receiver neuron on t=4."""
        a_in = get_a_in_with_random_neurons(
            self.G, neighbour, wta_circuit, self.rand_nrs, multiplier=1
        )
        # The current stays constant indefinitely.
        # u[t=x+1]=u[t=x]*(1-du)+a_in
        # u[t=x+1]=3*(1-0)+0
        # u[t=x+1]=3
        self.assertEqual(degree_receiver.u.get(), a_in)
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
