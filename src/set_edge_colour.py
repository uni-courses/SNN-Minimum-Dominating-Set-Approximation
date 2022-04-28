def color_nodes():
    import matplotlib.pyplot as plt
    import networkx as nx

    GExample = nx.Graph()
    GExample.add_nodes_from(["a", "b", "c", "d", "e", "f", "g"])
    GExample.add_edges_from(
        [
            ("a", "b"),
            ("b", "a"),
            ("a", "c"),
            ("b", "c"),
            ("b", "d"),
            ("c", "d"),
            ("d", "e"),
            ("b", "e"),
            ("b", "f"),
            ("f", "g"),
        ]
    )
    options = {"with_labels": True}
    color_map = []
    for node in GExample:
        if node == "a":
            color_map.append("blue")
        else:
            color_map.append("white")
        
    edge_color_map=[]
    for edge in GExample.edges:
        
        if edge==("a","c"):
            print(edge)
            edge_color_map.append("red")
        else:
            edge_color_map.append("yellow")


    nx.draw_networkx(GExample, node_color=color_map,edge_color=edge_color_map, **options)
    plt.show()

color_nodes()