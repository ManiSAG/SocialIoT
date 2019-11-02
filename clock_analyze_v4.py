import numpy as np
import pandas
import datetime as dt
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import LinearLocator
from datetime import timedelta
import nested_dict
import os

#
base_path = '/root/PycharmProjects/printer_social/clock_analyze_pic/'
for filename in os.listdir(base_path):
    os.unlink(base_path + filename)

src_host = '146.48.96.30'
dst_host = '146.48.96.232'

infile = open('arp_analyze_v7.txt','r')
all_lines = infile.readlines()

nd = nested_dict.nested_dict(3, list)


for line in all_lines:
    line = line[:-1]
    if '[' not in line or ']' not in line:
        continue
    host_from = line.split('[')[0].split('  ')[0]
    host_to = line.split('[')[0].split('  ')[1].split(' ')[0]
    if not (host_from == src_host and host_to == dst_host):
        continue

    my_list = line.split('[')[1].split("]")[0].split("', '")
    my_list = [item.replace("'","") for item in my_list]
    day_index = line.split(":")[1].split("[")[0].replace(" ","")
    nd.setdefault(host_from, {}).setdefault(host_to, {}).setdefault(day_index,[])
    nd[host_from][host_to][day_index] = my_list

for host_from in nd:
    for host_to in nd[host_from]:
        for my_day in nd[host_from][host_to]:
            ys = []
            float_object = [float(x) for x in nd[host_from][host_to][my_day]]
            intervals = [t - s for s, t in zip(float_object, float_object[1:])]
            ys.extend([round(x,4) for x in intervals])
            myticks = [datetime.fromtimestamp(x).strftime("%H:%M:%S") for x in intervals]
            xs = np.arange(len(nd[host_from][host_to][my_day])-1)
            plt.xticks(xs,myticks,rotation='vertical')
            plt.tick_params(axis='both', labelsize=6)
            plt.bar(xs, ys, color='tab:red' , align='center' , alpha = 0.5)
            out_pic = base_path + str(host_from) + "--" + str(host_to) + ':' + str(my_day) +  ".png"
            plt.savefig(out_pic)
            plt.clf()
            plt.close()