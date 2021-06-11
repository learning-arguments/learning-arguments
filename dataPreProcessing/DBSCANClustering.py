from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import warnings

from skopt import BayesSearchCV

# discretizes a column of the dataframe
def transformCol(myData):
    minEps = 0.1
    maxEps = 1.0

    minMinSamples = 1
    maxMinSamples = len(myData)/2

    bestScore = 0.0
    bestEps = 0.0
    bestMinSamples = 0

    epss = np.linspace(minEps, maxEps, 51)
    min_samples = np.linspace(minMinSamples, maxMinSamples, 100)

    for i in range(len(epss)):
        for j in range(len(min_samples)):
            dbSCAN = DBSCAN(eps = epss[i], min_samples = min_samples[j])
            myDataNormalized = MinMaxScaler().fit_transform(myData)
            y = dbSCAN.fit_predict(myDataNormalized)

            if len(np.unique(y)) != 1:
                score = silhouette_score(myData, dbSCAN.labels_)

                if score > bestScore:
                    bestScore = score
                    bestEps = epss[i]
                    bestMinSamples = min_samples[j]

    # best number of cluster has been found, now find the ranges that the cluster spans
    dbSCAN = DBSCAN(bestEps, bestMinSamples)
    myDataNormalized = MinMaxScaler().fit_transform(myData)
    predictions = dbSCAN.fit_predict(myDataNormalized)

    clusterIndices = np.unique(predictions)

    # For each outlier, we create a new cluster to assign it to
    if np.isin(-1, clusterIndices):

        myCluster = clusterIndices.max() + 1
        for i in range(len(predictions)):
            if predictions[i] == -1:
                predictions[i] = myCluster
                myCluster += 1

    numClusters = len(np.unique(predictions))
    clusters = [0] * numClusters

    for i in range(0, numClusters):
        # for the current cluster, find the indices of the datapoints that belong to this cluster
        myClusterIndices = np.where(predictions == i)
        # these are the values of the current cluster we are looking at
        myCluster = myData[myClusterIndices]
        # get the min and max values of these
        myMin = myCluster.min()
        myMax = myCluster.max()
        # here, clusters are described as a range of the maximum and minimum value of the cluster.
        # This makes prediction easier compared to simply using the centroids of the algorithm
        clusters[i] = str(myMin) + '-' + str(myMax)

    result = [""] * len(myData)

    for i in range(len(result)):
        thisResult = str(clusters[predictions[i]])
        result[i] = thisResult

    return result


class DBSCANClustering:
    def __init__(self):
        pass

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        result = X.copy()

        # get the columns to transform
        myCols = result._get_numeric_data().columns

        # for each of these columns
        for i in range(0, len(myCols)):
            thisCol = myCols[i]
            result[thisCol].astype('str')

            myData = result[[thisCol]].copy().to_numpy()

            # replace the value of the column
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                result[thisCol] = transformCol(myData)
        return result
