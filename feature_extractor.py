from nested_dict import nested_dict
from datetime import datetime,timedelta
from capinfos import *
import numpy as np
from resolver import *




input_pcap = '/root/captures/arp.pcap'
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

def when_packet(tmstmp):
    datetime_obj = datetime.fromtimestamp(float(tmstmp))
    if datetime_obj.hour < 7:
        return 0
    elif datetime_obj.hour >= 7 and datetime_obj.hour < 19:
        return 1
    elif datetime_obj.hour >= 19 and datetime_obj.hour <= 23:
        return 2




infile = open('arp_analyze_v7.txt')

connection_from = nested_dict(2, list)
connection_to = nested_dict(2, list)


outgoing_degree = {}
incoming_degree = {}


total_outgoing_pkts = dict()
total_incoming_pkts = dict()

for line in infile.readlines():
    line = line[:-1]
    host_from = line.split('[')[0].split('  ')[0]
    host_to = line.split('[')[0].split('  ')[1].split(' ')[0]
    day_index = line.split(":")[1].split("[")[0].replace(" ", "")

    try:
        outgoing_degree[host_from].add(host_to)
    except KeyError:
        outgoing_degree[host_from] = {host_to}

    try:
        incoming_degree[host_to].add(host_from)
    except KeyError:
        incoming_degree[host_to] = {host_from}

    interactions = line.split('[')[1].replace(']','').split(',')
    interactions = [float(x.replace("'","")) for x in interactions]

    my_dict_from = connection_from.setdefault(host_from, {})
    my_dict_to = connection_to.setdefault(host_to, {})
    for item in range(len(slots)):
        my_dict_from.setdefault(item, [])
        my_dict_to.setdefault(item, [])

    try:
        connection_from[host_from][int(day_index)].append(interactions)
    except KeyError as e:
        connection_from[host_from][int(day_index)] = interactions

    try:
        connection_to[host_to][int(day_index)].append(interactions)
    except KeyError as e:
        connection_to[host_to][int(day_index)] = interactions


notte_from_freq = {}
giorno_from_freq = {}
sera_from_freq = {}

std_diff_outgoing = nested_dict(2,list)
Mean_std_diff_outgoing = nested_dict(2,float)

daily_outgoing_pkts = nested_dict(2, list)
Mean_daily_outgoing_pkts = nested_dict(2, float)

for ip in connection_from:

    total_outgoing_pkts.setdefault(ip,0)
    total_incoming_pkts.setdefault(ip,0)
    notte_from_freq.setdefault(ip,0)
    giorno_from_freq.setdefault(ip, 0)
    sera_from_freq.setdefault(ip, 0)

    for day in connection_from[ip]:
        daily_outgoing_pkts.setdefault(ip, {}).setdefault(day,[])
        std_diff_outgoing.setdefault(ip,{}).setdefault(day,[])
        for llist in connection_from[ip][day]:

            total_outgoing_pkts[ip] += len(llist)

            #calculate distribution of connection between 3 time perdios of day
            for tmstmp in llist:
                time_index = when_packet(tmstmp)
                if time_index == 0:
                    notte_from_freq[ip] += 1
                elif time_index == 1:
                    giorno_from_freq[ip] += 1
                else:
                    sera_from_freq[ip] += 1

            #calculation for different btw consecutive timestamp
            if len(llist) > 1:
                float_object = [float(x) for x in llist]
                intervals = [t - s for s, t in zip(float_object, float_object[1:])]
                variance = np.var(intervals)
                try:
                    std_diff_outgoing[ip][day].append(variance)
                except KeyError:
                    std_diff_outgoing[ip][day] = variance
            else:
                try:
                    std_diff_outgoing[ip][day].append(0)
                except KeyError:
                    std_diff_outgoing[ip][day] = 0

            daily_outgoing_pkts[ip][day].append((len(llist)))
        # if len(daily_outgoing_pkts[ip][day]) == 0:
        #     continue

        Mean_daily_outgoing_pkts.setdefault(ip,{}).setdefault(day,0.0)
        if len(daily_outgoing_pkts[ip][day]) > 0:
            Mean_daily_outgoing_pkts[ip][day]= np.mean(daily_outgoing_pkts[ip][day])

        Mean_std_diff_outgoing.setdefault(ip,{}).setdefault(day,0.0)
        if len(std_diff_outgoing[ip][day]) > 0:
            Mean_std_diff_outgoing[ip][day] = np.mean(std_diff_outgoing[ip][day])


notte_to_freq = {}
giorno_to_freq = {}
sera_to_freq = {}


std_diff_incoming = nested_dict(2,list)
Mean_std_diff_incoming = nested_dict(1,list)

daily_incoming_pkts = nested_dict(2, list)
Mean_daily_incoming_pkts = nested_dict(2, float)
for ip in connection_to:
    total_outgoing_pkts.setdefault(ip, 0)
    total_incoming_pkts.setdefault(ip, 0)
    notte_to_freq.setdefault(ip, 0)
    giorno_to_freq.setdefault(ip, 0)
    sera_to_freq.setdefault(ip, 0)
    for day in connection_to[ip]:
        daily_incoming_pkts.setdefault(ip, {}).setdefault(day,[])
        std_diff_incoming.setdefault(ip,{}).setdefault(day,[])
        for llist in connection_to[ip][day]:

            total_incoming_pkts[ip] += len(llist)

            #calculate distribution of connection between 3 time perdios of day
            for tmstmp in llist:
                time_index = when_packet(tmstmp)
                if time_index == 0:
                    notte_to_freq[ip] += 1
                elif time_index == 1:
                    giorno_to_freq[ip] += 1
                else:
                    sera_to_freq[ip] += 1

            #calculation for different btw consecutive timestamp
            if len(llist) > 1:
                float_object = [float(x) for x in llist]
                intervals = [t - s for s, t in zip(float_object, float_object[1:])]
                variance = np.var(intervals)
                try:
                    std_diff_incoming[ip][day].append(variance)
                except KeyError:
                    std_diff_incoming[ip][day] = variance
            else:
                try:
                    std_diff_incoming[ip][day].append(0)
                except KeyError:
                    std_diff_incoming[ip][day] = 0

            daily_incoming_pkts[ip][day].append(len(llist))


        Mean_daily_incoming_pkts.setdefault(ip,{}).setdefault(day,0.0)
        Mean_std_diff_incoming.setdefault(ip,{}).setdefault(day,0)

        if len(daily_incoming_pkts[ip][day]) > 0:
            Mean_daily_incoming_pkts[ip][day] = np.mean(daily_incoming_pkts[ip][day])
        if len(std_diff_incoming[ip][day]) > 0 :
            Mean_std_diff_incoming[ip][day]= np.mean(std_diff_incoming[ip][day])


#Now we want to create the dataset file to be used by Machine Learning algorithm
#write Total number from and to

newfile = open("new_features_df.csv",'w')

ultimate_lines = {}

for ip in total_outgoing_pkts:
    ultimate_lines.setdefault(ip,'')
    ultimate_lines[ip] += str(total_incoming_pkts[ip]) + ','
    ultimate_lines[ip] += str(total_outgoing_pkts[ip]) + ','

#adding Mean frequency of each day as new features
for ip in ultimate_lines:
    if Mean_daily_incoming_pkts[ip] != {}:
        ultimate_lines[ip] += (','.join([str(Mean_daily_incoming_pkts[ip][x]) for x in Mean_daily_incoming_pkts[ip]])) + ','
    else:
        ultimate_lines[ip] += ','.join([str(0)] * len(slots)) + ','


    if Mean_daily_outgoing_pkts[ip] != {}:
        ultimate_lines[ip] += (','.join([str(Mean_daily_outgoing_pkts[ip][x]) for x in Mean_daily_outgoing_pkts[ip]])) + ','
    else:
        ultimate_lines[ip] += ','.join([str(0)] * len(slots)) + ','

    try:
        ultimate_lines[ip] += str(len(incoming_degree[ip])) + ','
    except:
        ultimate_lines[ip] += str(0) + ','

    try:
        ultimate_lines[ip] += str(len(outgoing_degree[ip])) + ','
    except KeyError:
        ultimate_lines[ip] += str(0) + ','

    if len(Mean_std_diff_incoming[ip]) != 0:
        ultimate_lines[ip] += (','.join([str(Mean_std_diff_incoming[ip][x]) for x in Mean_std_diff_incoming[ip]])) + ','
    else:
        ultimate_lines[ip] += ','.join([str(0)] * len(slots)) + ','

    if len(Mean_std_diff_outgoing[ip]) != 0:
        ultimate_lines[ip] += (','.join([str(Mean_std_diff_outgoing[ip][x]) for x in Mean_std_diff_outgoing[ip]])) + ','
    else:
        ultimate_lines[ip] += ','.join([str(0)] * len(slots)) + ','

    try:
        ultimate_lines[ip] += str(notte_to_freq[ip]) + ','
    except KeyError:
        ultimate_lines[ip] += str(0) + ','

    try:
        ultimate_lines[ip] += str(giorno_to_freq[ip]) + ','
    except KeyError:
        ultimate_lines[ip] += str(0) + ','

    try:
        ultimate_lines[ip] += str(sera_to_freq[ip]) + ','
    except KeyError:
        ultimate_lines[ip] += str(0) + ','

    try:
        ultimate_lines[ip] += str(notte_from_freq[ip]) + ','
    except KeyError:
        ultimate_lines[ip] += str(0) + ','

    try:
        ultimate_lines[ip] += str(giorno_from_freq[ip]) + ','
    except KeyError:
        ultimate_lines[ip] += str(0) + ','

    try:
        ultimate_lines[ip] += str(sera_from_freq[ip]) + ','
    except KeyError:
        ultimate_lines[ip] += str(0) + ','
    print(ip + "-->" + str(len(ultimate_lines[ip].split(','))))
    ultimate_lines[ip] += ip
    newfile.write(ultimate_lines[ip] + "\n")

newfile.close()