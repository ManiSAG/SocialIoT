import socket
from subprocess import check_output,CalledProcessError,TimeoutExpired
from contextlib import contextmanager
import signal
import re
import subprocess
import pymysql



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

def run_complex_command(command,cursor):
    drp_command = "DROP PROCEDURE IF EXISTS select_or_insert;"
    cursor.execute(drp_command)
    print(command)
    cursor.execute(command)
    call_command = "call select_or_insert(); "
    cursor.execute(call_command)

def get_browser_info(ip_addr):
    # Open database connection
    db = pymysql.connect("localhost", "root", "Vahid737", "lan_hosts")
    try:
        cursor = db.cursor()
        command = "SELECT `browser_server`,`browser_comment` FROM `resolution` WHERE `IP_addr` = '{}';".format(ip_addr)
        cursor.execute(command)
        rows = cursor.fetchall()
    except Exception as e:
        print("Exception occured:{}".format(e))

    if len(rows) == 0:
        return ""

    db.commit()
    db.close()
    for row in rows:
        if row[1] is None:
            second= ""
        else:
            second = row[1]
        if row[0] is None:
            first = ""
        else:
            first = row[0]
        return first + " " + second


def resolve_by_db(ip_addr):
    # Open database connection
    db = pymysql.connect("localhost", "root", "Vahid737", "lan_hosts")

    try:

        cursor = db.cursor()
        command = "SELECT ifnull(`Hostname`,`browser_server`) FROM `resolution` WHERE `IP_addr` = '{}';".format(ip_addr)
        cursor.execute(command)
        rows = cursor.fetchall()
    except Exception as e:
        print("Exception occured:{}".format(e))


    if len(rows) == 0:
        command = "create procedure select_or_insert()\
                                begin \
                                    IF NOT EXISTS(SELECT * FROM resolution WHERE `IP_addr` = '{}' ) THEN\
                                        INSERT INTO `resolution`(`IP_addr`) VALUES ('{}');\
                                    END IF;\
                                END ".format(ip_addr, ip_addr)
        run_complex_command(command,cursor)

    db.commit()
    db.close()
    for row in rows:
        return row[-1]

def resolve_by_host(hostname):
    try:
        ip_addr = socket.gethostbyname(hostname)
        return ip_addr
    except socket.gaierror:
        return ""
# this function resolve an IP address using nslookup and nmblookup tool of bash.
def resolve_by_addr(ipa):
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


    return hostname

def resolver_by_avahi(host):
    matchObj = re.match(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", host)
    if matchObj: #its an ip address
        hostname = ''
        output = subprocess.run(['avahi-resolve','--address',host],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        stdoutput = output.stdout.decode('utf-8')
        stderror  = output.stderr.decode('utf-8')
        if stderror == '':
            ip = stdoutput.split()[0]
            hostname = stdoutput.split()[1]
        else:
            ip = host
        return ip,hostname
    else: # host is a hostname
        ip =''
        output = subprocess.run(['avahi-resolve', '--name', host], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdoutput = output.stdout.decode('utf-8')
        stderror = output.stderr.decode('utf-8')
        if stderror == '':
            ip = stdoutput.split()[1]
            hostname = stdoutput.split()[0]
        else:
            hostname = host
        return ip, hostname

def resolve_by_snmp(host):
    #-v2c -c public 146.48.98.195  1.3.6.1.2.1.1.5
    output = subprocess.run(['snmpwalk', '-v2c','-c', 'public', host , "1.3.6.1.2.1.1.5"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdoutput = output.stdout.decode('utf-8')
    stderror = output.stderr.decode('utf-8')
    if stdoutput == "":
        return ""
    else:
        return stdoutput.split()[-1]

def get_type(ip_addr):
    # Open database connection
    db = pymysql.connect("localhost", "root", "Vahid737", "lan_hosts")
    cursor = db.cursor()

    try:
        command = "SELECT `type` FROM `resolution` WHERE `IP_addr` = '{}';".format(ip_addr)
        cursor.execute(command)
        rows = cursor.fetchall()
    except Exception as e:
        print("Exception occured:{}".format(e))


    for row in rows:
        return row[0]