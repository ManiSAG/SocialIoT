from sklearn.cluster import DBSCAN
import pandas as pd
from resolver import *
from nested_dict import *
import matplotlib.pyplot as plt
import numpy as np

def calculate_percent(my_list):
    temp_list = []
    for item in my_list:
        try:
            temp_list.append(int(item/sum(my_list) * 100))
        except ZeroDivisionError as e:
            return my_list
    return temp_list

# Load dataset
url = "trained_set.csv"
names = ['PD', 'service', 'sysadmin', 'ip']
dataset = pd.read_csv(url,names=names)
# Split-out validation dataset
array = dataset.values
X = array[:,0:3]
y = array[:,3:4]

df = [calculate_percent(x) for x in X]
# df = X

distance = 50
# dbscan = DBSCAN(eps=0.3, min_samples=10)
dbscan = DBSCAN(eps=distance)

# dbscan.fit(df)
# print(dbscan.labels_)
all_predictions = dbscan.fit_predict(df)

nd = nested_dict(2, int)

outfile = open('ML_dbscan_percent_%d' % distance,'w')

for i in range(len(y)):
    nd.setdefault(all_predictions[i], {}).setdefault("PD",0)
    nd.setdefault(all_predictions[i], {}).setdefault("service", 0)
    nd.setdefault(all_predictions[i], {}).setdefault("sysadmin", 0)
    nd.setdefault(all_predictions[i], {}).setdefault("unknown", 0)

    key_resolved = resolve_by_db(y[i][0])
    if key_resolved == "''" or key_resolved is None or key_resolved == "":
        key_resolved = y[i][0]

    key_type = get_type(y[i][0])
    if key_type is None:
        key_type = "unknown"
    try:
        nd[all_predictions[i]][key_type] += 1
    except KeyError as e:
        print(key_resolved + "(" + key_type + ")" + " " * (46 - len(key_resolved) - len(key_type) - 2) + "==> " + str(
            all_predictions[i]) + " " + str(df[i]))

    outfile.write(key_resolved + "(" + key_type + ")" + " " * (46-len(key_resolved) - len(key_type) - 2) + "==> " + str(all_predictions[i]) + " " + str(df[i]) + "\n")

outfile.close()
# for it2
pd_param_values = []
serv_param_values = []
sys_param_values = []
unknown_param_values = []


for cluster  in nd:
    pd_param_values.append(nd[cluster]["PD"])
    serv_param_values.append(nd[cluster]["service"])
    sys_param_values.append(nd[cluster]["sysadmin"])
    unknown_param_values.append(nd[cluster]["unknown"])

x_ind = np.arange(len(pd_param_values))

width = 0.15
my_lables = 'PD','service','sysadmin', 'unknown'

p1 = plt.bar(x_ind, pd_param_values, color='tab:red',align='edge')
p2 = plt.bar(x_ind, serv_param_values,bottom=pd_param_values, color='tab:orange',align='edge')
p3 = plt.bar(x_ind, sys_param_values,bottom=[sum(x) for x in zip(serv_param_values,pd_param_values)], color='tab:blue',align='edge')
p4 = plt.bar(x_ind, unknown_param_values,bottom=[sum(x) for x in zip(sys_param_values,serv_param_values,pd_param_values)], color='tab:green',align='edge')

plt.xticks(x_ind,nd.keys())

plt.legend(( p1[0], p2[0],p3[0], p4[0]), (my_lables))

plt.show()