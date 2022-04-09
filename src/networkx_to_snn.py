import networkx as nx
def convert_networkx_graph_to_snn(G,full_spec,bias=0,du=0, dv=0, weight=1,vth=1):
    """ Converts an incoming graph into a spiking neural network for lava-nc.
    Input arguments are the default values if they are not specified.
    Throws error if full spec is required whilst one argument is missing.
    """
    neurons=[]
    for node in G.nodes:
        node_has_full_neuron_specification(G,node)
        #neuron=LIF(du=0, dv=0, bias=2, vth=1)

        #neurons.append(neuron)
    
    #dense = create_weighted_synapse(spike_once, spike_once, -2)
    raise Exception("Stop")

def node_has_full_neuron_specification(G,node):
    try:
        print(G.nodes[node]["du"])
    except:
        pass
    try:
        print(node["du"])
    except:
        pass
    try:
        print(node)
        print(G.nodes[node])
        print(nx.get_node_attributes(G, node))
        print(f'for node:{node},du={get_attribute_of_node("du",G,node)}')    
    except:
        pass
    

def get_attribute_of_nodes_of_graph(G,attribute_name):
    return nx.get_node_attributes(G,attribute_name)

def get_attribute_of_node(attribute_name,G,node):
    attributes=get_attribute_of_nodes_of_graph(G,attribute_name)
    print(f'attributes={attributes}')
    #return attributes
    return attributes[f'spike_once_{node}']