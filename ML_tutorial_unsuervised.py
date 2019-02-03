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

def calculate_percent(my_list):
    temp_list = []
    for item in my_list:
        try:
            temp_list.append(int(item / sum(my_list) * 100))
        except ZeroDivisionError as e:
            return my_list
    return temp_list


# Load dataset
url = "trained_set.csv"
names = ['PD', 'service', 'sysadmin', 'ip']
feature_names = ['PD', 'service', 'sysadmin']
feature_dict = {'PD': 0, 'service': 1, 'sysadmin': 2, 'unknown': 3}

dataset = pd.read_csv(url, names=names)
# Split-out validation dataset
array = dataset.values
# df = pd.DataFrame(dataset,columns=feature_names)

known_df = pd.DataFrame(columns=names + ['label'])
unknown_df = pd.DataFrame(columns=names)
for index, row in dataset.iterrows():
    key_type = get_type(row['ip'])
    if key_type is not None:
        row['label'] = feature_dict[key_type]
        known_df = known_df.append(row)
    else:
        unknown_df = unknown_df.append(row)

    # print(row['PD'], row['service',row['sysadmin'],row['ip']])

# classifier = KMeans(init='k-means++', max_iter=300, n_init=10, random_state=0)
# classifier = KNeighborsClassifier()
models = []
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
    print("the average accuracy is : " + str(np.mean(accuracies)))
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
