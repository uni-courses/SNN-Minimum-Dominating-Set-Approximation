def compute_expected_current(a_in, du, lif_neuron, previous_u):
    """Returns the expected current at timestep t."""
    expected_u = previous_u * (1 - du) + lif_neuron.u.get() + a_in
    return expected_u


def compute_expected_voltage(bias, dv, lif_neuron, previous_v):
    """Returns the expected voltage at timestep t."""
    expected_v = previous_v * (1 - dv) + lif_neuron.u.get() + bias
    return expected_v
