import numpy as np
import pandas
import datetime as dt
import random
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


infile = open('arp_analyze_v7_resolved.txt','r')
all_lines = infile.readlines()

nd = nested_dict.nested_dict(3, list)


for line in all_lines:
    line = line[:-1]
    if '[' not in line or ']' not in line:
        continue
    host_from = line.split('[')[0].split('  ')[0]
    host_to = line.split('[')[0].split('  ')[1].split(' ')[0]
    my_list = line.split('[')[1].split("]")[0].split("', '")
    my_list = [item.replace("'","") for item in my_list]

    day_index = line.split(":")[1].split("[")[0].replace(" ","")

    nd.setdefault(host_from, {}).setdefault(host_to, {}).setdefault(day_index,[])

    nd[host_from][host_to][day_index] = my_list


for host_from in nd:
    for host_to in nd[host_from]:
        fig, ax = plt.subplots(len(nd[host_from][host_to]), frameon=False)
        counter = 1
        for my_day in nd[host_from][host_to]:
            flag = True
            ys = []
            xs = []
            for item in nd[host_from][host_to][my_day]:
                curr_time = dt.datetime.fromtimestamp(float(item))
                if flag:
                    flag = False
                    # zero_day = curr_time.day
                    # zero_month = curr_time.month
                    start_Date = dt.datetime(curr_time.year, curr_time.month, curr_time.day, 0, 0, 0)
                    end_Date = dt.datetime(curr_time.year, curr_time.month, curr_time.day, 23, 59, 0)
                # curr_time.replace(day=zero_day,month=zero_month)
                xs.append(curr_time)
                ys.append(counter)
            print(len(xs))
            dates = mdates.date2num(xs)
            try:
                if len(nd[host_from][host_to]) == 1:
                    ax.plot_date(dates, ys, 'k.',color=(0, counter / len(all_lines), counter / len(all_lines), 1))
                    # print(host_from + " " + host_to + ":" + str(nd[host_from][host_to]))
                    ax.tick_params(axis='y', labelsize=7)
                    ax.set_yticks([])
                    ax.set_ylabel(ylabel=xs[0].strftime("%d/%b"), rotation='horizontal', labelpad=25)
                    ax.set_xlim(start_Date, end_Date)
                    myFmt = mdates.DateFormatter("%H")
                    ax.xaxis.set_major_formatter(myFmt)
                else:
                    ax[counter-1].plot_date(dates, ys, 'k.',color = (0, counter / len(all_lines), counter / len(all_lines), 1))
                    ax[counter-1].tick_params(axis='y', labelsize=7)
                    ax[counter-1].set_yticks([])
                    ax[counter-1].set_ylabel(ylabel=xs[0].strftime("%d/%b"), rotation='horizontal',labelpad=25)
                    ax[counter-1].set_xlim(start_Date, end_Date)
                    myFmt = mdates.DateFormatter("%H")
                    ax[counter-1].xaxis.set_major_formatter(myFmt)
            except Exception as e:
                print(host_from + " " + host_to + ":" + str(nd[host_from][host_to]))
                exit(1)
            counter +=1

        # plt.show()
        out_pic = 'clock_analyze_pic/' + str(host_from) + "--" + str(host_to) + ".png"
        plt.savefig(out_pic)
        plt.clf()
        plt.close()