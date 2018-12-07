import heartpy as hp
import numpy as np

infile = open('arp_analyze_v5.txt.bk','r')
# now I want to calculate Median Absolute Deviation
for line in infile.readlines():
    line = line[:-1]
    if '[' not in line or ']' not in line:
        continue
    host_from = line.split('  ')[0]
    host_to = line.split('  ')[1]
    data = line.split('  ')[-1].replace('[','').replace(']','').split(',')
    try:
        data = [int(item) for item in data]
    except ValueError as e :
        print(data)
    del data[5:7]
    #method one is to use Median Absolute Deviation
    temp = []
    med = np.median(data)
    for item in data:
        temp.append(np.absolute(med-item))
    abs_med = str(np.median(temp))

    # method two is to use average frequency per day
    temp = []
    threshold = 1
    dsum = np.sum(data)
    avg_freq = dsum/len(data)
    if avg_freq > threshold:
        print(host_from + " " + host_to + " " + str(avg_freq))
        #print("average Frequency :" +  str(avg_freq) + "  MAD : " + abs_med)
