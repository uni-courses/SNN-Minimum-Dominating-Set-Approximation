def print_vars(lif):
    """Prints all variables of a LIF process and their values."""

    sp = 3 * "  "
    print("Variables of the LIF:")
    print(sp + "u:    {}".format(str(lif.u.get())))
    print(sp + "v:    {}".format(str(lif.v.get())))
    print(sp + "du:   {}".format(str(lif.du.get())))
    print(sp + "dv:   {}".format(str(lif.dv.get())))
    print(sp + "bias: {}".format(str(lif.bias.get())))
    print(sp + "vth:  {}".format(str(lif.vth.get())))


def create_two_neurons(u_1=0, du_1=0, dv_1=0, bias=0):
    # Instantiate Lava processes to build network
    from lava.proc.dense.process import Dense
    from lava.proc.lif.process import LIF

    # Initialise neurons and synapses.
    if dv_1 is None:
        lif1 = LIF(u=u_1, du=du_1, bias=bias)
    else:
        lif1 = LIF(u=u_1, du=du_1, dv=dv_1, bias=bias)
    print(f"lif1.u.get()={lif1.u.get()}")

    dense = Dense()
    lif2 = LIF()

    # Connect processes via their directional input and output ports
    lif1.out_ports.s_out.connect(dense.in_ports.s_in)
    dense.out_ports.a_out.connect(lif2.in_ports.a_in)
    return lif1, dense, lif2
