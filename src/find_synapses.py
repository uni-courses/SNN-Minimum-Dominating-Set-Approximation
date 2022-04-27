from pprint import pprint

# Instantiate Lava processes to build network
from lava.proc.dense.process import Dense
from lava.proc.lif.process import LIF

from lava.magma.core.run_conditions import RunSteps
from lava.magma.core.run_configs import Loihi1SimCfg


def create_two_neurons():
    """Creates 2 neurons that with a synapse inbetween."""
    spike_train = LIF(du=0, dv=0, bias=1, vth=4)
    dense = create_weighted_synapse(3)

    receiver = LIF(du=0, dv=0, bias=-4, vth=1)
    third_neuron = LIF(du=0, dv=0, bias=-4, vth=1)

    # Connect neuron to itself.
    spike_train = connect_synapse(spike_train, receiver, dense)
    # receiver = connect_synapse( receiver ,third_neuron, dense)
    return spike_train, receiver, third_neuron


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


spike_train, receiver, third_neuron = create_two_neurons()

# Run simulation for t = 2
for t in range(3):
    spike_train.run(condition=RunSteps(num_steps=2), run_cfg=Loihi1SimCfg())
    print(receiver.u.get())
print(f"spike_train")
print(spike_train)
print(f"receiver")
print(receiver)

##print("spike_train.s_out.out_connections[0]")
##print(spike_train.s_out.out_connections[0])
##
##print(f'spike_train.s_out.out_connections[0].in_connections[0]')
##print(spike_train.s_out.out_connections[0].in_connections[0])
##
##print(f's_out.out_connections[0].in_connections[0].out_connections[0]')
##print(spike_train.s_out.out_connections[0].in_connections[0].out_connections[0])
print("")

##print("receiver.a_in.in_connections[0].out_connections[0]")
##print(receiver.a_in.in_connections[0].out_connections[0])
##
##print("receiver.a_in.in_connections[0].out_connections[0].in_connections[0]")
##print(receiver.a_in.in_connections[0].out_connections[0].in_connections[0])
##
##
##print("receiver.a_in.in_connections[0].out_connections[0].in_connections[0].__dict__")
##print(receiver.a_in.in_connections[0].out_connections[0].in_connections[0].__dict__)
##
##print("receiver.a_in.in_connections[0].out_connections[0].in_connections[0].out_connections[0]")
##print(receiver.a_in.in_connections[0].out_connections[0].in_connections[0].out_connections[0])
# This prints the Dense object.
# print(receiver.a_in.in_connections[0].out_connections[0].in_connections[0]._process.__dict__)
# print(spike_train.__dict__)

pprint(spike_train.out_ports.__dict__)
pprint(spike_train.in_ports.__dict__)

print("")
pprint(spike_train.out_ports._members)
pprint(receiver.in_ports.__dict__)
print("IN PROCESSS")
pprint(receiver.in_ports.process.__dict__)
