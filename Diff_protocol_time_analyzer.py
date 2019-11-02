from pyshark import *
import pyshark
from datetime import datetime,timedelta
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.dates as mdates
from matplotlib.ticker import LinearLocator
from datetime import timedelta
import nested_dict
import os
import subprocess
from matplotlib.lines import Line2D


base_path = '/root/PycharmProjects/printer_social/plot_time_analysis/'
for filename in os.listdir(base_path):
    os.unlink(base_path + filename)

def capinfos(filename):
  output = subprocess.run(['capinfos',filename],stdout=subprocess.PIPE)
  return output.stdout

input_pcap = "/root/captures/cs_general_fixed.pcap"
#for the ARP Packets we read the pcap from the CNR and filter the traffic for arp packets but the ARPs which is not emmited from
#the DHCP Server 146.48.99.254


output = capinfos(input_pcap)

#print (output)
for line in output.decode("utf-8").split('\n'):
    if "First packet time:" in line:
        str_time = " ".join(line.split()[-2:])
    elif "Last packet time:" in line:
        end_time = " ".join(line.split()[-2:])
#print (str_time + " ->" + end_time)


str_time = str_time.split(',')[0]
start_time = datetime.strptime(str_time, '%Y-%m-%d %H:%M:%S')



end_time = end_time.split(',')[0]
finish_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')


duration = finish_time - start_time

global days
days = duration.days


#zero_day = datetime.datetime(start_time.year, start_time.month, start_time.day, 0, 0, 0, 0)
last_day = datetime(finish_time.year, finish_time.month, finish_time.day, 0, 0, 0, 0)

global slots
slots = []
my_date = start_time
while my_date < finish_time:
    next_day = datetime(my_date.year, my_date.month, my_date.day, 23, 59, 59, 0)
    if next_day.weekday() < 5: # Just consider the working days of the week
        slots.append((my_date.timestamp(),min(next_day.timestamp(),finish_time.timestamp())))
    one_sec = timedelta(seconds=1)
    my_date = next_day + one_sec


print(slots)


def calculate_slot(pkt_time):
    counter = 0
    for item in slots:
        if float(pkt_time) > item[0] and float(pkt_time) < (item[1]+1.0) :
            return counter
        else:
            counter +=1

cap:FileCapture=pyshark.FileCapture(
        input_file= input_pcap,
        keep_packets=False,
        use_json=False,
        # display_filter = '''dns.qry.name == "wpad" or nbns.name == "WPAD<00>"'''
        display_filter = '''db-lsp-disc'''
    )

data = nested_dict.nested_dict(2, list)



for pkt in cap:
    pkt_time = str(pkt.frame_info.time_epoch)
    day_index = calculate_slot(pkt_time)
    try:
        src_ip = pkt.ip.src
    except AttributeError as e:
        src_ip = pkt.ipv6.src

    src_mac = pkt.eth.src
    data.setdefault(src_mac, {}).setdefault(day_index,[])

    data[src_mac][day_index].append(pkt_time)

for host_from in data:
    fig, ax = plt.subplots(len(data[host_from]), frameon=False)
    # fig.suptitle('Matplotlib xticklabels Example')
    counter = 1
    for my_day in data[host_from]:
        flag = True
        ys = []
        xs = []
        colors = []
        for item in data[host_from][my_day]:
            curr_time = datetime.fromtimestamp(float(item))
            if flag:
                flag = False
                # zero_day = curr_time.day
                # zero_month = curr_time.month
                start_Date = datetime(curr_time.year, curr_time.month, curr_time.day, 0, 0, 0)
                end_Date = datetime(curr_time.year, curr_time.month, curr_time.day, 23, 59, 0)
            # curr_time.replace(day=zero_day,month=zero_month)

            xs.append(curr_time)
            dates = mdates.date2num(xs)
            ys.append(counter)
        try:
            mksize = 0.5
            if len(data[host_from]) == 1:
                for item in data[host_from][my_day]:
                    ax.plot_date(dates, ys, 'k.',color = 'red',markersize = mksize)
                    ax.set_ylabel(ylabel=xs[0].strftime("%d/%b"), rotation='horizontal', labelpad=25)

                # print(host_from + " " + host_to + ":" + str(nd[host_from][host_to]))
                ax.tick_params(axis='y', labelsize=7)
                ax.set_yticks([])
                # ax.set_xlim(start_Date, end_Date)
                myFmt = mdates.DateFormatter("%H:%M:%S")
                ax.xaxis.set_tick_params(labelsize=8)
                ax.xaxis.set_major_formatter(myFmt)
            else:
                for item in data[host_from][my_day]:
                    ax.plot_date(dates, ys, 'k.',color = 'red',markersize = mksize)
                    ax[counter-1].set_ylabel(ylabel=xs[0].strftime("%d/%b"), rotation='horizontal', labelpad=25)

                ax[counter-1].tick_params(axis='y', labelsize=7)
                ax[counter-1].set_yticks([])
                # ax[counter-1].set_xlim(start_Date, end_Date)
                myFmt = mdates.DateFormatter("%H:%M:%S")
                ax.xaxis.set_tick_params(labelsize=8)
                ax[counter-1].xaxis.set_major_formatter(myFmt)
        except Exception as e:
            print(e)
            print(host_from + " " + str(data[host_from]))
            exit(1)
        counter +=1


    plt.autoscale(enable=True, axis='both', tight=None)
    plt.show()

    # mycolors = ['red', 'blue']
    # lines = [Line2D([0], [0], color=c, linewidth=3, linestyle='-') for c in mycolors]
    # labels = ['NBNS', 'LLMNR']
    # plt.legend(lines, labels)
    out_pic = 'plot_time_analysis/' + str(host_from) + ".png"
    plt.savefig(out_pic)
    plt.clf()
    plt.close()