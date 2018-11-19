import socket
from subprocess import check_output,CalledProcessError,TimeoutExpired
from contextlib import contextmanager
import signal
import re
import subprocess


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

# resolve_by_host('124-171-188-87.dyn.iinet.net.au')