# Returns graph properties.

import networkx as nx


def is_triangle_free(G):
    if nx.triangles(G, 0) == 0:
        return True
    else:
        return False


def is_planar_graph(G):
    is_planar = nx.check_planarity(G)
    return is_planar
