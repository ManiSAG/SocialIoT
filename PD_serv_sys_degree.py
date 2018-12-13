import numpy as np
import pymysql
from numpy import zeros
import matplotlib.pyplot as plt
from igraph import *
from resolver import *
from time import sleep
infile = open('arp_analyze_v6.txt','r')
# now I want to calculate Median Absolute Deviation

iterations = 50

db = pymysql.connect("localhost", "root", "Vahid737", "lan_hosts")
cursor = db.cursor()

def get_type(ip_addr,cursor):
    # Open database connection
    try:
        command = "SELECT `type` FROM `resolution` WHERE `IP_addr` = '{}';".format(ip_addr)
        cursor.execute(command)
        rows = cursor.fetchall()
    except Exception as e:
        print("Exception occured:{}".format(e))
    for row in rows:
        return row[0]



# create zero array
global data
data = zeros([iterations,3,3])
global unknows
unknows = [0] * iterations

global nd

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

global pd_list

global sys_list

global sys_list

global unknown_list


def get_degree(temp_file,cursor):
    degree_dict = {}
    arp_g = Graph.Read_Ncol(temp_file,weights="if_present",directed=False)
    arp_v = arp_g.vs()
    arp_deg = arp_g.degree(mode="all")
    #sort_index = np.argsort(arp_deg)[::-1]
    for index in range(0,len(arp_deg)):
        ttype = get_type(arp_v[index]['name'],cursor)
        if ttype == "PD":
            pd_list.append(arp_deg[index])
            nd[arp_v[index]['name']] = ('PD',arp_deg[index])
        elif ttype == 'service':
            serv_list.append(arp_deg[index])
            nd[arp_v[index]['name']] = ('service', arp_deg[index])
        elif ttype == "sysadmin":
            sys_list.append(arp_deg[index])
            nd[arp_v[index]['name']] = ('sys', arp_deg[index])
        else:
            unknown_list.append(arp_deg[index])
            nd[arp_v[index]['name']] = ('unknown', arp_deg[index])
        #print(arp_v[index]['name'] + " ==> " + str(arp_deg[index]))
    return nd



all_lines = infile.readlines()

for threshold in range(0,iterations,1):
    pd_list = []
    serv_list = []
    sys_list = []
    unknown_list = []
    nd = {}

    outgraph = open('temporaty.txt','w')
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
            outgraph.write(host_from + " " + host_to + " " + str(avg_freq) + "\n")
            type_from = get_type(host_from, cursor)
            type_to = get_type(host_to, cursor)
            #PD_serv_sys_analyze(threshold,type_from,type_to)
    outgraph.close()
    outgraph = open('temporaty.txt', 'r')
    degrees = get_degree(outgraph,cursor)
    nd_sorted = dict(sorted(nd.items(), key=lambda x: x[1][1],reverse=True))

    print(nd_sorted)

    # for ip in nd_sorted:
    #     ttype ,degree = nd[ip]
    #     if ttype == 'PD':
    #         try:
    #             print( ip + "(" + resolve_by_db(ip) + ")" + " degree is " + str(degree) + ", Browser info: " + get_browser_info(ip) )
    #         except Exception as e:
    #             print(ip)
    #             exit()


    print("pd_list : " + str(pd_list))
    print("serv_list : " + str(serv_list))
    print("sys_list : " + str(sys_list))
    print("unknown_list : " + str(unknown_list))


    out_pic = 'serv_Figures/serv_degree_v2_th' + str(threshold) + ".png"
    my_list = pd_list
    #sleep(5)
    fig = plt.hist(my_list, bins=range(1,max(my_list)+2), color = 'red')


    #sleep(5)
    plt.title("Service Node's degree")
    plt.xlabel("degree")
    plt.ylabel("Frequency")
    #sleep(5)
    plt.savefig(out_pic)

    plt.clf()
#plt.show()


#plt.axis([0,75,0,350])


#width = 0.15
# my_lables = 'PD_PD', 'PD_service', 'PD_sysadmin', 'service_service', 'service_sys', 'sys_sys' , 'unknowns'
#
# x_ind = np.arange(len(unknown_list))
# y_values = []
# for item in unknown_list:
#     y_values.append(degrees[item])
#
# #x_ind = x_ind[1:]
# # Plot
# p1 = plt.bar(x_ind, y_values,color='tab:red')
# # p2 = plt.bar(x_ind, pd_serv, width,bottom=pd_sys,color='tab:green')
# # p3 = plt.bar(x_ind, pd_sys, width,bottom=serv_serv,color='tab:blue')
# # p4 = plt.bar(x_ind, serv_serv, width,bottom=serv_sys,color='tab:brown')
# # p5 = plt.bar(x_ind, serv_sys, width,bottom=sys_sys,color='tab:pink')
# # p6 = plt.bar(x_ind, sys_sys, width,bottom=unknows,color='tab:orange')
# # p7 = plt.bar(x_ind, unknows, width,color='tab:gray')
#
#
# #plt.legend((p1[0], p2[0],p3[0], p4[0],p5[0], p6[0],p7[0]), (my_lables))
#
# plt.show()
