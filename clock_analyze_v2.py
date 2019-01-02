import heartpy as hp
import numpy as np
import pymysql
from numpy import zeros
import matplotlib.pyplot as plt
from resolver import *
import nested_dict
from textwrap import wrap
import os

#
# base_path = '/root/PycharmProjects/printer_social/clock_analysis/'
# for filename in os.listdir(base_path):
#     for ffile in os.listdir(base_path + filename):
#         os.unlink(base_path+filename + '/' + ffile)


infile = open('arp_analyze_v6.txt','r')

iterations = 10

db = pymysql.connect("localhost", "root", "Vahid737", "lan_hosts")
cursor = db.cursor()


def calculate_percent(my_list):
    temp_list = []
    for item in my_list:
        try:
            temp_list.append(int(item/sum(my_list) * 100))
        except ZeroDivisionError as e :
            print(my_list)
            exit(1)
    return temp_list

# create zero array
global data
data = zeros([iterations,3,3])
global unknows
unknows = [0] * iterations




all_lines = infile.readlines()


type_file = open('arp_type_graph_v6.txt','w')

global nd
nd = nested_dict.nested_dict(2, list)

threshold = 2

#PD_to_PD = PD_to_service = PD_to_sysadmin = service_to_service = service_to_sysadmin = sysadmin_to_sysadmin = 0
for line in all_lines:
    line = line[:-1]
    if '[' not in line or ']' not in line:
        continue
    host_from = line.split('[')[0].split('  ')[0]
    host_to = line.split('[')[0].split('  ')[1].split(' ')[0]

    interactions = line.split('[')[1].replace(']','').split(',')
    try:
        interactions = [int(item) for item in interactions]
    except ValueError as e :
        print(interactions)
    #del data[5:7]


    notte = sum(interactions[:8])
    giorno = sum(interactions[8:20])
    sera = sum(interactions[20:])

    nd.setdefault(host_from, {}).setdefault(host_to, [0]*3)
    nd[host_from][host_to][0] += notte
    nd[host_from][host_to][1] += giorno
    nd[host_from][host_to][2] += sera

    #frequency = notte + giorno + sera
pd_pd = {}
pd_serv = {}
pd_sys = {}
serv_serv = {}
serv_sys = {}
sys_sys = {}

for host_from in nd:
    for host_to in nd[host_from]:
        type_from = get_type(host_from)
        type_to = get_type(host_to)
        resolved_from = resolve_by_db(host_from)
        resolved_to = resolve_by_db(host_to)
        if resolved_from == "''" or resolved_from is None or resolved_from == "":
            resolved_from = host_from
        if resolved_to == "''" or resolved_to is None or resolved_to == "":
            resolved_to = host_to
        if sum(nd[host_from][host_to]) < threshold:
            continue

        if type_from == 'PD' and type_to == "PD":
            pd_pd[str(resolved_from +"->" + resolved_to)] = calculate_percent(nd[host_from][host_to])
        elif (type_from == 'PD' and type_to == "service") or (type_from == 'service' and type_to == "PD"):
            pd_serv[str(resolved_from +"->" + resolved_to)] = calculate_percent(nd[host_from][host_to])
        elif (type_from == 'PD' and type_to == "sysadmin") or (type_from == 'sysadmin' and type_to == "PD"):
            pd_sys[str(resolved_from +"->" + resolved_to)] = calculate_percent(nd[host_from][host_to])
        elif type_from == 'service' and type_to == "service":
            serv_serv[str(resolved_from +"->" + resolved_to)] = calculate_percent(nd[host_from][host_to])
        elif (type_from == 'service' and type_to == "sysadmin") or (type_from == 'sysadmin' and type_to == "service"):
            serv_sys[str(resolved_from +"->" + resolved_to)] = calculate_percent(nd[host_from][host_to])
        elif type_from == 'sysadmin' and type_to == "sysadmin":
            sys_sys[str(resolved_from +"->" + resolved_to)] = calculate_percent(nd[host_from][host_to])

print("PD----PD")
for key in pd_pd:
    print(key + " : " + str(pd_pd[key]))

print("PD----Service")
for key in pd_serv:
    print(key + " : " + str(pd_serv[key]))


print("PD----Sysadmin")
for key in pd_sys:
    print(key + " : " + str(pd_sys[key]))


print("Service----Service")
for key in serv_serv:
    print(key + " : " + str(serv_serv[key]))

print("Service----Sysadmin")
for key in serv_sys:
    print(key + " : " + str(serv_sys[key]))

print("Sysadmin----Sysadmin")
for key in sys_sys:
    print(key + " : " + str(sys_sys[key]))

#Begin plotting
display_threshold = 60
counter = 0



for type_dict in [pd_pd,pd_serv,pd_sys,serv_serv,serv_sys,sys_sys]:
    partial_lists = []
    my_bins = int(len(type_dict) / display_threshold)
    type_dict_items = list(type_dict.items())
    while len(type_dict_items) > 0 :
        cut_index = min(len(type_dict_items),display_threshold)
        partial_lists.append(dict(type_dict_items[:cut_index]))
        del type_dict_items[:cut_index]

    in_counter = 1
    for part_dict in partial_lists:
        notte_values = [item[0] for item in part_dict.values()]
        giorno_values = [item[1] for item in part_dict.values()]
        sera_values = [item[2] for item in part_dict.values()]
        x_ind = np.arange(len(part_dict))
        #width = 0.15
        my_lables = 'notte values', 'Giorno values', 'sera values'

        #plt.figure(figsize=(25, 10))  # width:20, height:3

        p1 = plt.bar(x_ind,sera_values,bottom=[sum(x) for x in zip(notte_values,giorno_values)],color='tab:red')
        p2 = plt.bar(x_ind, giorno_values, bottom=notte_values,color='tab:green')
        p3 = plt.bar(x_ind, notte_values, color='tab:blue')

        #my_temp = [item.replace('iit.cnr.it.','') for item in type_dict.keys()]
        #my_temp = ['\n'.join(wrap(l, 10)) for l in my_temp]

        #plt.xticks(x_ind,my_temp ,rotation='vertical',fontsize=8)
        plt.legend((p1[0], p2[0], p3[0]), (my_lables))

        if counter == 0:
            out_pic = 'clock_analysis/pd_pd_figures/pd_pd_part' + str(in_counter) + ".png"
        elif counter == 1:
            out_pic = 'clock_analysis/pd_serv_figures/pd_serv_part' + str(in_counter) + ".png"
        elif counter == 2:
            out_pic = 'clock_analysis/pd_sys_figures/pd_sys_part' + str(in_counter) + ".png"
        if counter == 3:
            out_pic = 'clock_analysis/serv_serv_figures/serv_serv_part' + str(in_counter) + ".png"
        if counter == 4:
            out_pic = 'clock_analysis/serv_sys_figures/serv_sys_part' + str(in_counter) + ".png"
        if counter == 5:
            out_pic = 'clock_analysis/sys_sys_figures/sys_sys_part' + str(in_counter) + ".png"
        plt.savefig(out_pic)

        plt.clf()
        in_counter +=1

    counter += 1


