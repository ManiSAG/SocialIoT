import socket
from subprocess import check_output,CalledProcessError



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

ips = open('ips2','r')

for ip in ips.readlines():
    ip = ip[:-1]
    try:
        print(ip + " ====> " + resolve(ip))
    except TypeError:
        pass