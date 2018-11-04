import re
import socket
from subprocess import check_output,CalledProcessError


infile = open('/root/PycharmProjects/printer_social/RESULT3','r')

printer_ip = " "
relations = {}
hosts= set()

# this function resolve an IP address using nslookup and nmblookup tool of bash.
def resolve(ipa):
    try:
        a = socket.gethostbyaddr(ipa)
        return a[0]
    except socket.herror:
        try:
            out = check_output(["nmblookup", "-A", ipa])
            hostname=str(out).split("\\n")[1].split()[0].replace("\\t", "")
            return hostname
        except CalledProcessError:
            pass

# for line in infile.readlines():
#     matchObj = re.match(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",line)
#     if matchObj:
#         if '->' not in line:
#             if printer_ip == " ":
#                 printer_ip = line[:-1]
#             relations[printer_ip] = hosts
#             hosts= set()
#             printer_ip = line[:-1]
#         elif '->' in line:
#             if '0.0.0.0' not in line and '127.0.0' not in line:
#                 host_ip = line.split('->')[1].split(':')[0]
#                 hosts.add(host_ip)

# this function reads the input file line by line and fills the relations dictionary
# the keys in this dictionary are printer and value is a set of IP addresses of the hosts that printed on the key printer.

for line in infile.readlines():
    if '->' in line:
        line=line.replace('No SNMP response received before timeout','')
        if '0.0.0.0' not in line and '127.0.0' not in line:
            printer_ip=line.split('->')[0].split(':')[0]
            host_ip=line.split('->')[1].split(':')[0]
            try:
                relations[printer_ip].add(host_ip)
            except KeyError:
                relations[printer_ip] = {host_ip}




print (relations)

# in this section writes the information in the relations dictionary on the file to be used by jupyter to plot graph
# for each pair of hosts which reside in the same set (value of dictionary) should have a line in the output file
# since they printed on the same printer

outfile = open('printer_graph_results3_resolved.txt','w')
for printer_ip in relations:
    if len(relations[printer_ip]) > 0:
        for i in relations[printer_ip]:
            for j in relations[printer_ip]:
                if i != j :
                    try:
                        outfile.write(resolve(i) + "\t" + resolve(j) + "\t1\n")
                    except TypeError:
                        outfile.write(i + "\t" + j + "\t1\n")