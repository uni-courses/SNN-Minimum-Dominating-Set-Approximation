import networkx as nx


def a_in_spike_once(t):
    if t == 2:
        return 1
    else:
        return 0


def compute_expected_current(a_in, du, lif_neuron, previous_u):
    """Returns the expected current at timestep t."""
    expected_u = previous_u * (1 - du) + lif_neuron.u.get() + a_in
    return expected_u


def compute_expected_voltage(bias, dv, lif_neuron, previous_v):
    """Returns the expected voltage at timestep t."""
    expected_v = previous_v * (1 - dv) + lif_neuron.u.get() + bias
    return expected_v


def neurons_contain_n_spike_once_neurons(bias, du, dv, neurons, n, vth):
    """Verifies at least n neurons exist with the spike_once properties."""
    spike_once_neurons = []
    for neuron in neurons:

        # Check if neuron has the correct properties.
        bool_spike_once_neuron = is_spike_once_neuron(bias, du, dv, neuron, vth)

        if bool_spike_once_neuron:
            # TODO: Verify a spike_once neuron has a recurrent synaptic
            # connection to itself with weight -2.
            spike_once_neurons.append(neuron)

    if len(spike_once_neurons) == n:
        return True, spike_once_neurons
    else:
        print(f"len(spike_once_neurons)={len(spike_once_neurons)}")
        return False, spike_once_neurons


def is_spike_once_neuron(bias, du, dv, neuron, vth):
    """Assert the values of the spike_once neuron on t=0."""
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


def neurons_contain_n_degree_receiver_neurons(bias, du, dv, neurons, n, vth):
    """Verifies at least n neurons exist with the degree_receiver properties."""
    degree_receiver_neurons = []
    print(f"len(neurons)={len(neurons)}")
    for neuron in neurons:

        # Check if neuron has the correct properties.
        bool_degree_receiver_neuron = is_degree_receiver_neuron(
            bias, du, dv, neuron, vth
        )

        if bool_degree_receiver_neuron:
            # TODO: Verify a degree_receiver neuron has a recurrent synaptic
            # connection to itself with weight -2.
            degree_receiver_neurons.append(neuron)

    if len(degree_receiver_neurons) == n:
        return True, degree_receiver_neurons
    else:
        print(f"len(degree_receiver_neurons)={len(degree_receiver_neurons)}")
        return False, degree_receiver_neurons


def is_degree_receiver_neuron(bias, du, dv, neuron, vth):
    """Assert the values of the degree_receiver neuron on t=0."""
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


def compute_expected_number_of_degree_receivers(G):
    degree_receiver_count = 0
    for node in G.nodes:
        for neighbour in nx.all_neighbors(G, node):
            if node != neighbour:
                degree_receiver_count = degree_receiver_count + 1
    return degree_receiver_count
