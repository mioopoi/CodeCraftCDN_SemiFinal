from gurobipy import *

from read_graph import read_graph

class ILPSolver:

    def __init__(self, file_name):
        output_cap, server_fee, deploy_cost, cus_list, tol_demand, graph \
            = read_graph(file_name)

        self.p = server_fee
        self.q = output_cap
        self.o = deploy_cost
        self.cus_list = cus_list
        self.tol_demand = tol_demand
        self.graph = graph

        self.n = graph.number_of_nodes()
        self.m = graph.number_of_edges()
        self.level_num = len(output_cap)
        self.cus_num = len(cus_list)

        # Add "super source"
        source = self.n
        self.graph.add_node(source, demand = self.tol_demand)
        for i in range(self.n):
            self.graph.add_edge(source, i, cost = 0, capacity = 1000000)

        self.x = {}  # 0-1 decision variables: x[j,k] means whether node j is deployed with a server of level k
        self.f = {}  # Integer decision variables: f[i,j] means the flow on edge (i,j)
        self.c = {}  # c[i,j] means the unit cost of edge (i,j)
        self.u = {}  # u[i,j] means the capacity of edge (i,j)
        self.b = {}  # b[i] means the demand of node i

    def solve(self):

        model = Model("CodeCraftCDN")

        print "Create models..."

        # Add variables
        for j in range(self.n):
            for k in range(self.level_num):
                self.x[j,k] = model.addVar(vtype=GRB.BINARY, name="x%d%d" % (j,k))

        for i in range(self.n + 1):
            self.b[i] = self.graph.node[i]['demand']
            #if (self.b[i] != 0):
            #    print self.b[i],
            for edge in self.graph.out_edges(i):
                self.c[edge] = self.graph.get_edge_data(edge[0], edge[1])['cost']
                self.u[edge] = self.graph.get_edge_data(edge[0], edge[1])['capacity']
                self.f[edge] = model.addVar(lb=0, ub=self.u[edge], vtype=GRB.INTEGER, name="f%d,%d" % (edge[0], edge[1]))
        model.update()

        # Add constraints

        # Supply/demand constraints
        for i in range(self.n + 1):
            in_edges = self.graph.in_edges(i)
            in_adj_nodes = []
            for edge in in_edges:
                in_adj_nodes.append(edge[0])

            model.addConstr( quicksum(self.f[i,j] for j in self.graph.adjacency_list()[i]) -
                             quicksum(self.f[j,i] for j in in_adj_nodes) == self.b[i] )

        # Open and flow constraints
        for edge in self.graph.out_edges(self.n):
            model.addConstr( self.f[edge] >= quicksum(self.x[edge[1], k] for k in range(self.level_num)) )
            model.addConstr( self.f[edge] <= quicksum(self.x[edge[1], k] * self.q[k] for k in range(self.level_num)) )
            #self.f[edge] = model.addVar(lb=self.x[edge[1]], ub=self.u[edge]*self.x[edge[1]], vtype=GRB.INTEGER)

        # Assignment constraints (each net node can be deployed with at most one server)
        for j in range(self.n):
            model.addConstr( quicksum(self.x[j,k] for k in range(self.level_num)) <= 1 )

        model.update()

        # Set objective
        model.setObjective(
            quicksum( quicksum( self.x[j,k] * (self.o[j] + self.p[k]) for j in range(self.n) ) for k in range(self.level_num) ) +
            #quicksum( quicksum( self.x[j,k] * (self.o[j]) for j in range(self.n) ) for k in range(self.level_num) ) +
            quicksum( self.c[edge] * self.f[edge] for edge in self.graph.edges() ),
            GRB.MINIMIZE
        )

        model.setParam(GRB.Param.TimeLimit, 7200.0)
        model.update()

        print "Start optimizing..."
        model.optimize()

        solution = model.getAttr('x', self.x)
        server = []
        for j in range(self.n):
            for k in range(self.level_num):
                if (solution[j,k]):
                    server.append((j,k))
                    print (j,k),
        print

        return model.objVal, server


#solver = ILPSolver()
#obj = solver.solve()
#print obj
