from gettext import npgettext
import numpy as np

# Instantiate Lava processes to build network
from lava.proc.dense.process import Dense
from lava.proc.lif.process import LIF


def print_neuron_properties(neurons, ids=None):
    spacing = 4
    if not ids is None:
        [print(f"{str(x) : <{spacing+5}}", end=" ") for x in ids]

    print(f""), [print(f"u={str(x.u.get()) : <{spacing+3}}", end=" ") for x in neurons]
    print(f""), [
        print(f"du={str(x.du.get()) : <{spacing+2}}", end=" ") for x in neurons
    ]
    print(f""), [print(f"v={str(x.v.get()) : <{spacing+3}}", end=" ") for x in neurons]
    print(f""), [
        print(f"dv={str(x.dv.get()) : <{spacing+2}}", end=" ") for x in neurons
    ]
    print(f""), [
        print(f"bias={str(x.bias.get()) : <{spacing}}", end=" ") for x in neurons
    ]
    print(f""), [
        print(f"vth={str(x.vth.get()) : <{spacing+1}}", end=" ") for x in neurons
    ]
    print(f"\n")


def create_two_neurons(u_1=0, du_1=0, dv_1=0, bias_1=0, du_2=0, dv_2=0, bias_2=0):

    # Initialise neurons and synapses.
    if dv_1 is None:
        lif1 = LIF(u=u_1, du=du_1, bias=bias_1)
    else:
        lif1 = LIF(u=u_1, du=du_1, dv=dv_1, bias=bias_1)
    print(f"lif1.u.get()={lif1.u.get()}")

    # dense = Dense()
    # Details/documentation: https://github.com/lava-nc/lava/blob/64a3e4c779939506eccf05f7df3af94ace2518af/src/lava/proc/dense/process.py

    shape = (1, 1)
    # weights = np.random.randint(100, size=shape)
    weights = [[3]]  # Needs to be this shape for a 1-1 neuron connection.
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
    print(f"shape weights={np.shape(weights)}")
    # raise Exception("TERMINATED")
    lif2 = LIF(du=du_2, dv=dv_2, bias=bias_2)

    # Connect processes via their directional input and output ports
    lif1.out_ports.s_out.connect(dense.in_ports.s_in)
    dense.out_ports.a_out.connect(lif2.in_ports.a_in)
    return lif1, dense, lif2


def create_spike_once_neuron():
    """Creates neuron that spikes once and then never again. Uses a recurrent
    synapse with weight -1 such that it silences itself.
    """
    spike_once = LIF(du=0, dv=0, bias=2, vth=1)
    dense = create_weighted_synapse(-2)

    # Connect neuron to itself.
    spike_once = connect_synapse(spike_once, spike_once, dense)
    return spike_once


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


def connect_synapse_left_to_right(lhs_neuron, rhs_neuron, dense):
    """Connects a synapse named dense from lhs_neuron to rhs_neuron."""
    lhs_neuron.out_ports.s_out.connect(dense.in_ports.s_in)
    dense.out_ports.a_out.connect(rhs_neuron.in_ports.a_in)
    return lhs_neuron


def connect_synapse_right_to_left(lhs_neuron, rhs_neuron, dense):
    """Connects a synapse named dense from lhs_neuron to rhs_neuron."""
    rhs_neuron.out_ports.s_out.connect(dense.in_ports.s_in)
    dense.out_ports.a_out.connect(lhs_neuron.in_ports.a_in)
    return lhs_neuron
