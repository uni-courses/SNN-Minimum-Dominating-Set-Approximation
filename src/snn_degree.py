import random
import networkx as nx
from src.helper_snns import create_spike_once_neuron


def degree_rate_coding(G):
    """Creates a degree_sender neuron and a weight_receiver neuron for each
    node. The degree_sender spikes once to each weight_receiver neuron of its
    neighbours. This is spike is already the d in w=d+r, where r is the random
    spike pattern. The degree is generated over a timeframe: t=n*s, where
    n is the number of nodes in the graph (in essence it is the maximum degree
    such that the rate coding can convey all possible degrees). s is the custom
    window for the random spiking. For example s=10 allows the creation of a
    random integer in range 0 to 10.

    The weight receiver is the start of the non-conventional WTA circuit.
    Therefore, the synapses between degre_sender and weight_receiver is -1.

    The weight receiver keeps spiking untill it gets inhibited.
    """
    max_degree = G.number_of_nodes()
    degree_senders = []
    for node in G.nodes:
        print("hi")
        node["degree_sender"] = create_degree_sender_neuron()
        # degree_senders.append(create_degree_sender_neuron())


def create_degree_sender_neuron():
    """
    The degree_sender neuron should send 1 spike at t=1.
    At t>1, it should not send any spikes anymore.

    To realise this, a generic spike_once neuron is created
    that spikes at t=1.
    """
    return create_spike_once_neuron()


def create_weight_receiver_neuron():
    """Creates a weight receiver neuron for each node in the graph.
    It receives a single spike from each neighbour
    that it is connected to. The receiver neuron then sends 1 spike per
    incoming spike, one at a time. So basically it transforms 8 spikes at once
    into 8 consequitive spikes.
    """
    pass
