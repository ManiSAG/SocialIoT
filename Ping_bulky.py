import  os
import pymysql
import re
def pinger():
    db = pymysql.connect("localhost", "root", "Vahid737", "lan_hosts")
    try:
        cursor = db.cursor()
        command = "SELECT `IP_addr` FROM `resolution` WHERE `type` is NULL and Hostname is NULL and `browser_server` is NULL"
        cursor.execute(command)
        rows = cursor.fetchall()
    except Exception as e:
        print("Exception occured:{}".format(e))
    db.commit()
    db.close()
    outfile = open('ping_result','w')
    for row in rows:
        HOST_UP  = True if os.system("ping -c 1 " + row[0]) is 0 else False
        if HOST_UP:
            outfile.write(str(row[0]) + " ===> " + "UP\n")
        else:
            outfile.write(str(row[0]) + " ===> " + "DOWN\n")

global ip_status
ip_status = {}
ping_file = open('ping_result', 'r')
for line in ping_file.readlines():
    line = line[:-1]
    host=line.split(" ===> ")[0]
    status = line.split(" ===> ")[1]
    ip_status[host] = status
def get_status(host):
    try:
        matchObj = re.match(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", host)
    except TypeError as e:
        print(host)
        exit(1)
    if matchObj:
        try:
            status = ip_status[host]
        except KeyError as e:
            status = "?"
    else:
        status = "UP"
    return status

db = pymysql.connect("localhost", "root", "Vahid737", "lan_hosts")
cursor = db.cursor()
try:
    command = "SELECT MAC_addr, COUNT(*) c FROM resolution GROUP BY MAC_addr HAVING c > 1"
    cursor.execute(command)
    rows = cursor.fetchall()
except Exception as e:
    print("Exception occured:{}".format(e))
#outfile = open('ping_result','w')
for row in rows:
    try:
        command = "SELECT `IP_addr`, ifnull(`Hostname`,`browser_server`) FROM `resolution` WHERE `MAC_addr` = '{}'".format(row[0])
        cursor.execute(command)
        new_rows = cursor.fetchall()
    except Exception as e:
        print("Exception occured:{}".format(e))
    if row[0] is None:
        continue
    print(str(row[0]) + " : " + str([str(item[0]) for item in new_rows]))
    print(" " * (len(row[0]) + 3) + str([str(item[1]) for item in new_rows]))
    #print(" " * (len(row[0]) + 3) + str([get_status(item[0]) for item in new_rows]))
db.commit()
db.close()

