# Tests wether the signal of a spike-once neuron is received at the receiving
#  neuron if the spike-once neuron dies. To realise this robustness, a
# redunant neuron is created that is inhibited if the primary neuron fires.
# If the redundant neuron is not inhibited, it sends the signal the spike_once
# neuron would have sent, to the receiving neuron.

from pprint import pprint

import numpy as np

# Instantiate Lava processes to build network
from lava.proc.dense.process import Dense
from lava.proc.lif.process import LIF
from lava.magma.core.process.variable import Var

from lava.magma.core.run_conditions import RunSteps
from lava.magma.core.run_configs import Loihi1SimCfg


def create_two_neurons_with_one_redundant_neuron():
    """Creates 2 neurons that with a synapse inbetween and add a redundant
    neuron."""
    # Create excitatory and inhibitory synapses that are re-used.
    excit_spike_once_receiver = create_weighted_synapse(2)
    excit_redundant_spike_once_receiver = create_weighted_synapse(2)
    inhib_spike_once_spike_once = create_weighted_synapse(-2)
    inhib_spike_once_redundant_spike_once = create_weighted_synapse(-2)

    # Create neuron that spikes once and then inhibits itself.
    spike_once = LIF(du=0, dv=0, bias=2, vth=1)

    # Create redundant spike_once neuron
    redundant_spike_once = LIF(du=0, dv=0, bias=2, vth=3)

    # Create receiving neuron, spikes if it gets an input of 2 or higher.
    receiver = LIF(du=0, dv=0, bias=0, vth=1)

    # Create recurrent inhibitory connection to make spike_once spike only once.
    spike_once = connect_synapse(spike_once, spike_once, inhib_spike_once_spike_once)

    # Connect spike_once with receiving neuron
    spike_once = connect_synapse(spike_once, receiver, excit_spike_once_receiver)

    # Connect spike_once with redundant neuron
    spike_once = connect_synapse(
        spike_once, redundant_spike_once, inhib_spike_once_redundant_spike_once
    )

    # Connect spike_once with redundant neuron
    spike_once = connect_synapse(
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


# Create the snn network.
(
    spike_once,
    receiver,
    redundant_spike_once,
) = create_two_neurons_with_one_redundant_neuron()

# Run simulation for t = 2
arr = np.array([9])
id = np.array([0])
for t in range(2):
    # arr=np.ndarray(shape=(1,0), dtype=int)

    # print(f'arr={arr[0]}')
    spike_once.run(condition=RunSteps(num_steps=0), run_cfg=Loihi1SimCfg())
    # print(f'spike_once.shape={spike_once.shape}')
    # print(f'spike_once.vth={spike_once.vth}')
    print(f"spike_once.vth={spike_once.vth.__dict__}")
    # print(f'spike_once.vth={spike_once.vth.value}')
    # print(f'spike_once.vth.init={spike_once.vth.init}')
    # print(f'spike_once.vth.shape={spike_once.shape}')
    # spike_once.vth.init=4
    # spike_once.vth= Var(spike_once.shape,500)
    # spike_once.vth.set(spike_once.shape,500)
    # spike_once.vth.set(spike_once.shape,[500])
    # spike_once.vth.set([500],)
    # spike_once.vth.set(arr,id) # WOrks almost
    spike_once.vth.set(
        arr,
    )  # WOrks almost
    # spike_once.vth.set(55,id)
    print(f"set_arr")
    print(f"spike_once.vth={spike_once}")
    # spike_once.vth.set([1],500)
    # spike_once.vth.set([0],500)
    # spike_once.vth.set(spike_once.vth.shape,300)
    # spike_once.vth.set((None,),300)
    # spike_once.vth.set((1,),None)
    # spike_once.vth.set(3,(1,))
    # spike_once.vth.set(spike_once.vth.shape,300)

    spike_once.run(condition=RunSteps(num_steps=1), run_cfg=Loihi1SimCfg())
    print(f"spike_once.shape={spike_once.u.get()}")
    print(receiver.u.get())
# Terminate Loihi simulation.
spike_once.stop()
