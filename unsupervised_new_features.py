# Importing Modules
from sklearn.model_selection import train_test_split
from sklearn.cluster import KMeans
import pandas as pd
from resolver import *
from nested_dict import *
import matplotlib.pyplot as plt
import numpy as np
from sklearn import model_selection
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
from collections import defaultdict




# Load dataset
url = "new_features_df.csv"
names = ['total_incoming_pkts', 'total_outgoing_pkts']
Mean_daily_incoming_names = [('Mean_daily_incoming_pkts_' + str(x)) for x in range(19)]
Mean_daily_outgoing_names = [('Mean_daily_outgoing_pkts_' + str(x)) for x in range(19)]
names = names + Mean_daily_incoming_names + Mean_daily_outgoing_names
names.extend(['incoming_degree' , 'outgoing_degree'])

Mean_std_diff_incoming_names = [('Mean_std_diff_incoming_' + str(x)) for x in range(19)]
Mean_std_diff_outgoing_names = [('Mean_std_diff_outgoing_' + str(x)) for x in range(19)]
names = names + Mean_std_diff_incoming_names + Mean_std_diff_outgoing_names

names.extend(['notte_to_freq' , 'giorno_to_freq' , 'sera_to_freq' , 'notte_from_freq' , 'giorno_from_freq' , 'sera_from_freq'])


feature_names = names.copy()

names.append('ip')
print(','.join(names))
exit()
feature_dict = defaultdict(int)
for idx, item in enumerate(names):
    feature_dict[item] = idx


label_dict = {'PD': 0, 'service': 1, 'sysadmin': 2, 'unknown': 3}

dataset = pd.read_csv(url,names=names)
# Split-out validation dataset
array = dataset.values
# df = pd.DataFrame(dataset,columns=feature_names)

known_df = pd.DataFrame(columns=names + ['label'])
unknown_df = pd.DataFrame(columns=names)
for index, row in dataset.iterrows():
    key_type = get_type(row['ip'])
    if key_type is not None:
        row['label'] = label_dict[key_type]
        known_df = known_df.append(row)
    else:
        unknown_df = unknown_df.append(row)

    # print(row['PD'], row['service',row['sysadmin'],row['ip']])


model = KMeans(init='k-means++', max_iter=300, n_init=10, random_state=0)
accuracies = []
for i in range(1,11):

    model.fit(known_df[feature_names])
    pred_y = model.predict(unknown_df[feature_names])

    print(pred_y)
# print("the Average accuracy is : " + str(np.mean(accuracies)))
# print("the Maximum accuracy is : " + str(np.max(accuracies)))
# print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
