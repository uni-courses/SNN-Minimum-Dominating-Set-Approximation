from gettext import npgettext
import numpy as np
import networkx as nx


def get_weight_receiver_synapse_paths_fully_connected(G):
    # Set weight receiver synapse path attribute (as a list) for each node in
    # graph G.
    # nx.set_node_attributes(G, set(), "wr_paths")

    for node in G.nodes:
        G.nodes[node]["wr_paths"] = set()
    for node in G.nodes:
        for neighbour in nx.all_neighbors(G, node):
            for target in nx.all_neighbors(G, node):
                if (
                    neighbour != node
                    and target != node
                    and target != neighbour
                ):
                    G.nodes[node]["wr_paths"].add((neighbour, target))
    return G


def get_weight_receiver_synapse_paths(G):
    # Set weight receiver synapse path attribute (as a list) for each node in
    # graph G.
    # nx.set_node_attributes(G, set(), "wr_paths")

    for node in G.nodes:
        G.nodes[node]["wr_paths"] = set()
    for node in G.nodes:
        for neighbour in nx.all_neighbors(G, node):
            for target in nx.all_neighbors(G, node):
                if (
                    neighbour != node
                    and target != node
                    and target != neighbour
                ):
                    G.nodes[node]["wr_paths"].add((neighbour, target))
    return G
