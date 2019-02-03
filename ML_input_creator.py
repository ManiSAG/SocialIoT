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
from sklearn.cluster import KMeans
import pandas as pd

infile = open('arp_analyze_v6.txt.bk','r')

global nd
nd = nested_dict(1, list)


def add_to_nd(host_from,index):
    nd[host_from][index] += 1

def PD_serv_sys_analyze( type_to,host_from):
    nd.setdefault(host_from, [0]*(4))
    if type_to == "PD":
        add_to_nd(host_from,  0)
    elif type_to == "service":
        add_to_nd( host_from, 1)
    elif type_to == "sysadmin":
        add_to_nd( host_from, 2)
    else:
        add_to_nd( host_from, 3)

def calculate_percent(my_list):
    temp_list = []
    for item in my_list:
        temp_list.append(int(item/sum(my_list) * 100))
    return temp_list

all_lines = infile.readlines()


threshold = 2
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
        PD_serv_sys_analyze(type_to,host_from)

dataset_file = open('trained_set.csv','w')

for ip in nd:
    dataset_file.write(str(nd[ip][0]) + "," + str(nd[ip][1]) + "," + str(nd[ip][2]) + "," + ip + "\n")

dataset_file.close()
exit(1)

df = pd.DataFrame.from_dict(nd, orient='index')

model = KMeans(n_clusters=3)

# Fitting Model
model.fit(df)

print(model.labels_)

all_predictions = model.predict(df)

for i in range(len(nd)):
    key_resolved = resolve_by_db(list(nd.keys())[i])
    if key_resolved == "''" or key_resolved is None or key_resolved == "":
        key_resolved = list(nd.keys())[i]

    key_type = get_type(list(nd.keys())[i])
    if key_type is None:
        key_type = " "
    print(key_resolved + "(" + key_type + ") ==> " + str(all_predictions[i]) + " " + str(nd[i]))

