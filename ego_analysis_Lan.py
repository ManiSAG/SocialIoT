from nested_dict import *
import numpy as np
import pymysql
from numpy import zeros
import matplotlib.pyplot as plt
from resolver import *
import random
import math
import sys
import os
from textwrap import wrap

infile = open('arp_analyze_v6.txt.bk','r')
# now I want to calculate Median Absolute Deviation

iterations = 10

# base_path = '/root/PycharmProjects/printer_social/ego_analysis/'
# for filename in os.listdir(base_path):
#     for ffile in os.listdir(base_path + filename):
#         os.unlink(base_path+filename + '/' + ffile)





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


all_lines = infile.readlines()


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
        if avg_freq > (threshold):
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

print(nd)


pd_dict = {}
serv_dict = {}
sys_dict = {}
unknown_dict = {}

def calculate_percent(my_list):
    temp_list = []
    for item in my_list:
        temp_list.append(int(item/sum(my_list) * 100))
    return temp_list

my_threshold = 1
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

print("PD : " + str(pd_dict))
print("service : " + str(serv_dict))
print("sysadmin : " + str(sys_dict))
print("others : " + str(unknown_dict))


width = 0.15
my_lables = 'PD','service','sysadmin', 'unknown'
#
x_ind = np.arange(len(pd_dict))

# # Plot
display_threshold = 30 # this means that each plot should have at most 30 xes.


counter = 0
for type_dict in [pd_dict,serv_dict,sys_dict,unknown_dict]:
    partial_lists = []
    my_bins = int(len(type_dict) / display_threshold)
    type_dict_items = list(type_dict.items())
    while len(type_dict_items) > 0 :
        cut_index = min(len(type_dict_items),display_threshold)
        partial_lists.append(dict(type_dict_items[:cut_index]))
        del type_dict_items[:cut_index]

    in_counter = 1
    for part_dict in partial_lists:
        pd_values = [item[0] for item in part_dict.values()]
        serv_values = [item[1] for item in part_dict.values()]
        sys_values = [item[2] for item in part_dict.values()]
        unknown_values = [item[3] for item in part_dict.values()]

        x_ind = range(len(part_dict))
        width = 0.5
        plt.figure(figsize=(25, 10))  # width:20, height:3
        p1 = plt.bar(x_ind, pd_values, color='tab:red',align='edge', width=width)
        p2 = plt.bar(x_ind, serv_values,bottom=pd_values, color='tab:orange',align='edge', width=width)
        p3 = plt.bar(x_ind, sys_values,bottom=[sum(x) for x in zip(serv_values,pd_values)], color='tab:blue',align='edge', width=width)
        p4 = plt.bar(x_ind, unknown_values,bottom=[sum(x) for x in zip(sys_values,serv_values,pd_values)], color='tab:green',align='edge', width=width)

        my_temp = [item.replace('iit.cnr.it.','') for item in part_dict.keys()]
        my_temp = ['\n'.join(wrap(l, 10)) for l in my_temp]

        plt.xticks(x_ind,my_temp ,rotation='vertical',fontsize=12)

        plt.legend(( p1[0], p2[0],p3[0], p4[0]), (my_lables))

        if counter == 0:
            out_pic = 'ego_analysis/pd_ego_figures/pd_ego_part' + str(in_counter) + ".png"
        elif counter == 1:
            out_pic = 'ego_analysis/serv_ego_figures/serv_ego_part' + str(in_counter) + ".png"
        elif counter == 2:
            out_pic = 'ego_analysis/sys_ego_figures/sys_ego_part' + str(in_counter) + ".png"
        if counter == 3:
            out_pic = 'ego_analysis/unknown_ego_figures/unknown_ego_part' + str(in_counter) + ".png"

        plt.savefig(out_pic)
        plt.clf()
        in_counter +=1

    counter += 1