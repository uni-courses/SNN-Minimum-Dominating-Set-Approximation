import random
import networkx as nx


def compute_mtds(input_graph, m=0):
    # As currently no decision has been reached as to what kind of object
    # input_graph actually is,this code will accept both node and edges lists
    # as well as nx.graphs.
    if isinstance(input_graph, nx.Graph):
        graph = nx.Graph()
        graph.add_nodes_from(
            list(input_graph.nodes),
            marks=0,
            random_number=0,
            weight=0,
        )
        graph.add_edges_from(list(input_graph.edges))
    if isinstance(input_graph, tuple):
        graph = nx.Graph()
        graph.add_nodes_from(
            input_graph[0],
            marks=0,
            random_number=0,
            weight=0,
        )
        graph.add_edges_from(input_graph[1])

    for node in graph.nodes:
        graph.nodes[node]["marks"] = 0
        # 1.a Each vertex v_i chooses random float r_i in range 0<r_i<1
        graph.nodes[node]["random_number"] = random.random()
        # 1.b Each vertex v_i computes d_i. d_i=degree of vertex v_i
        # 1.c Each vertex v_i computes weight: w_i=d_i+r_i
        # 1.d Each vertex v_i sends w_i to each of its neighbours. (Not
        # happening due to a centralised version)
        graph.nodes[node]["weight"] = (
            graph.degree(node) + graph.nodes[node]["random_number"]
        )

    for node in graph.nodes:
        # 2.a Each vertex v_i gets the index of the
        # neighbouring vertex v_j_(w_max) that has the heighest w_i, with i!=j.
        max_weight = max(
            graph.nodes[n]["weight"] for n in nx.all_neighbors(graph, node)
        )
        for n in nx.all_neighbors(graph, node):
            if graph.nodes[n]["weight"] == max_weight:
                # 2.b Each vertex v_i adds a mark to that neighbour vertex
                # v_j_(w_max).
                graph.nodes[n]["marks"] += 1

    # 3 for k in range [0,m] rounds, do:
    for _ in range(m):

        for node in graph.nodes:
            # 4.a Each node v_i computes how many marks it has received, as
            # (x_i)_k.
            # 4.b Each node v_i computes (w_i)_k=(x_i)_k+ r_i
            graph.nodes[node]["weight"] = (
                graph.nodes[node]["marks"] + graph.nodes[node]["random_number"]
            )
            # 5. Reset marked vertices: for each vertex v_i, (x_i)_k=0
            graph.nodes[node]["marks"] = 0

        for node in graph.nodes:
            # 6.a Each vertex v_i sends w_i to each of its neighbours.
            # 6.b Each vertex v_i gets the index of the
            # neighbouring vertex v_j_(w_max) that has the heighest w_i, with
            # i!=j.
            max_weight = max(
                graph.nodes[n]["weight"] for n in nx.all_neighbors(graph, node)
            )
            for n in nx.all_neighbors(graph, node):
                if graph.nodes[n]["weight"] == max_weight:
                    # 6.d Each vertex v_i adds a mark to that neighbour vertex
                    # v_j_(w_max).
                    graph.nodes[n]["marks"] += 1

    dset = []
    for n in graph.nodes.data():
        if n[1]["marks"] > 0:
            dset.append(n[0])

    return dset
