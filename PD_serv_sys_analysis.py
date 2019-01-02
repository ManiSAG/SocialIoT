import heartpy as hp
import numpy as np
import pymysql
from numpy import zeros
import matplotlib.pyplot as plt
from resolver import *


infile = open('arp_analyze_v6.txt','r')
# now I want to calculate Median Absolute Deviation

iterations = 10

db = pymysql.connect("localhost", "root", "Vahid737", "lan_hosts")
cursor = db.cursor()



# create zero array
global data
data = zeros([iterations,3,3])
global unknows
unknows = [0] * iterations

def PD_serv_sys_analyze(threshold,type_from, type_to):
    if type_from == "PD":
        if type_to == "PD":
            data[threshold][0][0] +=1
        elif type_to == "service":
            data[threshold][0][1] +=1
        elif type_to == "sysadmin":
            data[threshold][0][2] +=1
        else:
            unknows[threshold] +=1
    elif type_from == "service":
        if type_to == "PD":
            data[threshold][0][1] +=1
        elif type_to == "service":
            data[threshold][1][1] +=1
        elif type_to == "sysadmin":
            data[threshold][1][2] +=1
        else:
            unknows[threshold] +=1
    elif type_from == "sysadmin":
        if type_to == "PD":
            data[threshold][0][2] +=1
        elif type_to == "service":
            data[threshold][1][2] +=1
        elif type_to == "sysadmin":
            data[threshold][2][2] +=1
        else:
            unknows[threshold] +=1
    else:
        unknows[threshold] +=1


all_lines = infile.readlines()

type_file = open('arp_type_graph_v6.txt','w')

for threshold in range(0,iterations):
    #PD_to_PD = PD_to_service = PD_to_sysadmin = service_to_service = service_to_sysadmin = sysadmin_to_sysadmin = 0
    for line in all_lines:
        line = line[:-1]
        if '[' not in line or ']' not in line:
            continue
        host_from = line.split('  ')[0]
        host_to = line.split('  ')[1]
        interactions = line.split('  ')[-1].replace('[','').replace(']','').split(',')
        try:
            interactions = [int(item) for item in interactions]
        except ValueError as e :
            print(interactions)
        #del data[5:7]

        # method two is to use average frequency per day
        temp = []
        dsum = np.sum(interactions)
        avg_freq = dsum/len(interactions)
        if avg_freq > threshold:
            type_from = get_type(host_from)
            type_to = get_type(host_to)
            if type_from is not None and  type_to is not None and threshold == 9:
                key_resolved = resolve_by_db(host_from)
                host_resolved = resolve_by_db(host_to)
                if key_resolved == "''" or key_resolved is None or key_resolved == "":
                    key_resolved = host_from
                if host_resolved == "''" or host_resolved is None or host_resolved == "":
                    host_resolved = host_to
                type_file.write(key_resolved + " " + host_resolved + " " + str(avg_freq) + " " + type_from + "-" + type_to + "\n")
            PD_serv_sys_analyze(threshold,type_from,type_to)

type_file.close()

pd_pd = []
pd_serv = []
pd_sys = []
serv_serv = []
serv_sys = []
sys_sys = []


for i in range(0,iterations):
    pd_pd.append(data[i][0][0])
    pd_serv.append(data[i][0][1])
    pd_sys.append(data[i][0][2])
    serv_serv.append(data[i][1][1])
    serv_sys.append(data[i][1][2])
    sys_sys.append(data[i][2][2])

print("PD_to_PD : " + str(pd_pd))
print("PD_to_service : " + str(pd_serv))
print("PD_to_sysadmin : " + str(pd_sys))
print("service_to_service : " + str(serv_serv))
print("service_to_sysadmin : " + str(serv_sys))
print("sysadmin_to_sysadmin : " + str(sys_sys))
#print("others : " + str(unknows))

del [unknows[0]]

width = 0.15
my_lables = 'PD_PD', 'PD_service', 'PD_sysadmin', 'service_service', 'service_sys', 'sys_sys'
#my_lables = 'sys_sys'

x_ind = np.arange(iterations)


#x_ind = x_ind[1:]
# Plot
p1 = plt.bar(x_ind, pd_pd, width=width,bottom=pd_serv,color='tab:red')
p2 = plt.bar(x_ind, pd_serv, width=width,bottom=pd_sys,color='tab:green')
p3 = plt.bar(x_ind, pd_sys, width=width,bottom=serv_serv,color='tab:blue')
p4 = plt.bar(x_ind, serv_serv,width=width,bottom=serv_sys,color='tab:brown')
p5 = plt.bar(x_ind, serv_sys,width=width,bottom=sys_sys,color='tab:pink')
p6 = plt.bar(x_ind, sys_sys, width=width,color='tab:orange')
#p7 = plt.bar(x_ind, unknows, width,color='tab:gray')


plt.legend((p1[0], p2[0],p3[0], p4[0],p5[0], p6[0]), (my_lables))
#plt.legend(( p6[0]), (my_lables))

plt.show()
