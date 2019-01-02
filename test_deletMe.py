# create sample data
from datetime import datetime, timedelta
d = datetime.now()
data = [d + timedelta(minutes=i) for i in range(1,100)]


def calculate_hour_slot(pkt_time):
    prev_time = find_previuos_hour(pkt_time)
    hour_timestamp
    return  (pkt_time-prev_time/)
# prepare and group the data
from itertools import groupby

def get_key(d):
    # group by 30 minutes
    k = d + timedelta(minutes=-(d.minute % 30))
    return datetime(k.year, k.month, k.day, k.hour, k.minute, 0)

g = groupby(sorted(data), key=get_key)

# print data
for key, items in g:
    print (key)
    for item in items:
        print ('-', item)