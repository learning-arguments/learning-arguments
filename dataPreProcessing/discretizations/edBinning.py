from scipy.spatial.distance import cdist
from sklearn.metrics import silhouette_score
import numpy as np
import warnings


# discretizes a column of the dataframe
# to use other methods of discretiation, this method should be overwritten
def transformCol(myData):
    bestScore = -float('inf')
    bestK = 0.0

    # find the best number of clusters
    for k in range(2, 11):
        edBin = binning(n_clusters=k)
        y = edBin.fit_predict(myData)

        if len(np.unique(y)) != 1:
            score = silhouette_score(myData, y)

            if score > bestScore:
                bestScore = score
                bestK = k

    # parameter tuning is finished, make clusters using the best parameters
    edBin = binning(n_clusters=bestK)
    predictions = edBin.fit_predict(myData)
    clusters = list()

    for i in range(0, bestK):
        # for the current cluster
        myClusterIndex = i
        # find the indices of the datapoints that belong to this cluster
        myClusterIndices = np.where(predictions == myClusterIndex)

        if(len(myClusterIndices[0]) > 0):
            # these are the values of the current cluster we are looking at
            myCluster = myData[myClusterIndices]
            # get the min and max values of these
            myMin = myCluster.min()
            myMax = myCluster.max()
            # here, clusters are described as a range of the maximum and minimum value of the cluster.
            # This makes prediction easier compared to simply using the centroids of the algorithm
            myRange = str(myMin) + '-' + str(myMax)
            clusters.append(myRange)

    result = [""] * len(myData)

    for i in range(len(result)):
        thisResult = str(clusters[predictions[i]])
        result[i] = thisResult

    return result

class edBinning:
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


class binning:

    def __init__(self, n_clusters):
        self.myK = n_clusters

    def fit_predict(self, myData):
        result = list()

        tempData = list()
        for i in range(len(myData)):
            tempData.append(myData[i][0])

        sortedData = np.sort(tempData)
        binSize = int(len(tempData)/self.myK)
        myBins = np.ndarray([self.myK, 2])

        for i in range(self.myK - 1):
            myBins[i][0] = sortedData[i * binSize]
            myBins[i][1] = sortedData[(i + 1) * binSize - 1]

        # it is possible that there is a remainder when calculating len(tempData)/self.myK
        # therefore, the last bin may be larger than our given binSize
        # to solve this, we will simply use the last entry in our data for the high end of the last bin
        myBins[self.myK - 1][0] = sortedData[(self.myK - 1) * binSize]
        myBins[self.myK - 1][1] = sortedData[len(sortedData) - 1]

        for value in myData:
            index = self.getClosestRange(value, myBins)
            result.append(index)

        return np.array(result)

    # instead of choosing the correct bin,
    # we get the bin which has one of its end points closest to our given data point
    # while this can result in wrong bins in case two bins have the same same point as end point
    # and this point is the closest to our data point,
    # choosing the correct bin was not always possible for the largest/smallest value in the dataset
    # due to floating point errors
    def getClosestRange(self, myValue, ranges):
        # get the distances to each of the ends of the bins in the ranges
        distances = cdist([myValue], ranges.reshape(-1, 1)).reshape(2, len(ranges))

        # get the index of the smallest distance in the array
        # (this index is two-dimensional, because there are two ends of bins.
        # in the array, each range is represented in a row, where the two columns describe the ends of the bin.)
        index_closest = np.where(distances == np.amin(distances))
        # (we are only interested in the index of the respective bin, and not which end is the closest one)
        index_closest = index_closest[0][0]

        return index_closest
