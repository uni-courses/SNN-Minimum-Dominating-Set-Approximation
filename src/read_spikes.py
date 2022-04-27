# Instantiate Lava processes to build network
from lava.proc.dense.process import Dense
from lava.proc.lif.process import LIF
from lava.proc.monitor.process import Monitor
from pprint import pprint
import numpy as np

simulation_time = 10

lif1 = LIF(bias=1, vth=1)
dense = Dense(shape=(1, 1), weights=np.ones((1, 1)))
lif2 = LIF(vth=np.inf, dv=0, du=1)
monitor1 = Monitor()
monitor1.probe(lif1.out_ports.s_out, simulation_time)
# monitor1.probe(lif1.v, simulation_time)

# Connect processes via their directional input and output ports
lif1.out_ports.s_out.connect(dense.in_ports.s_in)
dense.out_ports.a_out.connect(lif2.in_ports.a_in)

# Execute process lif1 and all processes connected to it for fixed number of steps
from lava.magma.core.run_conditions import RunSteps
from lava.magma.core.run_configs import Loihi1SimCfg

lif1.run(condition=RunSteps(num_steps=simulation_time), run_cfg=Loihi1SimCfg())
print(monitor1.get_data())
lif1.stop()
