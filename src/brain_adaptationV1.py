# Tests wether the signal of a spike-once neuron is received at the receiving
#  neuron if the spike-once neuron dies. To realise this robustness, a
# redunant neuron is created that is inhibited if the primary neuron fires.
# If the redundant neuron is not inhibited, it sends the signal the spike_once
# neuron would have sent, to the receiving neuron.

from math import inf
from pprint import pprint

import numpy as np

# Instantiate Lava processes to build network
from lava.proc.dense.process import Dense
from lava.proc.lif.process import LIF
from lava.magma.core.process.variable import Var

from lava.magma.core.run_conditions import RunSteps
from lava.magma.core.run_configs import Loihi1SimCfg


def create_two_neurons_without_redundant_neuron():
    """Creates 2 neurons that with a synapse inbetween and add a redundant
    neuron."""
    # Create excitatory and inhibitory synapses that are re-used.
    excit_spike_once_receiver = create_weighted_synapse(2)
    inhib_spike_once_spike_once = create_weighted_synapse(-2)

    # Create neuron that spikes once and then inhibits itself.
    # Implement neuron death by setting vth to inf, meaning it won't spike.
    spike_once = LIF(du=0, dv=0, bias=2, vth=1)

    # Create receiving neuron, spikes if it gets an input of 2 or higher.
    receiver = LIF(du=0, dv=0, bias=0, vth=1)

    # Create recurrent inhibitory connection to make spike_once spike only once.
    spike_once = connect_synapse(spike_once, spike_once, inhib_spike_once_spike_once)

    # Connect spike_once with receiving neuron
    spike_once = connect_synapse(spike_once, receiver, excit_spike_once_receiver)

    return spike_once, receiver


def create_two_neurons_with_one_redundant_neuron():
    """Creates 2 neurons that with a synapse inbetween and add a redundant
    neuron."""
    # Create excitatory and inhibitory synapses that are re-used.
    excit_spike_once_receiver = create_weighted_synapse(2)
    excit_redundant_spike_once_receiver = create_weighted_synapse(2)
    inhib_redundant_spike_once_redundant_spike_once = create_weighted_synapse(-2)
    inhib_spike_once_redundant_spike_once = create_weighted_synapse(-2)

    # Create neuron that spikes once and then inhibits itself.
    # Implement neuron death by setting vth to inf, meaning it won't spike.
    spike_once = LIF(du=0, dv=0, bias=2, vth=inf)

    # Create redundant spike_once neuron
    redundant_spike_once = LIF(du=0, dv=0, bias=2, vth=3)

    # Create receiving neuron, spikes if it gets an input of 2 or higher.
    receiver = LIF(du=0, dv=0, bias=0, vth=1)

    # Create recurrent inhibitory connection to make spike_once spike only once.
    redundant_spike_once = connect_synapse(
        redundant_spike_once,
        redundant_spike_once,
        inhib_redundant_spike_once_redundant_spike_once,
    )

    # Connect spike_once with receiving neuron
    spike_once = connect_synapse(spike_once, receiver, excit_spike_once_receiver)

    # Connect spike_once with redundant neuron
    spike_once = connect_synapse(
        spike_once, redundant_spike_once, inhib_spike_once_redundant_spike_once
    )

    # Connect spike_once with redundant neuron
    redundant_spike_once = connect_synapse(
        redundant_spike_once, receiver, excit_redundant_spike_once_receiver
    )

    # receiver = connect_synapse( receiver ,third_neuron, dense)
    return spike_once, receiver, redundant_spike_once


def create_weighted_synapse(w):
    """
    Creates a weighted synapse between neuron a and neuron b.
    """
    shape = (1, 1)
    # weights = np.random.randint(100, size=shape)
    weights = [[w]]  # Needs to be this shape for a 1-1 neuron connection.
    weight_exp = 2
    num_weight_bits = 7
    sign_mode = 1

    dense = Dense(
        shape=shape,
        weights=weights,
        weight_exp=weight_exp,
        num_weight_bits=num_weight_bits,
        sign_mode=sign_mode,
    )
    return dense


def connect_synapse(neuron_a, neuron_b, dense):
    """Connects a synapse named dense from neuron a to neuron b."""
    neuron_a.out_ports.s_out.connect(dense.in_ports.s_in)
    dense.out_ports.a_out.connect(neuron_b.in_ports.a_in)
    return neuron_a


# Create the snn networks.
(
    spike_once_with_redundancy,
    receiver_with_redundancy,
    redundant_spike_once,
) = create_two_neurons_with_one_redundant_neuron()

(
    spike_once_without_redundancy,
    receiver_without_redundancy,
) = create_two_neurons_without_redundant_neuron()


def run_snn(receiver_neuron, starter_neuron, t):
    # Run simulation for t seconds and print receiver u.
    for t in range(t):
        starter_neuron.run(condition=RunSteps(num_steps=1), run_cfg=Loihi1SimCfg())
        print(f"t={t},u={receiver_neuron.u.get()}")
    # Terminate Loihi simulation.
    starter_neuron.stop()


run_snn(receiver_without_redundancy, spike_once_without_redundancy, 10)
run_snn(receiver_with_redundancy, spike_once_with_redundancy, 10)
