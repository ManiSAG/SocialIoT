from sklearn.cluster import DBSCAN
import pandas as pd
from resolver import *
from nested_dict import *
import matplotlib.pyplot as plt
import numpy as np
from sklearn.semi_supervised import label_propagation
from sklearn.metrics import classification_report, confusion_matrix
from scipy import stats
from resolver import *


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
df = [calculate_percent(x) for x in X]
X = df
known_labels = [1,1,1,1,1,2,2,2,3,3 ,4 ,4 ,4 ,4]
###############[1,2,3,4,5,6,7,8,9,10,11,12,13,14]
ips = array[:,3:4]
y = known_labels + [-1] * (len(ips)-len(known_labels))
indices = np.arange(len(ips))


# df = [calculate_percent(x) for x in X]
df = np.copy(X)

n_total_samples = len(ips)
n_labeled_points = len(known_labels)
max_iterations = 5
types_dict = {1:'PD',2:'printers',3:'services',4:'sysadmin'}

unlabeled_indices = np.arange(n_total_samples)[n_labeled_points:]

lp_model = label_propagation.LabelSpreading(gamma=0.25, max_iter=10)
lp_model.fit(X, y)

predicted_labels = lp_model.transduction_

print("Label Spreading model: %d labeled & %d unlabeled (%d total)"
      % (n_labeled_points, n_total_samples - n_labeled_points,
         n_total_samples))
true_labels = []
temp_labels = []
for i in range(0,len(predicted_labels)):
    key_resolved = resolve_by_db(ips[i][0])
    if key_resolved == "''" or key_resolved is None or key_resolved == "":
        key_resolved = ips[i][0]

    key_type = get_type(ips[i][0])
    if key_type is None:
        key_type = "unknown"
    temp_labels.append(key_type)
    print(key_resolved + " (" + key_type + ") " + str(X[i]) + " : " + types_dict[predicted_labels[i]] )

# counter = 0
# for counter in range(len(predicted_labels)):
#     if temp_labels[counter] == 'unknown':
#         del[true_labels[counter]]
#         del[predicted_labels[counter]]
#     if temp_labels == 'printers'
#     counter+=1