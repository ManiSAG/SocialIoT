from nested_dict import *
import numpy as np
import pymysql
from numpy import zeros
import matplotlib.pyplot as plt
from resolver import *
import math
from scipy import stats
import sys
import os
from textwrap import wrap

infile = open('arp_analyze_v6.txt.bk','r')
# now I want to calculate Median Absolute Deviation

iterations = 20

base_path = '/root/PycharmProjects/printer_social/ego_analysis_v2/'
for filename in os.listdir(base_path):
    os.unlink(base_path+filename)


# create zero array
global nd
nd = nested_dict(2, list)


def add_to_nd(threshold,host_from,index):
    nd[threshold][host_from][index] += 1

def PD_serv_sys_analyze(threshold, type_to,host_from):
    nd.setdefault(threshold, {}).setdefault(host_from, [0]*(4))
    if type_to == "PD":
        add_to_nd(threshold,host_from,  0)
    elif type_to == "service":
        add_to_nd(threshold, host_from, 1)
    elif type_to == "sysadmin":
        add_to_nd(threshold, host_from, 2)
    else:
        add_to_nd(threshold, host_from, 3)

def get_statistics(res_dict,my_dict):
    pd_values = [item[0] for item in my_dict.values()]
    serv_values = [item[1] for item in my_dict.values()]
    sys_values = [item[2] for item in my_dict.values()]
    unknown_values = [item[3] for item in my_dict.values()]

    res_dict.setdefault("PD", {})
    res_dict.setdefault("serv", {})
    res_dict.setdefault("sys", {})
    res_dict.setdefault("unknown", {})

    res_dict["PD"]["Mean"] = np.mean(pd_values)
    res_dict["PD"]["Variance"] = np.var(pd_values)

    res_dict["serv"]["Mean"] = np.mean(serv_values)
    res_dict["serv"]["Variance"] = np.var(serv_values)

    res_dict["sys"]["Mean"] = np.mean(sys_values)
    res_dict["sys"]["Variance"] = np.var(sys_values)

    res_dict["unknown"]["Mean"] = np.mean(unknown_values)
    res_dict["unknown"]["Variance"] = np.var(unknown_values)

def calculate_percent(my_list):
    temp_list = []
    for item in my_list:
        temp_list.append(int(item/sum(my_list) * 100))
    return temp_list

all_lines = infile.readlines()


for threshold in range(0,iterations+1):
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
        if avg_freq > (threshold/10):
            type_from = get_type(host_from)
            type_to = get_type(host_to)
            if type_from is not None and  type_to is not None :
                key_resolved = resolve_by_db(host_from)
                host_resolved = resolve_by_db(host_to)
                if key_resolved == "''" or key_resolved is None or key_resolved == "":
                    key_resolved = host_from
                if host_resolved == "''" or host_resolved is None or host_resolved == "":
                    host_resolved = host_to
            PD_serv_sys_analyze(threshold,type_to,host_from)




result =  nested_dict(4,float)

for my_threshold in nd:
    pd_dict = {}
    serv_dict = {}
    sys_dict = {}
    unknown_dict = {}
    for ip in nd[my_threshold]:
        ttype = get_type(ip)
        host_resolved = resolve_by_db(ip)
        if host_resolved == "''" or host_resolved is None or host_resolved == "":
            host_resolved = ip
        if ttype == "PD":
            pd_dict[host_resolved] = calculate_percent(nd[my_threshold][ip])
        elif ttype == 'service':
            serv_dict[host_resolved] = calculate_percent(nd[my_threshold][ip])
        elif ttype == "sysadmin":
            sys_dict[host_resolved] = calculate_percent(nd[my_threshold][ip])
        else:
            unknown_dict[host_resolved] = calculate_percent(nd[my_threshold][ip])

    result.setdefault(my_threshold, {}).setdefault("PD", {})
    result.setdefault(my_threshold, {}).setdefault("serv", {})
    result.setdefault(my_threshold, {}).setdefault("sys", {})
    result.setdefault(my_threshold, {}).setdefault("unknown", {})

    get_statistics(result[my_threshold]["PD"],pd_dict)

    get_statistics(result[my_threshold]["serv"],serv_dict)

    get_statistics(result[my_threshold]["sys"],sys_dict)

    get_statistics(result[my_threshold]["unknown"],unknown_dict)

print(result)

# for threshold in result:
#     print("Threshold : " + str(int(threshold)/10))
#     for ttype in result[threshold]:
#         if ttype == "PD":
#             print("\tPD composition : ")
#         elif ttype == "serv":
#             print("\tserv composition : ")
#         elif ttype == "sys":
#             print("\tSYSAdmin composition : ")
#         elif ttype == "unknown":
#             print("\tUnknown composition : ")
#         for tttype in result[threshold][ttype]:
#             print("\t\t" + str(tttype) + " : (Mean : " + str(math.ceil(result[threshold][ttype][tttype]["Mean"])) + " , Variance : " + str(math.ceil(result[threshold][ttype][tttype]["Variance"])) + ")" )


width = 0.15
my_lables = 'PD','service','sysadmin', 'unknown'
#

x_ind = np.arange(len(result.keys()))

# # Plot

counter = 0

param = "Variance"
for ttype in  ['PD','serv','sys', 'unknown']:

    pd_param_values = []
    serv_param_values = []
    sys_param_values = []
    unknown_param_values = []


    for threshold  in result:
        pd_param_values.append(result[threshold][ttype]["PD"][param])
        serv_param_values.append(result[threshold][ttype]["serv"][param])
        sys_param_values.append(result[threshold][ttype]["sys"][param])
        unknown_param_values.append(result[threshold][ttype]["unknown"][param])

    p1 = plt.bar(x_ind, pd_param_values, color='tab:red',align='edge')
    p2 = plt.bar(x_ind, serv_param_values,bottom=pd_param_values, color='tab:orange',align='edge')
    p3 = plt.bar(x_ind, sys_param_values,bottom=[sum(x) for x in zip(serv_param_values,pd_param_values)], color='tab:blue',align='edge')
    p4 = plt.bar(x_ind, unknown_param_values,bottom=[sum(x) for x in zip(sys_param_values,serv_param_values,pd_param_values)], color='tab:green',align='edge')

    plt.legend(( p1[0], p2[0],p3[0], p4[0]), (my_lables))

    out_pic = base_path + ttype + '_ego_' + param + '.png'

    plt.savefig(out_pic)
    plt.clf()
