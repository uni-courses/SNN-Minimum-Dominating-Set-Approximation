from gettext import npgettext
import numpy as np
import networkx as nx
import pylab as plt


def get_weight_receiver_synapse_paths_fully_connected(G):
    # Set weight receiver synapse path attribute (as a list) for each node in
    # graph G.
    # nx.set_node_attributes(G, set(), "wr_paths")

    for node in G.nodes:
        G.nodes[node]["wr_paths"] = set()
    for node in G.nodes:
        for neighbour in nx.all_neighbors(G, node):
            for target in nx.all_neighbors(G, node):
                if neighbour != node and target != node and target != neighbour:
                    G.nodes[node]["wr_paths"].add((neighbour, target))
    return G

def create_graph_of_network_degree_computation(G):
    """ Generates graphs for the WTA circuits that represents the neurons as
    nodes and synaptic connections as edges for the segment that of the
    solution network that goes from a spike once neuron to a degree receiver
    neuron.

    One neuron per node named: spike_once_0-n
    One neuron per node named: degree_receiver.
    One synapse from spike_once_0-n to each of its neighbours named degree_receiver.
    (Make the graph directional.)
    Then for the WTA circuit:
    Suppose node A is a node in 0-n:
    One neuron per neighbour X of node A, named neighbourgh_A_0-n
    where the first A is the index of the node it belongs to,
    and the second 0-n is the node nr of the neighbour.
    Synapses:
    For each Node A in graph G:
        For each neighbour X of node A:
            For each neighbour Y of node A in X where X!=Y:
                Synapse from X to Y with weight -1.
        Create a neuron Selector_A with threshold 1 (that keeps spiking and raising
        u of neighbour neurons untill the first one spikes. Stops spiking upon 
        receiving the first spike.)
        For each neighbour X of A:
            Synapse from X to Selector_A

        Then verify that for node A, the neuron B (winner neuron)
        keeps spiking at t=101. If this is verified, connect to the next round.
    """

    # Generate directed graph
    get_degree=nx.DiGraph()
    WTA_circuits=[]
    for node in G.nodes:
        WTA_circuits.append(nx.DiGraph())
        print(f'node={node}')
        #One neuron per node named: spike_once_0-n
        get_degree.add_node(f'spike_once_{node}',id=node, du=0, dv=0, bias=0)
        #One neuron per node named: degree_receiver.
        get_degree.add_node(f'degree_receiver_{node}',id=node, du=0, dv=0, bias=0)
        # For each neighbour of node, named degree_receiver:
        for neighbour in nx.all_neighbors(G, node):
            print(f'node={node}, neighbour={neighbour}')
            #One synapse from spike_once_0-n to each degree receiver that
            # represents neighbour node.
            get_degree.add_edges_from([(f'spike_once_{node}', f'degree_receiver_{neighbour}')])



        #Then for the WTA circuit:
        WTA_circuits[node]=get_degree.deepcopy()
        #Suppose node A is a node in 0-n:
        # DOUBT: One neuron per neighbour X of node A, named neighbourgh_A_0-n
        #where the first A is the index of the node it belongs to,
        #and the second 0-n is the node nr of the neighbour.
        #Synapses:
    #For each Node A in graph G:
        #    For each neighbour X of node A:
        for neighbour_x in nx.all_neighbors(G, node):
        #        For each neighbour Y of node A in X where X!=Y:
            for neighbour_y in nx.all_neighbors(G, node):
                if neighbour_x!=neighbour_y:
                    # Synapse from X to Y with weight -1.
                    WTA_circuits[node].add_edges_from([(f'degree_receiver{neighbour_x}', f'degree_receiver_{neighbour_y}')])
        #    Create a neuron Selector_A with threshold 1 (that keeps spiking and raising
        #    u of neighbour neurons untill the first one spikes. Stops spiking upon 
        #    receiving the first spike.)
        #    For each neighbour X of A:
        #        Synapse from X to Selector_A

        #    Then verify that for node A, the neuron B (winner neuron)
        #    keeps spiking at t=101. If this is verified, connect to the next round.
        #
    # Add nodes and edges
    #G.add_edge("Node1", "Node2")
    nx.draw(get_degree, with_labels = True)
    plt.show()
    #plt.savefig('labels.png')


def get_weight_receiver_synapse_paths(G):
    # Set weight receiver synapse path attribute (as a list) for each node in
    # graph G.
    # nx.set_node_attributes(G, set(), "wr_paths")

    for node in G.nodes:
        G.nodes[node]["wr_paths"] = set()
    for node in G.nodes:
        for neighbour in nx.all_neighbors(G, node):
            for target in nx.all_neighbors(G, node):
                if neighbour != node and target != node and target != neighbour:
                    G.nodes[node]["wr_paths"].add((neighbour, target))
    return G
