import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN, KMeans
import seaborn as sns

from shapely.geometry import Point
import geopandas as gpd
from geopandas import GeoDataFrame
import geodatasets

df = pd.read_csv("overlapping_ships.csv")

ships = np.hstack((df.iloc[:,0].to_numpy(), df.iloc[:, 3].to_numpy()))
print(len(np.unique(ships)))

latitude = np.hstack((df.iloc[:,1].to_numpy(), df.iloc[:, 4].to_numpy()))
longitude = np.hstack((df.iloc[:, 2].to_numpy(), df.iloc[:, 5].to_numpy()))
coordinates = np.column_stack((latitude, longitude))

# print(coordinates)
# print(coordinates.shape)


sse = {}
for k in range(1, 20):
    kmeans = KMeans(n_clusters=k, max_iter=1000).fit(coordinates)
    sse[k] = kmeans.inertia_

plt.figure()
plt.plot(list(sse.keys()), list(sse.values()))
plt.xlabel("Number of cluster")
plt.ylabel("SSE")
plt.show()



num_clusters = 7
kmeans = KMeans(n_clusters=num_clusters, random_state=100)
labels = kmeans.fit_predict(coordinates)

plt.scatter(coordinates[:,1], coordinates[:,0], c=labels, cmap='viridis', marker='o')
plt.scatter(kmeans.cluster_centers_[:,1], kmeans.cluster_centers_[:,0], c='red', marker='x', s=100, label="Centroids")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("K-means Clustering of Coordinates (K=7)")
plt.legend()
plt.show()

print(kmeans.cluster_centers_)
centroids = kmeans.cluster_centers_
clust_lat = []
clust_lon = []
for i in range(centroids.shape[0]):
    clust_lat.append(centroids[i][0])
    clust_lon.append(centroids[i][1])



geometry = [Point(xy) for xy in zip(clust_lon, clust_lat)]
gdf = GeoDataFrame(np.column_stack((clust_lat, clust_lon)), geometry=geometry)   
world = gpd.read_file(geodatasets.data.naturalearth.land['url'])
gdf.plot(ax=world.plot(figsize=(10, 6)), marker='x', color='red', markersize=15)
plt.show()