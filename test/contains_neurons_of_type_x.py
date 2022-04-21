import networkx as nx

# TODO: move to separate ?test_?contains_neurons.py
def neurons_of_expected_type_are_all_present_in_snn(
    test_object,
    expected_amount,
    G,
    get_degree,
    neuron_dict,
    neuron_identifier,
    neurons,
    sample_neuron,
):
    """
    Asserts all degree_receiver neurons are present in snn, and:
    Asserts the initial properties for the degree_receiver neurons are
    correct at t=0.
    Assumes neurons are named degree_receiver_<index>. Where index represents
    the number of the node in the original graph G that they represent."""
    # Assert for each node in graph G, that a degree_receiver node exists in
    # get_degree.
    if neuron_identifier == "degree_receiver_":
        test_all_degree_receiver_neurons_are_in_graph(
            test_object, G, get_degree, neuron_identifier
        )
    else:
        for node in G.nodes:
            test_object.assertTrue(f"{neuron_identifier}{node}" in get_degree.nodes)
    # Assert no more than n degree_receiver nodes exist in get_degree.
    test_object.assertEqual(
        sum(neuron_identifier in string for string in get_degree.nodes), expected_amount
    )  # manual assert for fully connected graph of n=4.

    # Write a function that verifies n neurons exist with the
    # sample_neuron properties.
    test_object.assertTrue(
        has_n_neurons_of_sample_type(
            expected_amount, neurons, neuron_dict, neuron_identifier, sample_neuron
        )
    )


def test_all_degree_receiver_neurons_are_in_graph(
    test_object, G, get_degree, neuron_identifier
):
    for node in G.nodes:
        for neighbour in nx.all_neighbors(G, node):
            if node != neighbour:
                test_object.assertTrue(
                    f"{neuron_identifier}{node}_{neighbour}" in get_degree.nodes
                )


def has_n_neurons_of_sample_type(
    expected_amount, neurons, neuron_dict, neuron_identifier, sample_neuron
):
    """Verifies at least n neurons exist with the selector properties."""
    expected_neurons = []
    for neuron in neurons:

        # Check if neuron has the correct properties.
        if has_expected_neuron_properties(neuron, sample_neuron):
            # Check if the name of the neuron is correct.
            if neuron_has_expected_name(neuron, neuron_dict, neuron_identifier):
                expected_neurons.append(neuron)

    if len(expected_neurons) == expected_amount:
        return True
    else:
        print(f"len(expected_neurons)={len(expected_neurons)}")
        return False


def get_n_neurons(n, neurons, neuron_dict, neuron_identifier, sample_neuron):
    """Verifies at least n neurons exist with the sample_neuron properties."""
    expected_neurons = []
    for neuron in neurons:

        # Check if neuron has the correct properties.
        if has_expected_neuron_properties(neuron, sample_neuron):

            # Check if the name of the neuron is correct.
            if neuron_has_expected_name(neuron, neuron_dict, neuron_identifier):
                expected_neurons.append(neuron)

    if len(expected_neurons) == n:
        return expected_neurons
    else:
        raise Exception(f"len(expected_neurons)={len(expected_neurons)}")


def neuron_has_expected_name(neuron, neuron_dict, neuron_identifier):
    if neuron_dict[neuron][: len(neuron_identifier)] == neuron_identifier:
        return True
    else:
        print(
            f"neuron_dict[neuron][:len(neuron_identifier)]={neuron_dict[neuron][:len(neuron_identifier)]}"
        )
        return False


def has_expected_neuron_properties(neuron, sample_neuron, verbose=False):
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
                        elif verbose:
                            print(
                                f"neuron.vth.get()={neuron.vth.get()}, whereas expected vth={sample_neuron.vth}"
                            )
                    elif verbose:
                        print(
                            f"neuron.bias.get()={neuron.bias.get()}, whereas bias={sample_neuron.bias}"
                        )
                elif verbose:
                    print(
                        f"neuron.dv.get()={neuron.dv.get()}, whereas dv={sample_neuron.dv}"
                    )
            elif verbose:
                print(f"neuron.v.get()={neuron.v.get()}, whereas v={sample_neuron.v}")
        elif verbose:
            print(f"neuron.du.get()={neuron.du.get()}, whereas du={sample_neuron.du}")
    elif verbose:
        print(f"neuron.u.get()={neuron.u.get()}, whereas u={0}")
    return False
