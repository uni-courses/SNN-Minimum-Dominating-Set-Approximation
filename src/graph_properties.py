# Returns graph properties.

import networkx as nx


def is_triangle_free(G):
    # https://networkx.org/documentation/stable//reference/algorithms/generated/networkx.algorithms.cluster.triangles.html
    triangles = nx.triangles(G).values()
    nr_of_triangles = sum(triangles) / 3
    if nr_of_triangles == 0:
        return True
    else:
        return False


def is_planar(G):
    # https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.planarity.check_planarity.html
    is_planar, certificate = nx.check_planarity(G)
    return is_planar
