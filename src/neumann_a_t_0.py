# This code computes a minimium total dominating set approximation.
import random


def compute_mtds_a_t_0(G, m=2):

    # No directed graphs supported in this algorithm.
    if G.is_directed():
        raise Exception("Parameter graph should be undirected")

    # 1.a Each vertex v_i chooses random float r_i in range 0<r_i<1
    for node in G.nodes:
        # print(f'label={G.nodes[node]["label"]}')
        G.nodes[node]["rand_val"] = random.uniform(0, 1)
        print(f'rand_val={G.nodes[node]["rand_val"]}')
    # 1.b Each vertex v_i computes d_i. d_i=degree of vertex v_i
    for node in G.nodes:
        G.nodes[node]["degree"] = G.degree(node)
        print(f'degree={G.nodes[node]["degree"]}')
    # 1.c Each vertex v_i computes weight: w_i=d_i+r_i
    for node in G.nodes:
        G.nodes[node]["weight"] = G.nodes[node]["degree"] + G.nodes[node]["rand_val"]
        print(f'weight={G.nodes[node]["weight"]}')

    # 1.d Each vertex v_i sends w_i to each of its neighbours.
    # TODO: paradigm: Either each neuron sends some value to another neuron.
    # OR: each neuron asks/demands some value of each of its neighbours.
    store_index_max_neighbour_weight(G)

    # 2.a Each vertex v_i gets the index of the
    # neighbouring vertex v_j_(w_max) that has the heighest w_i, with i!=j.
    # 2.b Initialise the mark counter x_i
    for node in G.nodes:
        G.nodes[node]["mark"] = 0
    # 2.c Each vertex v_i adds a mark to that neighbour vertex v_j_(w_max).
    for node in G.nodes:
        neighbor_with_max_weight = G.nodes[node]["neighbor_with_max_weight"]
        G.nodes[neighbor_with_max_weight]["mark"] = (
            G.nodes[neighbor_with_max_weight]["mark"] + 1
        )

    # 3 for k in range [0,m] rounds, do:
    for _ in range(0, m):

        # 4.a Each node v_i computes how many marks it has received, as (x_i)_k.
        # 4.b Each node v_i computes (w_i)_k=(x_i)_k+ r_i
        for node in G.nodes:
            G.nodes[node]["weight"] = G.nodes[node]["mark"] + G.nodes[node]["rand_val"]
            print(f'weight={G.nodes[node]["weight"]}')

        # 5. Reset marked vertices: for each vertex v_i, (x_i)_k=0
        for node in G.nodes:
            G.nodes[node]["mark"] = 0

        # 6.a Each vertex v_i computes d_i. d_i=degree of vertex v_i
        # 6.b Each vertex v_i sends w_i to each of its neighbours.
        # 6.c Each vertex v_i gets the index of the
        # neighbouring vertex v_j_(w_max) that has the heighest w_i, with i!=j.
        store_index_max_neighbour_weight(G)
        # 6.d Each vertex v_i adds a mark to that neighbour vertex v_j_(w_max).
        for node in G.nodes:
            neighbor_with_max_weight = G.nodes[node]["neighbor_with_max_weight"]
            G.nodes[neighbor_with_max_weight]["mark"] = (
                G.nodes[neighbor_with_max_weight]["mark"] + 1
            )

        # Print Minimum Total Dominating Set approximation.
        mtds = []
        for node in G.nodes:
            print(f'node {node} has {G.nodes[node]["mark"]} marks')
            if 0 < G.nodes[node]["mark"]:
                mtds.append(node)
        print(f"mtds={mtds}")


def store_index_max_neighbour_weight(G):
    for node in G.nodes:
        G.nodes[node]["neighbor_with_max_weight"] = None
        max = 0  # Assumes positive weights
        for neighbor in G.neighbors(node):
            if G.nodes[node]["neighbor_with_max_weight"] is None:
                G.nodes[node][
                    "neighbor_with_max_weight"
                ] = neighbor  # G.nodes[neighbor]
                max = G.nodes[neighbor]["weight"]
            elif G.nodes[neighbor]["weight"] > max:
                G.nodes[node][
                    "neighbor_with_max_weight"
                ] = neighbor  # G.nodes[neighbor]
                max = G.nodes[neighbor]["weight"]
        print(
            f'node={node}G.nodes[node]["neighbor_with_max_weight"]={G.nodes[node]["neighbor_with_max_weight"]}'
        )
    return G


def add_two(x):
    return x + 2
