from gettext import npgettext
import numpy as np


def print_vars(lif, id=None):
    """Prints all variables of a LIF process and their values."""

    sp = 3 * "  "
    print(f"Variables of the LIF:{id}")
    print(sp + "u:    {}".format(str(lif.u.get())))
    print(sp + "v:    {}".format(str(lif.v.get())))
    print(sp + "du:   {}".format(str(lif.du.get())))
    print(sp + "dv:   {}".format(str(lif.dv.get())))
    print(sp + "bias: {}".format(str(lif.bias.get())))
    print(sp + "vth:  {}".format(str(lif.vth.get())))


def create_two_neurons(u_1=0, du_1=0, dv_1=0, bias_1=0,du_2=0, dv_2=0, bias_2=0):
    # Instantiate Lava processes to build network
    from lava.proc.dense.process import Dense
    from lava.proc.lif.process import LIF

    # Initialise neurons and synapses.
    if dv_1 is None:
        lif1 = LIF(u=u_1, du=du_1, bias=bias_1)
    else:
        lif1 = LIF(u=u_1, du=du_1, dv=dv_1, bias=bias_1)
    print(f"lif1.u.get()={lif1.u.get()}")

    # dense = Dense()
    shape = (1, 1)
    # weights = np.random.randint(100, size=shape)
    weights = [[3]]  # Needs to be this shape for a 1-1 neuron connection.
    weight_exp = 2
    num_weight_bits = 7
    sign_mode = 1
    print(f"weights={weights}")
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