import pyshark
import socket
from subprocess import check_output,CalledProcessError,TimeoutExpired
from nested_dict import nested_dict
from contextlib import contextmanager
import signal
import re
from decimal import Decimal
import time
from datetime import datetime,timedelta
from capinfos import *
from dateutil import tz
import numpy as np
from resolver import *
#from mac_vendor import *


global timeout_time
timeout_time = 2

global resolved_dict
resolved_dict = {}

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


print(slots)

cap = pyshark.FileCapture(input_pcap,display_filter="arp")

nd = nested_dict(3, list)


def calculate_slot(pkt_time):
    counter = 0
    for item in slots:
        if float(pkt_time) > item[0] and float(pkt_time) < (item[1]+1.0) :
            return counter
        else:
            counter +=1

# This is the main function which reads every packet and fills the relations Dictionary.
# This Dict has a key for source IP address and the value is a set of IP addresses that the key is trying to resolve
# through ARP protocol

def print_conversation_header(pkt):
    # if str(pkt.arp.src_hw_mac).startswith('d8:18:d3'):
    #     return
    my_data = pkt['ARP']
    src_ip = my_data.src_proto_ipv4
    dst_ip = my_data.dst_proto_ipv4
    #IP addresses which are related to sysadmin : '146.48.96.3','146.48.96.1','146.48.96.2','146.48.98.155' ,'192.168.100.1'
    if src_ip == '0.0.0.0' or src_ip.startswith('169.254'):
        return
    if dst_ip == '0.0.0.0' or dst_ip.startswith('169.254'):
        return
    if src_ip == dst_ip :
        return
    if dst_ip in nd:
        if src_ip in nd[src_ip]:
            src_ip , dst_ip = dst_ip ,src_ip
    pkt_time = str(pkt.frame_info.time_epoch)
    day_index = calculate_slot(pkt_time)


    if day_index == None:
        return

    nd.setdefault(src_ip, {}).setdefault(dst_ip, {}).setdefault(day_index, [])
    #    nd.setdefault(src_ip, {}).setdefault(dst_ip, [0]*(days+1))
    #nd.setdefault(src_ip, {}).setdefault(dst_ip, {} [0]*(days+1))
    #print(src_ip + "  " + dst_ip + str(nd[src_ip][dst_ip]))
    try:
        nd[src_ip][dst_ip][day_index].append(pkt_time)
    except Exception as e:
        print(str(pkt.number))
        print("src :" + src_ip + " dst :" + dst_ip + " pkt time: " + pkt_time)

def print_highest_layer(pkt):
    print (pkt.highest_layer)


global counter
counter = 0



cap.apply_on_packets(print_conversation_header)

outfile = open('arp_analyze_v7.txt','w')
outfile2 = open('arp_analyze_v7_resolved.txt','w')

print(nd)

for key in nd:
    for host in nd[key]:
        key_resolved = resolve_by_db(key)
        host_resolved = resolve_by_db(host)
        if key_resolved == "''" or key_resolved is None or key_resolved == "":
            key_resolved = key
        if host_resolved == "''" or host_resolved is None or host_resolved == "":
            host_resolved = host
        for day in nd[key][host]:
            print(key_resolved + " --> " + host_resolved + " :" + str(day) + " " + str(nd[key][host][day]))
            temp_sentence = key_resolved + "  " + host_resolved + " :" + str(day) + " " + str(nd[key][host][day])
            outfile2.write(temp_sentence + "\n")
            temp_sentence = key + "  " + host + " :" + str(day) + " " + str(nd[key][host][day])
            outfile.write(temp_sentence  + "\n")

outfile.close()
outfile2.close()

