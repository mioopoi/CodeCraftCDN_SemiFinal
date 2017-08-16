import networkx as nx
import time

from read_graph import read_graph


file_name = "./case_example/low/case0.txt"
#file_name = "./case_example/high/topo2400.txt"

output_cap, server_fee, deploy_cost, cus_list, total_demand, G = read_graph(file_name)

for i in range(G.number_of_nodes()):
    G.node[i]['demand'] = -G.node[i]['demand']

# Super sink
sink = G.number_of_nodes()
G.add_node(sink, demand=total_demand)
for i in range(G.number_of_nodes()-1):
    if G.node[i]['demand'] != 0:
        G.add_edge(i, sink, capacity=G.node[i]['demand'], cost=0)

for i in range(G.number_of_nodes()-1):
    G.node[i]['demand'] = 0

for i in range(G.number_of_nodes()-1):
    G.add_node(i, demand=-total_demand)

    start_time = time.clock()
    nx.max_flow_min_cost(G, i, sink, weight='cost')
    #nx.capacity_scaling(G, weight='cost')
    end_time = time.clock()
    print("Elapsed time: %f" % (end_time - start_time))

    G.add_node(i, demand=0)