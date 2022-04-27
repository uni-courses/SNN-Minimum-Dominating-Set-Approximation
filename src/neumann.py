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


def partial_alipour(delta, inhibition, G, rand_ceil, rand_nrs):
    """
    This code implements the alipour algorithm as described in the paper https://doi.org/10.48550/arXiv.2012.04883
    The algorithm is implemented on a single computer instead of an actual network of nodes.
    """
    # Reverse engineer actual rand nrs:
    uninhibited_rand_nrs = [x + inhibition for x in rand_nrs]
    print(f"uninhibited_rand_nrs={uninhibited_rand_nrs}")

    for node in G.nodes:
        G.nodes[node]["marks"] = 0
        G.nodes[node]["random_number"] = 1 * uninhibited_rand_nrs[node]
        # *(rand_ceil+1) because the spike_weights are multiplied with that value.
        # Because the random weights should map to 0<random_weight<spike_weight.
        G.nodes[node]["weight"] = (
            G.degree(node) * (rand_ceil + 1) * delta + G.nodes[node]["random_number"]
        )
        G.nodes[node]["neg_rand"] = rand_nrs[node]
        G.nodes[node]["expected_weight"] = (
            rand_nrs[node] + G.degree(node) * (rand_ceil + 1) * delta
        )

    for node in G.nodes:
        max_weight = max(G.nodes[n]["weight"] for n in nx.all_neighbors(G, node))

        print(f"node={node},max_weight={max_weight}")
        for neighbour in sorted(list(nx.all_neighbors(G, node))):
            print(f'{node}_{neighbour}:weight={G.nodes[neighbour]["weight"]}')
            print(f'{node}_{neighbour}:neg_rand={G.nodes[neighbour]["neg_rand"]}')
            print(
                f'{node}_{neighbour}:expected_weight={G.nodes[neighbour]["expected_weight"]}'
            )
        print(f"")
        for n in nx.all_neighbors(G, node):
            if (
                G.nodes[n]["weight"] == max_weight
            ):  # should all max weight neurons be marked or only one of them?
                G.nodes[n]["marks"] += 1
    return G


def full_alipour(delta, inhibition, G, rand_ceil, rand_nrs, m):
    # Reverse engineer actual rand nrs:
    uninhibited_rand_nrs = [(x + inhibition) for x in rand_nrs]
    print(f"uninhibited_rand_nrs={uninhibited_rand_nrs}")

    for node in G.nodes:
        G.nodes[node]["marks"] = 0
        G.nodes[node]["countermarks"] = 0
        G.nodes[node]["random_number"] = 1 * uninhibited_rand_nrs[node]
        G.nodes[node]["weight"] = (
            G.degree(node) * (rand_ceil + 1) * delta + G.nodes[node]["random_number"]
        )

    for node in G.nodes:
        max_weight = max(G.nodes[n]["weight"] for n in nx.all_neighbors(G, node))
        for n in nx.all_neighbors(G, node):
            if (
                G.nodes[n]["weight"] == max_weight
            ):  # should all max weight neurons be marked or only one of them?
                G.nodes[n]["marks"] += 1 if m == 0 else (rand_ceil + 1) * delta
                G.nodes[n]["countermarks"] += 1

    for loop in range(m):

        for node in G.nodes:
            G.nodes[node]["weight"] = (
                G.nodes[node]["marks"] + G.nodes[node]["random_number"]
            )
            G.nodes[node]["marks"] = 0
            G.nodes[node]["countermarks"] = 0

        for node in G.nodes:
            max_weight = max(G.nodes[n]["weight"] for n in nx.all_neighbors(G, node))
            for n in nx.all_neighbors(G, node):
                if G.nodes[n]["weight"] == max_weight:
                    G.nodes[n]["marks"] += (
                        1 if loop == (m - 1) else (rand_ceil + 1) * delta
                    )
                    G.nodes[n]["countermarks"] += 1

    return G
