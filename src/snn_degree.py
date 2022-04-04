import random
import networkx as nx
from src.helper_snns import create_spike_once_neuron


def create_network(G):
    """ Creates a network that can compute the degree of the neurons."""
    max_degree = G.number_of_nodes()
    degree_senders = []
    for node in G.nodes:
        print("hi")
        degree_senders.append(create_degree_sender_neuron)


def create_degree_sender_neuron():
    """
    The degree_sender neuron should send 1 spike at t=1.
    At t>1, it should not send any spikes anymore.

    To realise this, a generic spike_once neuron is created
    that spikes at t=1.
    """
    return create_spike_once_neuron()

def create_degree_receiver_neuron():
    """ Creates a neuron that receives a single spike from each neighbour
    that it is connected to. The receiver neuron then sends 1 spike per 
    incoming spike, one at a time. So basically it transforms 8 spikes at once
    into 8 consequitive spikes.
    """
    pass