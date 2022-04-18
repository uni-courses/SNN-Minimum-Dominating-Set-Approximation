import unittest
import networkx as nx
from lava.magma.core.run_conditions import RunSteps
from lava.magma.core.run_configs import Loihi1SimCfg
from src.create_planar_triangle_free_graph import create_manual_graph_with_4_nodes
from src.helper import (
    generate_list_of_n_random_nrs,
    get_a_in_for_selector_neuron_retry,
    get_node_from_selector_neuron_name,
    is_selector_neuron_dict,
    print_degree_neurons,
)

from src.helper_network_structure import (
    get_degree_graph_with_separate_wta_circuits,
    plot_coordinated_graph,
    plot_unstructured_graph,
)
from src.networkx_to_snn import (
    convert_networkx_graph_to_snn_with_one_neuron,
)


class Test_selector(unittest.TestCase):
    """
    Tests whether the networks that are fed into networkx_to_snn are generating
    the correct snn networks.
    """

    # Initialize test object
    def __init__(self, *args, **kwargs):
        super(Test_selector, self).__init__(*args, **kwargs)

        ## Specify the expected neuron properties.
        # TODO: change this to make it a function of
        self.du = 0
        self.dv = 1
        self.bias = 5
        self.vth = 4

        ## Specify the expected synaptic weights
        # TODO: Specify per synapse group. (except for the random synapses)
        self.incoming_selector_weight = -5

        ## Generate the graph on which the algorithm is ran.
        #  Generate a fully connected graph with n=4.
        self.G = nx.complete_graph(4)
        # self.G = create_manual_graph_with_4_nodes()
        plot_unstructured_graph(self.G)

        ## Generate the maximum random ceiling
        # +2 to allow selecting a larger range of numbers than the number of
        # nodes in the graph.
        self.rand_ceil = len(self.G) + 2
        # Get the list of random numbers.
        self.rand_nrs = generate_list_of_n_random_nrs(
            self.G, max=self.rand_ceil, seed=42
        )
        print(f"before={self.rand_nrs}")
        # Make the random numbers differ with at least delta>=2. This is to
        # prevent multiple degree_receiver_x_y neurons (that differ less than
        # delta) in a single WTA circuit to spike before they are inhibited by
        # the first winner. This inhibition goes via the selector neuron and
        # has a delay of 2. So a winner should have a difference of at least 2.
        self.delta = 2
        # Spread the random numbers with delta to ensure 1 winner in WTA
        # circuit.
        self.rand_nrs = [x * self.delta for x in self.rand_nrs]
        print(f"after_delta={self.rand_nrs}")
        # Add inhibition to rand_nrs to ensure the degree_receiver current u[1]
        # always starts negative. The a_in of the degree_receiver_x_y neuron is
        # : the incoming spike_once_x weights+rand_x neurons+selector_excitation
        # - There are at most n incoming spike signals.
        # - Each spike_once should have a weight of at least random_ceiling.
        # That is because the random value should map to 0<rand<1 with respect
        # to the difference of 1 spike_once more or less.
        # - The random_ceiling is specified.
        # - The excitatory neuron comes in at +1, a buffer of 1 yields+2.
        # Hence, the inhibition is computed as:
        self.inhibition = len(self.G) * self.rand_ceil + self.rand_ceil + 2
        self.rand_nrs = [x - self.inhibition for x in self.rand_nrs]
        print(f"After inhibition of:{self.inhibition}, rand_nrs={self.rand_nrs}")

        ## Convert the fully connected graph into a networkx graph that
        # stores the snn properties.
        self.get_degree = get_degree_graph_with_separate_wta_circuits(
            self.G, self.rand_nrs
        )
        plot_unstructured_graph(self.get_degree)
        plot_coordinated_graph(self.get_degree)

        ## Convert the snn networkx graph into a Loihi implementation.
        (
            self.converted_nodes,
            self.lhs_neuron,
            self.neurons,
            self.lhs_node,
            self.neuron_dict,
        ) = convert_networkx_graph_to_snn_with_one_neuron(
            self.get_degree, True, bias=0, du=0, dv=0, weight=1, vth=1
        )

    def test_selector_neurons_in_get_degree(
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
        selector_neurons = self.all_selector_neurons_are_present_in_snn(
            self.converted_nodes, self.G, self.get_degree, self.neurons
        )

        # Simulate SNN and assert values inbetween timesteps.
        starter_neuron = selector_neurons[0]
        for t in range(1, 100):

            # Run the simulation for 1 timestep.
            starter_neuron.run(condition=RunSteps(num_steps=1), run_cfg=Loihi1SimCfg())
            # Print the values coming into the timestep.
            # Assert neuron values.
            self.redirect_tests(
                self.bias,
                self.du,
                self.dv,
                starter_neuron,
                t,
                self.vth,
                selector_neurons,
            )

        starter_neuron.stop()

        # TODO: Assert the neuron properties for the degree_receiver neurons are
        # correct at t>0

    def all_selector_neurons_are_present_in_snn(
        self, converted_nodes, G, get_degree, neurons
    ):
        """Assumes neurons are named degree_receiver_<index>. Where index represents
        the number of the node in the original graph G that they represent."""
        # Assert for each node in graph G, that a degree_receiver node exists in
        # get_degree.
        for node in G.nodes:
            self.assertTrue(f"selector_{node}" in get_degree.nodes)

        # Assert no more than n degree_receiver nodes exist in get_degree.
        self.assertEqual(
            sum("selector" in string for string in get_degree.nodes), 4
        )  # manual assert for fully connected graph of n=4.
        self.assertEqual(
            sum("selector" in string for string in get_degree.nodes),
            len(G),
        )

        # Write a function that verifies n neurons exist with the
        # selector properties.
        (
            has_n_selector_neurons,
            selector_neurons,
        ) = neurons_contain_n_selector_neurons(
            self.bias,
            self.du,
            self.dv,
            neurons,
            len(G),
            self.vth,
        )
        self.assertTrue(has_n_selector_neurons)

        # TODO: Verify they have the correct amount of outgoing synapses.
        # This is currently tested implicitly by checking the degree_receiver
        # behaviour over time.

        # TODO: Verify the outgoing synapses have the correct weight.

        # TODO: Subtract those neurons from neuron group and return reduced
        #  group for remainder of tests.
        return selector_neurons

    def redirect_tests(self, bias, du, dv, starter_neuron, t, vth, selector_neurons):
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
                        bias, du, dv, selector_neuron, vth
                    )
                elif t == 2:
                    self.asserts_for_selector_at_t_is_2(
                        bias,
                        du,
                        dv,
                        selector_neuron,
                        t,
                        vth,
                        wta_circuit,
                    )
                elif t == 3:
                    self.asserts_for_selector_at_t_is_3(
                        bias,
                        du,
                        dv,
                        selector_neuron,
                        t,
                        vth,
                        wta_circuit,
                    )
                elif t == 4:
                    self.asserts_for_selector_at_t_is_4(
                        bias,
                        du,
                        dv,
                        selector_neuron,
                        t,
                        vth,
                        wta_circuit,
                    )
                elif t > 4:
                    self.asserts_for_selector_at_t_is_larger_than_4(
                        bias,
                        du,
                        dv,
                        selector_neuron,
                        t,
                        vth,
                        wta_circuit,
                    )
            else:
                print(f"Not a degree_receiver neuron:{selector_neuron_name}")
                exit()

    def asserts_for_selector_at_t_is_0(self, bias, du, dv, selector_neuron, vth):
        """Assert the values of the selector_neuron neuron on t=0."""
        self.assertEqual(selector_neuron.u.get(), 0)  # Default initial value.
        self.assertEqual(selector_neuron.du.get(), 0)  # Custom value.
        self.assertEqual(selector_neuron.v.get(), 0)  # Default initial value.
        self.assertEqual(selector_neuron.dv.get(), dv)  # Default initial value.
        self.assertEqual(selector_neuron.bias.get(), bias)  # Custom value.
        self.assertEqual(selector_neuron.vth.get(), vth)  # Default value.

    def asserts_for_selector_at_t_is_1(self, bias, du, dv, selector_neuron, vth):
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

        self.assertEqual(selector_neuron.du.get(), du)  # Custom Value.
        self.assertEqual(selector_neuron.dv.get(), dv)  # Custom value.
        self.assertEqual(selector_neuron.bias.get(), bias)  # Custom value.
        self.assertEqual(selector_neuron.vth.get(), vth)  # Default value.

    def asserts_for_selector_at_t_is_2(
        self, bias, du, dv, selector_neuron, t, vth, wta_circuit
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

        self.assertEqual(selector_neuron.du.get(), du)  # Custom Value.
        self.assertEqual(selector_neuron.dv.get(), dv)  # Custom value.
        self.assertEqual(selector_neuron.bias.get(), bias)  # Custom value.
        self.assertEqual(selector_neuron.vth.get(), vth)  # Default value.

    def asserts_for_selector_at_t_is_3(
        self,
        bias,
        du,
        dv,
        selector_neuron,
        t,
        vth,
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

        self.assertEqual(selector_neuron.du.get(), du)  # Custom Value.
        self.assertEqual(selector_neuron.dv.get(), dv)  # Custom value.
        self.assertEqual(selector_neuron.bias.get(), bias)  # Custom value.
        self.assertEqual(selector_neuron.vth.get(), vth)  # Default value.

    def asserts_for_selector_at_t_is_4(
        self, bias, du, dv, selector_neuron, t, vth, wta_circuit
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

        self.assertEqual(selector_neuron.du.get(), du)  # Custom Value.
        self.assertEqual(selector_neuron.dv.get(), dv)  # Custom value.
        self.assertEqual(selector_neuron.bias.get(), bias)  # Custom value.
        self.assertEqual(selector_neuron.vth.get(), vth)  # Default value.

    def asserts_for_selector_at_t_is_larger_than_4(
        self, bias, du, dv, selector_neuron, t, vth, wta_circuit
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
        if bias + selector_neuron.u.get() > 1:
            expected_voltage = 0  # It spikes
        elif selector_neuron.u.get() < self.incoming_selector_weight:
            expected_voltage = bias + selector_neuron.u.get()  # no spike
        else:
            expected_voltage = bias + selector_neuron.u.get()  # no spike
        # expected_voltage = get_expected_voltage_of_first_spike(self.rand_nrs, t, a_in)
        # print(f"expected_voltage={expected_voltage}")
        # self.assertEqual(selector_neuron.v.get(), selector_neuron.u.get())
        self.assertEqual(selector_neuron.v.get(), expected_voltage)

        self.assertEqual(selector_neuron.du.get(), du)  # Custom Value.
        self.assertEqual(selector_neuron.dv.get(), dv)  # Custom value.
        self.assertEqual(selector_neuron.bias.get(), bias)  # Custom value.
        self.assertEqual(selector_neuron.vth.get(), vth)  # Default value.


def neurons_contain_n_selector_neurons(bias, du, dv, neurons, n, vth):
    """Verifies at least n neurons exist with the selector properties."""
    selector_neurons = []
    for neuron in neurons:

        # Check if neuron has the correct properties.
        bool_selector_neuron = is_selector_neuron(bias, du, dv, neuron, vth)

        if bool_selector_neuron:
            # TODO: Verify a selector neuron has a recurrent synaptic
            # connection to itself with weight -2.
            selector_neurons.append(neuron)

    if len(selector_neurons) == n:
        return True, selector_neurons
    else:
        print(f"len(selector_neurons)={len(selector_neurons)}")
        return False, selector_neurons


def is_selector_neuron(bias, du, dv, neuron, vth):
    """Assert the values of the selector neuron on t=0."""
    if neuron.u.get() == 0:  # Default initial value.
        if neuron.du.get() == du:  # Custom value.
            if neuron.v.get() == 0:  # Default initial value.
                if neuron.dv.get() == dv:  # Default initial value.
                    if neuron.bias.get() == bias:  # Custom value.
                        if neuron.vth.get() == vth:  # Default value.
                            return True
                        else:
                            print(
                                f"neuron.vth.get()={neuron.vth.get()}, whereas vth={vth}"
                            )
                    else:
                        print(
                            f"neuron.bias.get()={neuron.bias.get()}, whereas bias={bias}"
                        )
                else:
                    print(f"neuron.dv.get()={neuron.dv.get()}, whereas dv={dv}")
            else:
                print(f"neuron.v.get()={neuron.v.get()}, whereas v={v}")
        else:
            print(f"neuron.du.get()={neuron.du.get()}, whereas du={du}")
    else:
        print(f"neuron.u.get()={neuron.u.get()}, whereas u={0}")
    return False
