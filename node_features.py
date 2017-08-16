import networkx as nx
import math

from read_graph import read_graph


class NodeFeatures:

    def __init__(self, file_name="./case_example_3/mid/case0.txt"):
        output_cap, server_fee, deploy_cost, cus_list, total_demand, G = read_graph(file_name)
        self.output_cap = output_cap
        self.server_fee = server_fee
        self.deploy_cost = deploy_cost
        self.cus_list = cus_list
        self.total_demand = total_demand
        self.G = G

        self.spl = nx.all_pairs_shortest_path_length(self.G)

        self.compute_node_features()

    def compute_node_features(self):
        for i in range(self.G.number_of_nodes()):
            self.G.node[i]['demand'] = -self.G.node[i]['demand']
            '''if self.G.node[i]['demand'] == 0:
                self.G.node[i]['demand'] = 1'''

            self.G.add_node(i, deploy_cost=self.deploy_cost[i])  # deploy cost
            self.G.add_node(i, outgoing_bandwidth=self.cal_outgoing_bandwidth(i))  # sum of outgoing bandwidth
            #self.G.add_node(i, ingoing_bandwidth=self.cal_ingoing_bandwidth(i))  # sum of ingoing bandwidth
            self.G.add_node(i, outgoing_cost=self.cal_outgoing_cost(i))  # average cost of outgoing edges
            self.G.add_node(i, out_degree=self.G.out_degree(i))  # out degree
            self.G.add_node(i, hops_to_cus=self.cal_hops_to_cus(i))  # sum of hops to all cus nodes
            #self.G.add_node(i, num_cus_within_three_hops=self.cal_num_cus_within_three_hops(i))
            self.G.add_node(i, num_cus_within_two_hops=self.cal_num_cus_within_two_hops(i)+1)
            self.G.add_node(i, num_cus_within_one_hops=self.cal_num_cus_within_one_hop(i)+1)
            self.G.add_node(i, degrees_of_neighbors=self.cal_degrees_of_neighbors(i))

        #for i in range(self.G.number_of_nodes()):
        #    self.G.add_node(i, bandwidth_of_neighbors=self.cal_bandwidth_of_neighbors(i))

    def compute_mcf(self, servers):
        # Add super source and sink
        n = self.G.number_of_nodes()
        source, sink = n, n+1
        self.G.add_node(source, demand=-self.total_demand)
        self.G.add_node(sink, demand=self.total_demand)

        # super source --> servers
        for i in servers:
            self.G.add_edge(source, i, cost=0, capacity=self.output_cap[servers[i]])
        # cus --> super sink
        for i in self.cus_list:
            self.G.add_edge(i, sink, cost=0, capacity=self.cus_list[i])

        for i in range(n):
            self.G.node[i]['demand'] = 0

        min_cost_flow = nx.max_flow_min_cost(self.G, source, sink, weight='cost')
        min_cost = nx.cost_of_flow(self.G, min_cost_flow, weight='cost')
        max_flow = nx.maximum_flow(self.G, source, sink)[0]
        is_feasible = (max_flow == self.total_demand)
        print min_cost, max_flow, is_feasible

        # Delete edges
        for i in servers:
            self.G.remove_edge(source, i)
        for i in self.cus_list:
            self.G.remove_edge(i, sink)
        # Delete nodes
        self.G.remove_node(source)
        self.G.remove_node(sink)

        return min_cost, max_flow, is_feasible

    def test_mcf(self):
        servers = {}
        servers[3] = 5
        servers[7] = 3
        servers[14] = 4
        servers[36] = 3
        servers[69] = 4
        servers[103] = 3
        servers[125] = 3
        servers[129] = 3
        servers[155] = 5
        deploy_cost, server_cost = 0, 0
        for i in servers:
            deploy_cost += self.deploy_cost[i]
            server_cost += self.server_fee[servers[i]]
        min_cost, max_flow, is_feasible = self.compute_mcf(servers)
        total_cost = min_cost + deploy_cost + server_cost
        print total_cost

    def total_cost(self, servers):
        deploy_cost, server_cost = 0, 0
        for i in servers:
            deploy_cost += self.deploy_cost[i]
            server_cost += self.server_fee[servers[i]]
        min_cost, max_flow, is_feasible = self.compute_mcf(servers)
        total_cost = min_cost + deploy_cost + server_cost
        return total_cost, is_feasible

    def cal_outgoing_bandwidth(self, node_id):
        ret = 0
        for u, v, data in self.G.out_edges(node_id, data=True):
            ret += data['capacity']
        return ret

    def cal_ingoing_bandwidth(self, node_id):
        ret = 0
        for u, v, data in self.G.in_edges(node_id, data=True):
            ret += data['capacity']
        return ret

    def cal_outgoing_cost(self, node_id):
        ret = 0.0
        for u, v, data in self.G.out_edges(node_id, data=True):
            ret += data['cost']
        ret /= self.G.out_degree(node_id)
        return ret

    def cal_hops_to_cus(self, node_id):
        ret = 0
        '''for cus in self.cus_list:
            ret += self.spl[node_id][cus]'''
        dis = [self.spl[node_id][cus] for cus in self.cus_list]
        dis = sorted(dis)
        for i in range(3):
            ret += dis[i]
        return ret

    def cal_num_cus_within_two_hops(self, node_id):
        ret = 0
        for cus in self.cus_list:
            if self.spl[node_id][cus] <= 2:
                ret += 1
        return ret

    def cal_num_cus_within_one_hop(self, node_id):
        ret = 0
        for cus in self.cus_list:
            if self.spl[node_id][cus] <= 1:
                ret += 1
        return ret

    def cal_num_cus_within_three_hops(self, node_id):
        ret = 0
        for cus in self.cus_list:
            if self.spl[node_id][cus] <= 3:
                ret += 1
        return ret

    def cal_degrees_of_neighbors(self, node_id):
        ret = 0
        for neighbor in self.G.neighbors(node_id):
            ret += self.G.degree(neighbor)
        return ret

    def cal_bandwidth_of_neighbors(self, node_id):
        ret = 0
        for neighbor in self.G.neighbors(node_id):
            ret += self.G.node[neighbor]['outgoing_bandwidth']
        return ret

    def TOPSIS(self):
        """
        Technique for Order of Preference by Similarity to Ideal Solution.
        :return: None
        """
        # pre-process
        self.pre_process()

        # weighting
        weight = {'outgoing_bandwidth': 0.2,
                  'num_cus_within_one_hops': 0.2,
                  'demand': 0.15,
                  'deploy_cost': 0.12,
                  'outgoing_cost': 0.1,
                  'num_cus_within_two_hops': 0.08,
                  'out_degree': 0.05,
                  'degrees_of_neighbors': 0.05,
                  'hops_to_cus': 0.05}
        #weight = self.determine_weight()
        #print weight
        self.add_weight(weight)

        # determine ideal solution
        pos_ideal_sol, neg_ideal_sol = self.determine_ideal_sol()

        # cal distance to two ideal solutions
        self.cal_dis(pos_ideal_sol, neg_ideal_sol)

    def pre_process(self):
        # nodes_data = self.G.nodes(data=True)
        for attr in self.G.node[0].keys():

            # cal sum_{v in V} (v[node_attr])^2
            sum_square = 0.0
            for i in range(self.G.number_of_nodes()):
                sum_square += (self.G.node[i][attr])**2
                #sum_square += (self.G.node[i][attr])
            sum_square = math.sqrt(sum_square)

            # cal norm attr
            for i in range(self.G.number_of_nodes()):
                self.G.node[i][attr] /= sum_square

    def determine_weight(self):
        weight = {}
        num_nodes = self.G.number_of_nodes()

        # cal entropy
        G = {}
        H = {}
        for attr in self.G.node[0].keys():
            try:
                H[attr] = -( sum(self.G.node[i][attr] * math.log(self.G.node[i][attr]) for i in range(num_nodes))  )
            except:
                print attr
                H[attr] = 0
            G[attr] = 1 - H[attr] / math.log(num_nodes)

        # cal weight
        sum_G = sum(G[attr] for attr in G)
        for attr in self.G.node[0].keys():
            weight[attr] = G[attr] / sum_G

        return weight

    def add_weight(self, weight):
        for attr in self.G.node[0].keys():
            for i in range(self.G.number_of_nodes()):
                self.G.node[i][attr] *= weight[attr]

    def determine_ideal_sol(self):
        positive_ideal_sol = {}
        negative_ideal_sol = {}

        attr = 'outgoing_bandwidth'
        x = sorted( [self.G.node[i][attr] for i in range(self.G.number_of_nodes())] )
        positive_ideal_sol[attr] = x[len(x)-1]
        negative_ideal_sol[attr] = x[0]

        attr = 'num_cus_within_one_hops'
        x = sorted( [self.G.node[i][attr] for i in range(self.G.number_of_nodes())] )
        positive_ideal_sol[attr] = x[len(x)-1]
        negative_ideal_sol[attr] = x[0]

        attr = 'demand'
        x = sorted( [self.G.node[i][attr] for i in range(self.G.number_of_nodes())] )
        positive_ideal_sol[attr] = x[len(x)-1]
        negative_ideal_sol[attr] = x[0]

        attr = 'deploy_cost'
        x = sorted( [self.G.node[i][attr] for i in range(self.G.number_of_nodes())] )
        positive_ideal_sol[attr] = x[0]
        negative_ideal_sol[attr] = x[len(x)-1]

        attr = 'outgoing_cost'
        x = sorted( [self.G.node[i][attr] for i in range(self.G.number_of_nodes())] )
        positive_ideal_sol[attr] = x[0]
        negative_ideal_sol[attr] = x[len(x)-1]

        attr = 'num_cus_within_two_hops'
        x = sorted( [self.G.node[i][attr] for i in range(self.G.number_of_nodes())] )
        positive_ideal_sol[attr] = x[len(x)-1]
        negative_ideal_sol[attr] = x[0]

        attr = 'out_degree'
        x = sorted( [self.G.node[i][attr] for i in range(self.G.number_of_nodes())] )
        positive_ideal_sol[attr] = x[len(x)-1]
        negative_ideal_sol[attr] = x[0]

        attr = 'degrees_of_neighbors'
        x = sorted( [self.G.node[i][attr] for i in range(self.G.number_of_nodes())] )
        positive_ideal_sol[attr] = x[len(x)-1]
        negative_ideal_sol[attr] = x[0]

        attr = 'hops_to_cus'
        x = sorted( [self.G.node[i][attr] for i in range(self.G.number_of_nodes())] )
        positive_ideal_sol[attr] = x[0]
        negative_ideal_sol[attr] = x[len(x)-1]

        return positive_ideal_sol, negative_ideal_sol

    def cal_dis(self, pos_ideal_sol, neg_ideal_sol):
        for i in range(self.G.number_of_nodes()):
            dis_pos, dis_neg = 0.0, 0.0
            for attr in self.G.node[i].keys():
                dis_pos += (self.G.node[i][attr] - pos_ideal_sol[attr])**2
                dis_neg += (self.G.node[i][attr] - neg_ideal_sol[attr])**2
            dis_pos = math.sqrt(dis_pos)
            dis_neg = math.sqrt(dis_neg)
            eva = dis_pos / (dis_pos + dis_neg)  # the smaller, the better
            self.G.add_node(i, eva=eva)
