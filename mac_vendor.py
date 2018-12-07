#!/python33/python
#Python 3 Example of how to use https://macvendors.co to lookup vendor from mac address
import urllib.request as urllib2
import json
import codecs
from manuf import manuf
import pymysql
import re
import pyshark
import nested_dict

def mac_vendor(mac_address):
    #API base url,you can also use https if you need
    url = "http://macvendors.co/api/"


    request = urllib2.Request(url+mac_address, headers={'User-Agent' : "API Browser"})
    response = urllib2.urlopen( request )
    #Fix: json object must be str, not 'bytes'
    reader = codecs.getreader("utf-8")
    obj = json.load(reader(response))

    #Print company name
    print (obj['result']['company'])

def ip_to_mac_with_db(host_ip,cursor):

    try:
        command = '''SELECT `MAC_addr` FROM `resolution` WHERE `IP_addr` = '{}' '''.format(host_ip)
        cursor.execute(command)
        rows = cursor.fetchall()
        return rows[0][0]
    except Exception as e:
        print("Exception occured:{}".format(e))

def mac_vendor_manuf(mac_address):
    p = manuf.MacParser(update=False)
    #p.get_all('BC:EE:7B:00:00:00')
    return p.get_manuf(mac_address)
    #p.get_comment('BC:EE:7B:00:00:00')


# Open database connection
db = pymysql.connect("localhost", "root", "Vahid737", "lan_hosts")

# prepare a cursor object using cursor() method
cursor = db.cursor()

input_pcap = '/root/captures/sofar.pcap'


global resolved_dict
resolved_dict = {}


cap = pyshark.FileCapture(input_pcap,display_filter="arp")

def print_conversation_header(pkt):
    src_mac = pkt.arp.src_hw_mac
    src_ip = pkt['ARP'].src_proto_ipv4
    try:
        resolved_dict[src_ip] = src_mac
    except Exception as e:
        print(e)

cap.apply_on_packets(print_conversation_header)

for key in resolved_dict:
    command = "UPDATE `resolution` " \
              "SET `MAC_addr`='{}' WHERE `IP_addr` = '{}'".format(resolved_dict[key], key)
    print(command)
    cursor.execute(command)

# for line in infile.readlines():
#     line = line[:-1]
#     host_from = line.split('  ')[0]
#     host_to = line.split('  ')[1]
#     matchObj = re.match(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", host_from)
#     if matchObj: #its an ip address
#         mac_from = ip_to_mac_with_db(host_from,cursor)
#         if mac_from.replace("'",'') != '' :
#             print(mac_from + "==>" + mac_vendor_manuf(mac_from))
#     matchObj = re.match(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", host_to)
#     if matchObj:  # its an ip address
#         mac_to = ip_to_mac_with_db(host_to,cursor)
#         if mac_to.replace("'",'') != "":
#             print(mac_to + "==>" + mac_vendor_manuf(mac_to))

db.commit()
db.close()