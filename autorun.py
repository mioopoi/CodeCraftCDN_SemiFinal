import os

from solver import ILPSolver

path = "./case_example/low/"
# path = "./case_example_3/high/"
file_list = os.listdir(path)
print file_list
all_obj = []
all_server = []
k = 0

for file_name in file_list:
    solver = ILPSolver(path + file_name)
    obj, server = solver.solve()
    print obj
    print server
    all_obj.append(obj)
    all_server.append(server)
    del solver
    '''
    k += 1
    if k >= 4: break
    '''

print
for i in range(len(all_obj)):
    print "case %d: %d" % (i, all_obj[i])
    #print all_server[i]
    for x in all_server[i]:
        print x,
    print
