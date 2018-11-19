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
from re


global timeout_time
timeout_time = 2
def raise_error(signum, frame):
    """This handler will raise an error inside gethostbyname"""
    raise OSError

@contextmanager
def set_signal(signum, handler):
    """Temporarily set signal"""
    old_handler = signal.getsignal(signum)
    signal.signal(signum, handler)
    try:
        yield
    finally:
        signal.signal(signum, old_handler)

@contextmanager
def set_alarm(time):
    """Temporarily set alarm"""
    signal.setitimer(signal.ITIMER_REAL, time)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0) # Disable alarm

@contextmanager
def raise_on_timeout(time):
    """This context manager will raise an OSError unless
    The with scope is exited in time."""
    with set_signal(signal.SIGALRM, raise_error):
        with set_alarm(time):
            yield

global resolved_dict
resolved_dict = {}

# this function resolve an IP address using nslookup and nmblookup tool of bash.
def resolve(ipa):
    hostname = ""
    hostname1 = ""
    hostname2 = ""
    if ipa in resolved_dict:
        return resolved_dict[ipa]
    try:
        with raise_on_timeout(timeout_time):
            a = socket.gethostbyaddr(ipa)
            hostname1 = a[0]
            resolved_dict[ipa] = hostname1
            matchObj = re.match(r"(dhcp|vpn)\d*.iit.cnr.it", hostname1)
            if not matchObj:
                hostname = hostname1
    except OSError:
        pass
    if hostname == "":
        try:
            out = check_output(["nmblookup", "-A", ipa],timeout=timeout_time)
            hostname2=str(out).split("\\n")[1].split()[0].replace("\\t", "")
            hostname = hostname2
        except (CalledProcessError,TimeoutExpired) as e:
            if hostname1 != "":
                hostname = hostname1
            else:
                hostname = ipa

    return hostname

def




input_pcap = '/root/captures/sofar.pcap'
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
    slots.append((my_date.timestamp(),min(next_day.timestamp(),finish_time.timestamp())))
    one_sec = timedelta(seconds=1)
    my_date = next_day + one_sec


print(slots)

cap = pyshark.FileCapture(input_pcap,display_filter="arp and not arp.dst.proto_ipv4 == 146.48.96.1 and not arp.dst.proto_ipv4 == 146.48.96.2")


global relations
relations = {}



nd = nested_dict(2, list)



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
    # x=Decimal(int(pkt.number)/96100)*100
    # output = round(x, 4)
    # print(str(output) + "%")
    my_data = pkt['ARP']
    src_ip = my_data.src_proto_ipv4
    dst_ip = my_data.dst_proto_ipv4
    if src_ip == dst_ip :
        return
    if dst_ip in nd:
        if src_ip in nd[src_ip]:
            src_ip , dst_ip = dst_ip ,src_ip
    pkt_time = str(pkt.frame_info.time_epoch)
    day_index = calculate_slot(pkt_time)
    nd.setdefault(src_ip, {}).setdefault(dst_ip, [0]*(days+1))
    #print(src_ip + "  " + dst_ip + str(nd[src_ip][dst_ip]))
    nd[src_ip][dst_ip][day_index] +=1


def print_highest_layer(pkt):
    print (pkt.highest_layer)


global counter
counter = 0



cap.apply_on_packets(print_conversation_header)

for key in nd:
    for host in nd[key]:
        print(key + "==>" + host + " : " + str(nd[key][host]))


outfile = open('arp_graph_variance.txt','w')



for key in nd:
    for host in nd[key]:
        #key_resolved = resolve(key)
        #host_resolved =resolve(host)
        # temp_sentence = key_resolved + " " + host_resolved + "  " + str(nd[key][host])
        variance = np.var(nd[key][host])
        mean = np.mean(nd[key][host])
        if variance != 0:
            weight = mean / variance
        else:
            weight = mean
        temp_sentence = key + " " + host + "  " + str(weight)
        print(temp_sentence)
        outfile.write(temp_sentence + "\n")


outfile.close()
