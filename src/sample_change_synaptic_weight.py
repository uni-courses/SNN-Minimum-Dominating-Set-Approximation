# Instantiate Lava processes to build network
from lava.magma.core.run_conditions import RunSteps
from lava.magma.core.run_configs import Loihi1SimCfg
from lava.proc.dense.process import Dense
from lava.proc.lif.process import LIF
from lava.proc.monitor.process import Monitor
from pprint import pprint
import numpy as np

lif1 = LIF(bias=2, vth=1)
dense = Dense(shape=(1, 1), weights=np.ones((1, 1)))
lif2 = LIF(vth=np.inf, dv=0, du=1)
monitor1 = Monitor()
monitor1.probe(lif2.v, 20)

# Connect processes via their directional input and output ports
lif1.out_ports.s_out.connect(dense.in_ports.s_in)
dense.out_ports.a_out.connect(lif2.in_ports.a_in)

# Execute process lif1 and all processes connected to it for fixed number of steps
lif1.run(condition=RunSteps(num_steps=10), run_cfg=Loihi1SimCfg())

# Print the currents that have accumulated in the post synaptic neuron (lif2)
print(monitor1.get_data())

# Change and Print the weights of the synapse (dense) to 2 from its initial state of 1
dense.weights.set(np.ones((1, 1)) * 2)
print(dense.weights)

# Run the simulation for 10 more timesteps
lif1.run(condition=RunSteps(num_steps=10), run_cfg=Loihi1SimCfg())
# Show that the voltage increase reflects the increase in the synaptic weights
print(monitor1.get_data())

lif1.stop()
