from gettext import npgettext
import numpy as np
import networkx as nx


def get_weight_receiver_synapse_paths(G):
    # Set weight receiver synapse path attribute (as a list) for each node in
    # graph G.
    #nx.set_node_attributes(G, set(), "wr_paths")

    for node in G.nodes:
        G.nodes[node]["wr_paths"]=set()
    for node in G.nodes:
        for neighbour in nx.all_neighbors(G, node):
            print(
                f'G.nodes[node]["wr_paths"]={G.nodes[node]["wr_paths"]}'
            )
            for target in nx.all_neighbors(G, node):
                if neighbour != node and target != node and target != neighbour:
                    print(
                        f"node:{node}, from neighbour{neighbour}, attributes={G.nodes[node]} to target={target}"
                    )
                    print(
                        f'Before G.nodes[node]["wr_paths"]={G.nodes[node]["wr_paths"]}'
                    )
                    G.nodes[node]["wr_paths"].add((neighbour, target))
                    print(
                        f'After G.nodes[node]["wr_paths"]={G.nodes[node]["wr_paths"]}\n'
                    )
    return G
