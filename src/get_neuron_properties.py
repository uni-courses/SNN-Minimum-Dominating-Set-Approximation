def neuron_spikes_at_t(get_degree, t, node_name):
    # Initialise new a_in for a time step.

    # Compute whether the neuron spikes or not.
    if t == 0:
        # Create dictionary with int t as key and bool spike as value.

        # Neurons can only spike after being simulated for 1 timestep, so
        # initialise to False.
        spikes = False
    elif t == 1:
        # No spikes have come in yet at t=1, so a_in is 0. Compute
        # whether or not the neuron spikes based on its init properties.
        pass
    elif t > 1:
        # Get the incoming edges to the neuron.
        # Get the left/input neurons of the incoming edges.
        # Check if the input neuron spiked in the previous round (t-1)
        pass
        # If input neuron spiked, compute the synaptic/edge weight and add it to a_in

    # Store the spike in a dictionary with t as keys in the node.
