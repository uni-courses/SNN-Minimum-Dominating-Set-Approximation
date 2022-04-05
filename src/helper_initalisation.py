from gettext import npgettext
import numpy as np
import networkx as nx


def get_weight_receiver_synapse_paths(G):
    # Set weight receiver synapse path attribute (as a list) for each node in
    # graph G.
    nx.set_node_attributes(G, set(), "wr_paths")

    for node in G.nodes:
        for neighbour in nx.all_neighbors(G, node):
            for target in nx.all_neighbors(G, node):
                if target != neighbour:
                    print(
                        f"node:{node}, from neighbour{neighbour}, attributes={G.nodes[neighbour]} to target={target}"
                    )
                    print(
                        f'G.nodes[neighbour]["wr_paths"]={G.nodes[neighbour]["wr_paths"]}'
                    )
                    # if G.nodes[neighbour]["wr_paths"] is None:
                    #    G.nodes[neighbour]["wr_paths"]= set((neighbour,target))
                    # else:
                    # G.nodes[neighbour]["wr_paths"]= G.nodes[neighbour]["wr_paths"].add([neighbour,target])
                    G.nodes[neighbour]["wr_paths"] = G.nodes[neighbour][
                        "wr_paths"
                    ].add("a")
    return G
