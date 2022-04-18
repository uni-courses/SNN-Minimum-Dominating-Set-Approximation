# TODO: move to separate ?test_?contains_neurons.py
def all_selector_neurons_are_present_in_snn(
    test_object, converted_nodes, G, get_degree, neurons
):
    """Assumes neurons are named degree_receiver_<index>. Where index represents
    the number of the node in the original graph G that they represent."""
    # Assert for each node in graph G, that a degree_receiver node exists in
    # get_degree.
    for node in G.nodes:
        test_object.assertTrue(f"selector_{node}" in get_degree.nodes)

    # Assert no more than n degree_receiver nodes exist in get_degree.
    test_object.assertEqual(
        sum("selector" in string for string in get_degree.nodes), 4
    )  # manual assert for fully connected graph of n=4.
    test_object.assertEqual(
        sum("selector" in string for string in get_degree.nodes),
        len(G),
    )

    # Write a function that verifies n neurons exist with the
    # selector properties.
    (has_n_selector_neurons, selector_neurons,) = neurons_contain_n_selector_neurons(
        test_object.bias,
        test_object.du,
        test_object.dv,
        neurons,
        len(G),
        test_object.vth,
    )
    test_object.assertTrue(has_n_selector_neurons)
    return selector_neurons


def neurons_contain_n_selector_neurons(bias, du, dv, neurons, n, vth):
    """Verifies at least n neurons exist with the selector properties."""
    selector_neurons = []
    for neuron in neurons:

        # Check if neuron has the correct properties.
        bool_selector_neuron = is_selector_neuron(bias, du, dv, neuron, vth)

        if bool_selector_neuron:
            # TODO: Verify a selector neuron has a recurrent synaptic
            # connection to ittest_object.with weight -2.
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
