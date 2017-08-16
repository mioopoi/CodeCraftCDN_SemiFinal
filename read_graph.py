import networkx as nx


def read_graph(file_name):
    G = nx.DiGraph()

    f = open(file_name)

    first_line = f.readline()
    #print first_line
    node_num, edge_num, cus_node_num = first_line.split()
    node_num, edge_num, cus_node_num = int(node_num), int(edge_num), int(cus_node_num)
    print node_num, edge_num, cus_node_num

    second_line = f.readline()  # blank line

    # server level information
    output_cap = {}
    server_fee = {}
    for i in range(15):
        line = f.readline()
        if len(line) == 1:  # the blank line
            break
        level_id, _cap, _fee = line.split()
        level_id, _cap, _fee = int(level_id), int(_cap), int(_fee)

        '''output_cap, server_fee = {}, {}
        output_cap[0] = _cap
        server_fee[0] = _fee'''

        output_cap[level_id] = _cap
        server_fee[level_id] = _fee

    # deploy cost of net vertex
    deploy_cost = {}
    for i in range(node_num):
        line = f.readline()
        node_id, _cost = line.split()
        node_id, _cost = int(node_id), int(_cost)
        deploy_cost[node_id] = _cost

    line = f.readline()  # blank line

    # edge information
    for i in range(edge_num):
        line = f.readline()
        src, des, cap, fee = line.split()
        src, des, cap, fee = int(src), int(des), int(cap), int(fee)
        G.add_edge(src, des, cost = fee, capacity = cap)
        G.add_edge(des, src, cost = fee, capacity = cap)

    line = f.readline()

    for i in range(node_num):
        G.add_node(i, demand = 0)

    #cus_list = []
    cus_list = {}
    total_demand = 0
    for i in range(cus_node_num):
        line = f.readline()
        cus_node, adj_net_node, need = line.split()
        cus_node, adj_net_node, need = int(cus_node), int(adj_net_node), int(need)
        #cus_list.append(adj_net_node)
        cus_list[adj_net_node] = need
        total_demand += need
        G.add_node(adj_net_node, demand = -need)

    f.close()

    print "number of nodes: %d" % G.number_of_nodes()
    print "number of edges: %d" % G.number_of_edges()
    print "number of customers: %d" % cus_node_num

    return output_cap, server_fee, deploy_cost, cus_list, total_demand, G

#read_graph()