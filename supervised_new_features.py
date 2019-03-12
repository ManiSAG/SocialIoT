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


# classifier = KNeighborsClassifier()
models = []
models.append(('Kmeans',KMeans(init='k-means++', max_iter=300, n_init=10, random_state=0)))
models.append(('LR', LogisticRegression(solver='lbfgs')))
models.append(('KNN', KNeighborsClassifier()))
models.append(('CART', DecisionTreeClassifier()))
models.append(('NB', GaussianNB()))
models.append(('SVM', SVC()))

for name, classifier in models:
    accuracies = []
    print("\nFor Classifier : " + name )
    for i in range(1,11):
        train_X , test_X , train_y, test_y = train_test_split(known_df[feature_names],known_df['label'],
                                                              train_size=0.8,
                                                              test_size=0.2,
                                                              random_state=i,
                                                              stratify=known_df['label'])
        train_y = train_y.astype('int')


        classifier.fit(train_X, train_y)
        pred_y = classifier.predict(test_X)

        # print("Fraction Correct [Accuracy]:")
        accuracy = np.sum(pred_y == test_y) / float(len(test_y))
        # print(accuracy)
        # print("#################")
        accuracies.append(accuracy)
    print("the Average accuracy is : " + str(np.mean(accuracies)))
    print("the Maximum accuracy is : " + str(np.max(accuracies)))
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
