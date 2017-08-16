import os
import numpy as np
from sklearn.naive_bayes import GaussianNB

from node_features import NodeFeatures


class SelectServer:
    def __init__(self):
        self.data, self.target = self.get_train_data()
        gnb = GaussianNB()
        model = gnb.fit(self.data[600:], self.target[600:])
        y_pred = model.predict(self.data[0:600])
        self.servers = {}
        for i in range(len(y_pred)):
            if y_pred[i] != -1:
                self.servers[i] = y_pred[i]
        print self.servers

    def get_optimal_data(self, file_name="./case_solution/solution_mid.txt"):
        optimal_solution = {}

        f = open(file_name)
        first_line = f.readline()
        num_case = int(first_line)
        second_line = f.readline()
        for i in range(num_case):
            line = f.readline()
            x = line.split(') ')
            x[len(x)-1] = x[len(x)-1][0:-2]

            optimal_solution[i] = {}
            for str_tuple in x:
                st = str_tuple[1:]
                server_id, level = st.split(', ')
                server_id, level = int(server_id), int(level)
                optimal_solution[i][server_id] = level

            '''print optimal_solution[i]'''
        f.close()
        return optimal_solution

    def get_train_data(self, start=0, end=9):
        optimal_sol = self.get_optimal_data()

        data = []
        target = []
        path = "./case_example_3/mid/"
        file_list = os.listdir(path)
        case_num = 0
        for file_name in file_list:
            if case_num < start:
                continue

            node_features = NodeFeatures(path + file_name)
            G = node_features.G
            for i in range(G.number_of_nodes()):
                x = [G.node[i][attr] for attr in G.node[i].keys()]
                data.append(x)
                y = -1
                if i in optimal_sol[case_num]:
                    y = optimal_sol[case_num][i]
                target.append(y)

            case_num += 1
            if case_num >= end:
                break
        data = np.array(data)
        target = np.array(target)
        return data, target

    def search(self):
        gnb = GaussianNB()
        model = gnb.fit(self.data[600:], self.target[600:])
        y_pred = model.predict(self.data[0:600])

        servers = {}
        for i in range(len(y_pred)):
            if y_pred[i] != -1:
                servers[i] = y_pred[i]
        nf = NodeFeatures()
        cost, is_feasible = nf.total_cost(servers)
        print cost, is_feasible

        cnt = 0
        best_cost = cost
        while True:
            vis = {}
            for level in range(6):
                tmp_servers = servers.copy()
                for server_id in servers:
                    if servers[server_id] == level and level not in vis:
                        ori_level = servers[server_id]
                        tmp_servers.pop(server_id)
                        cost, is_feasible = nf.total_cost(tmp_servers)
                        if is_feasible and cost < best_cost:
                            best_cost = cost
                            vis[level] = True
                        else:
                            tmp_servers[server_id] = ori_level
                servers = tmp_servers
            print best_cost
            cnt += 1
            if cnt >= 100:
                break