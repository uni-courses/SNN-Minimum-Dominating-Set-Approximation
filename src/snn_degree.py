import random
import networkx as nx


def create_network(G):
    max_degree = G.number_of_nodes()

    for node in G.nodes:
        print("hi")


def create_degree_sender_neuron():
    """
    The degree_sender neuron should send 1 spike at t=1.
    At t>1, it should not send any spikes anymore.

    To realise this, one sets the v(t=0) to 1.
    """
    print("hi")
