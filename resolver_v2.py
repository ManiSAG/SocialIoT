import subprocess

def resolver_v2(host):
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


print (resolver_v2('146.48.96.188'))