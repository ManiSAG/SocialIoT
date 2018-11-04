import re
import sys

infile = open('printer_graph_results3_resolved.txt' ,'r')

showIPs= False
if len(sys.argv) > 1:
    if sys.argv[1] == "-v":
        showIPs = True

for line in infile.readlines():
    ipfrom = line.split()[0]
    ipto   = line.split()[1]

    #matchObj = re.match(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", ipfrom)
    matchObj = re.match(r"(dhcp|vpn)\d*.iit.cnr.it", ipfrom)
    if matchObj:
        continue
    matchObj = re.match(r"(dhcp|vpn)\d*.iit.cnr.it", ipto)
    if matchObj:
        continue
    if not showIPs :
        matchObj = re.match(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", line)
        if matchObj:
            continue

    print(line)


