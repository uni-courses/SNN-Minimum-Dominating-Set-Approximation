def LIF_neuron():
    # Instantiate Lava processes to build network
    from lava.proc.dense.process import Dense
    from lava.proc.lif.process import LIF

    lif1 = LIF()
    dense = Dense()
    lif2 = LIF()

    # Connect processes via their directional input and output ports
    lif1.out_ports.s_out.connect(dense.in_ports.s_in)
    dense.out_ports.a_out.connect(lif2.in_ports.a_in)

    # Execute process lif1 and all processes connected to it for fixed number of steps
    from lava.magma.core.run_conditions import RunSteps
    from lava.magma.core.run_configs import Loihi1SimCfg

    lif1.run(condition=RunSteps(num_steps=10),
             run_cfg=Loihi1SimCfg()
    )
    lif1.stop()
    print(f'done')