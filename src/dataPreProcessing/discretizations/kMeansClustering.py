from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import numpy as np
import warnings

# discretizes a column of the dataframe
def transformCol(myData, no_bins):
    bestScore = -float('inf')
    bestK = 0.0
    if no_bins is None:
        # find the best number of clusters
        for k in range(2, 11):
            kMeans = KMeans(n_clusters=k, random_state=42)
            y = kMeans.fit_predict(myData)

            # silhouette score only works when more than one cluster is found by the algorithm
            # even if numbers of clusters k > 1,
            # the algorithm can return one cluster if centroids converge closely
            if len(np.unique(y)) != 1:
                score = silhouette_score(myData, kMeans.labels_)

                if score > bestScore:
                    bestScore = score
                    bestK = k
    else:
        bestK = no_bins

    # parameter tuning is finished, make clusters using the best parameters
    kMeans = KMeans(n_clusters=bestK, random_state=42)
    predictions = kMeans.fit_predict(myData)
    clusters = [0] * bestK

    for i in range(0, bestK):
        # for the current cluster
        myClusterIndex = i
        # find the indices of the datapoints that belong to this cluster
        myClusterIndices = np.where(predictions == myClusterIndex)
        # these are the values of the current cluster we are looking at
        myCluster = myData[myClusterIndices]
        # get the min and max values of these
        myMin = float(myCluster.min())
        myMax = float(myCluster.max())
        # here, clusters are described as a range of the maximum and minimum value of the cluster.
        # This makes prediction easier compared to simply using the centroids of the algorithm
        clusters[i] = str(myMin) + '-' + str(myMax)

    result = [""] * len(myData)

    for i in range(len(result)):
        thisResult = str(clusters[predictions[i]])
        result[i] = thisResult

    return result


class kMeansClustering:
    def __init__(self, no_bins):
        self._no_bins = no_bins

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
                result[thisCol] = transformCol(myData, self._no_bins)
        return result
