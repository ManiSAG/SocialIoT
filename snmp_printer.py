from pysnmp.hlapi import *
import sys

import time


def walk(host, oid):
    output=""
    for (errorIndication,errorStatus,errorIndex,varBinds) in nextCmd(SnmpEngine(),
        CommunityData('public'), UdpTransportTarget((host, 161)), ContextData(),
        ObjectType(ObjectIdentity(oid)),lexicographicMode=False):
        if errorIndication:
            if errorIndication._ErrorIndication__value == 'requestTimedOut':
                for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(SnmpEngine(),
                                                                                    CommunityData('public',mpModel=0),
                                                                                    UdpTransportTarget((host, 161)),
                                                                                    ContextData(),
                                                                                    ObjectType(ObjectIdentity(oid)),
                                                                                    lexicographicMode=False):
                    if errorIndication:
                        print(errorIndication, file=sys.stderr)
                        flag = True
                        break
                    elif errorStatus:
                        print('%s at %s' % (errorStatus.prettyPrint(),
                                            errorIndex and varBinds[int(errorIndex) - 1][0] or '?'),
                              file=sys.stderr)
                        break
                    else:
                        for varBind in varBinds:
                            output = output + str(varBind) + "\n"
            else:
                print(errorIndication, file=sys.stderr)
                break
        elif errorStatus:
            print('%s at %s' % (errorStatus.prettyPrint(),
                                errorIndex and varBinds[int(errorIndex) - 1][0] or '?'),
                                file=sys.stderr)
            break
        else:
            for varBind in varBinds:
                output = output + str(varBind) + "\n"
    return output

def extract_relations(lines,verbose):
    for line in lines.split('\n') :
        if line == "":
            continue
        line=line.replace("SNMPv2-SMI::mib-2.6.13.1.2.",'')
        temp = line.split()[0].split('.')
        srcIP = '.'.join(temp[0:4])
        srcPort = temp[4]
        dspIP = '.'.join(temp[5:9])
        dstport = temp[9]
        if not verbose:
            if srcIP in ["0.0.0.0","127.0.0.1"]:
                continue
        print (srcIP + ':' + srcPort + '->' + dspIP + ':' + dstport)

printer_addr = open('/root/PycharmProjects/printer_social/captures/printers_new','r')
addrs = printer_addr.readlines()
addrs=[addr[:-1] for addr in addrs]

#s = sched.scheduler(time.time, time.sleep)

#set the script parameters
interval = 1 # interval time between two consequent snmpwalk
verbose = False  # verbose mode to show all addresses in the TCP table

#
# def do_something(sc):
#     print ("Doing stuff...")
#     for addr in addrs:
#         print(addr)
#         output = walk(addr, 'iso.3.6.1.2.1.6.13.1.2.0.0.0')
#         extract_relations(output,verbose)
#         s.enter(interval, 1, do_something, (sc,))
#     s.enter(interval, 1, do_something, (s,))
#     s.run()

while True:

    for addr in addrs:
        print(addr)
        output = walk(addr, 'iso.3.6.1.2.1.6.13.1.2')
        extract_relations(output,verbose)

    time.sleep(interval)