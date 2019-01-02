import numpy as np
import pandas
import datetime as dt
import random
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import LinearLocator
from datetime import timedelta
from cycler import cycler


infile = open('sample.txt','r')
all_lines = infile.readlines()

counter = 1
fig, ax = plt.subplots(len(all_lines),frameon=False)

for line in all_lines:
    flag = True
    xs = []
    ys = []
    my_list = []
    line = line[:-1]
    my_list = line.split('[')[1].split("]")[0].split("', '")
    my_list = [item.replace("'","") for item in my_list]


    for item in my_list:
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
    if len(all_lines) != 1:
        ax[counter-1].plot_date(dates, ys, 'k.',color = (0, counter / len(all_lines), counter / len(all_lines), 1))
        ax[counter-1].tick_params(axis='y', labelsize=7)
        ax[counter-1].set_yticks([])
        # ax[counter - 1].set(ylabel=)
        ax[counter-1].set_ylabel(ylabel=xs[0].strftime("%d/%b"), rotation='horizontal',labelpad=25)

        fig.autofmt_xdate()

        #pd_times = [pandas.to_datetime(float(item),unit='s') for item in my_list]

        ax[counter-1].set_xlim(start_Date, end_Date)

        myFmt = mdates.DateFormatter("%H:%M")
        ax[counter-1].xaxis.set_major_formatter(myFmt)
    else:
        ax.plot_date(dates, ys, 'k.', color=(0, counter / len(all_lines), counter / len(all_lines), 1))
        ax.tick_params(axis='y', labelsize=7)
        ax.set_yticks([])
        # ax[counter - 1].set(ylabel=)
        ax.set_ylabel(ylabel=xs[0].strftime("%d/%b"), rotation='horizontal', labelpad=25)

        fig.autofmt_xdate()

        # pd_times = [pandas.to_datetime(float(item),unit='s') for item in my_list]

        ax.set_xlim(start_Date, end_Date)

        myFmt = mdates.DateFormatter("%H:%M")
        ax.xaxis.set_major_formatter(myFmt)
    counter +=1


plt.show()
plt.close()