from sklearn.cluster import KMeans
import pandas as pd
import matplotlib.pyplot as plt

# Load dataset
url = "trained_set.csv"
names = [ 'ip','PD', 'service', 'sysadmin']
dataset = pd.read_csv(url,names=names)

# Split-out validation dataset
array = dataset.values
x = array[:,0:3]
y = array[:,3:4]

# wcss = []
#
# iterations = 20
# for i in range(1, iterations):
#     kmeans = KMeans(n_clusters=i, init='k-means++', max_iter=300, n_init=10, random_state=0)
#     kmeans.fit(X)
#     wcss.append(kmeans.inertia_)
#
# intervals = [ s - t for s, t in zip(wcss, wcss[1:])]
# print(wcss)
# # Plotting the results onto a line graph, allowing us to observe 'The elbow'
# # plt.plot(range(0, len(intervals)), intervals)
# plt.plot(range(1, iterations), wcss)
# # plt.bar(range(0, len(intervals)), intervals)
# plt.title('The elbow method')
# plt.xlabel('Number of clusters')
# # plt.xlabel('different between two consecutive WCSS')
# plt.ylabel('WCSS')  # within cluster sum of squares
# # plt.ylabel('intervals')  # within cluster sum of squares
# plt.show()

#Applying kmeans to the dataset / Creating the kmeans classifier
kmeans = KMeans(n_clusters = 4, init = 'k-means++', max_iter = 300, n_init = 10, random_state = 0)
y_kmeans = kmeans.fit_predict(x)
#Visualising the clusters
plt.scatter(x[y_kmeans == 0, 0], x[y_kmeans == 0, 1], s = 100, c = 'red', label = 'Iris-setosa')
plt.scatter(x[y_kmeans == 1, 0], x[y_kmeans == 1, 1], s = 100, c = 'blue', label = 'Iris-versicolour')
plt.scatter(x[y_kmeans == 2, 0], x[y_kmeans == 2, 1], s = 100, c = 'green', label = 'Iris-virginica')

#Plotting the centroids of the clusters
plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:,1], s = 100, c = 'yellow', label = 'Centroids')

plt.legend()