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
mon_lif_1_v = Monitor()
mon_lif_2_v = Monitor()
mon_spike = Monitor()

mon_lif_1_v.probe(lif1.v, 20)
mon_lif_2_v.probe(lif2.v, 20)
mon_spike.probe(lif1.s_out, 20)


# This is used to get the name of the process that is used for monitoring.
mon_lif_1_v_process = list(mon_lif_1_v.get_data())[0]
mon_lif_2_v_process = list(mon_lif_2_v.get_data())[0]
mon_spike_process = list(mon_spike.get_data())[0]
# Note it follows the order of declaration/initialisation of the neuron/dense it follows.
print(f"mon_lif_1_v_process={mon_lif_1_v_process}")
print(f"mon_lif_2_v_process={mon_lif_2_v_process}")
print(f"mon_spike_process={mon_spike_process}")


# Connect processes via their directional input and output ports
lif1.out_ports.s_out.connect(dense.in_ports.s_in)
dense.out_ports.a_out.connect(lif2.in_ports.a_in)

for run in range(10):
    t = run
    # Execute process lif1 and all processes connected to it for fixed number of steps
    lif1.run(condition=RunSteps(num_steps=1), run_cfg=Loihi1SimCfg())

    # Print the currents that have accumulated in the post synaptic neuron (lif2)
    print(
        f'lif1.v={mon_lif_1_v.get_data()[mon_lif_1_v_process]["v"][t]},lif1.s_out={mon_spike.get_data()[mon_spike_process]["s_out"][t]}, lif2.v={mon_lif_2_v.get_data()[mon_lif_2_v_process]["v"][t]}'
    )

# Change and Print the weights of the synapse (dense) to 2 from its initial state of 1
dense.weights.set(np.ones((1, 1)) * 2)
print(dense.weights)

for run in range(10):
    t = run + 10
    # Run the simulation for 10 more timesteps
    lif1.run(condition=RunSteps(num_steps=1), run_cfg=Loihi1SimCfg())
    # Show that the voltage increase reflects the increase in the synaptic weights
    print(
        f'lif1.v={mon_lif_1_v.get_data()[mon_lif_1_v_process]["v"][t]},lif1.s_out={mon_spike.get_data()[mon_spike_process]["s_out"][t]}, lif2.v={mon_lif_2_v.get_data()[mon_lif_2_v_process]["v"][t]}'
    )

print(f'voltage_list after={voltage_list}')
lif1.stop()
