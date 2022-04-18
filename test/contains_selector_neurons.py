# TODO: move to separate ?test_?contains_neurons.py
def all_selector_neurons_are_present_in_snn(
    test_object, converted_nodes, G, get_degree, neurons
):
    """
    Asserts all degree_receiver neurons are present in snn, and:
    Asserts the initial properties for the degree_receiver neurons are
    correct at t=0.
    Assumes neurons are named degree_receiver_<index>. Where index represents
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
    has_n_selector_neurons = neurons_contain_n_selector_neurons(
        test_object.sample_selector_neuron.bias,
        test_object.sample_selector_neuron.du,
        test_object.sample_selector_neuron.dv,
        neurons,
        len(G),
        test_object.sample_selector_neuron.vth,
    )
    test_object.assertTrue(has_n_selector_neurons)


def get_n_selector_neurons(neurons, n, sample_neuron):
    """Verifies at least n neurons exist with the selector properties."""
    selector_neurons = []
    for neuron in neurons:

        # Check if neuron has the correct properties.
        if has_expected_neuron_properties(neuron, sample_neuron):
            selector_neurons.append(neuron)

    if len(selector_neurons) == n:
        return selector_neurons
    else:
        raise Exception(f"len(selector_neurons)={len(selector_neurons)}")


def neurons_contain_n_selector_neurons(neurons, n, sample_neuron):
    """Verifies at least n neurons exist with the selector properties."""
    selector_neurons = []
    for neuron in neurons:

        # Check if neuron has the correct properties.
        if has_expected_neuron_properties(neuron, sample_neuron):
            selector_neurons.append(neuron)

    if len(selector_neurons) == n:
        return True
    else:
        print(f"len(selector_neurons)={len(selector_neurons)}")
        return False


def has_expected_neuron_properties(neuron, sample_neuron):
    """Assert the values of the incoming neuron are those of the expected
    neuron. Note sample_neuron does not have a sample_neuron.<property>.get()
    because it is a basic object with the properties stored as ints instead
    of with getters and setters."""
    if neuron.u.get() == 0:  # Default initial value.
        if neuron.du.get() == sample_neuron.du:  # Custom value.
            if neuron.v.get() == 0:  # Default initial value.
                if neuron.dv.get() == sample_neuron.dv:  # Default initial value.
                    if neuron.bias.get() == sample_neuron.bias:  # Custom value.
                        if neuron.vth.get() == sample_neuron.vth:  # Default value.
                            return True
                        else:
                            print(
                                f"neuron.vth.get()={neuron.vth.get()}, whereas expected vth={sample_neuron.vth}"
                            )
                    else:
                        print(
                            f"neuron.bias.get()={neuron.bias.get()}, whereas bias={sample_neuron.bias}"
                        )
                else:
                    print(
                        f"neuron.dv.get()={neuron.dv.get()}, whereas dv={sample_neuron.dv}"
                    )
            else:
                print(f"neuron.v.get()={neuron.v.get()}, whereas v={sample_neuron.v}")
        else:
            print(f"neuron.du.get()={neuron.du.get()}, whereas du={sample_neuron.du}")
    else:
        print(f"neuron.u.get()={neuron.u.get()}, whereas u={0}")
    return False
