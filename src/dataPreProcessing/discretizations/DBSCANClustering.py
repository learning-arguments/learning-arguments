import warnings

import matplotlib.pyplot
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import MinMaxScaler

from skopt.space import Real, Integer
from skopt.utils import use_named_args
from skopt import gp_minimize
from skopt.plots import plot_objective, plot_convergence

import matplotlib.pyplot as plt
import time
import sys


# discretizes a column of the dataframe
def transformCol(myData, n_calls=50):
    space = [Real(sys.float_info.min, 1.0, name='eps'),
             Integer(1, len(myData), name='min_samples')]

    # scaling the range of the data in order to make sure that eps is between 0 and 1
    scaler = MinMaxScaler()
    myDataNormalized = scaler.fit_transform(myData)

    @use_named_args(space)
    def objective(**params):
        dbSCAN = DBSCAN(**params, n_jobs=-1)
        y = dbSCAN.fit_predict(myDataNormalized)

        if len(np.unique(y)) != 1:
            score = silhouette_score(myData, dbSCAN.labels_)
            return -score
        else:
            # in case of one cluster, we will not be able to compute silhouette score nor
            # have any useful information for the column.
            # Therefore, assign score worse than worst silhouette score
            return 2

    start_time = time.time()
    gp = gp_minimize(objective, space, n_calls=n_calls, random_state=0, n_jobs=-1)
    end_time = time.time()
    #print("Time used for discretizing the data: %.2f minutes." % ((end_time - start_time) / 60))

    bestEps = gp.x[0]
    bestMinSamples = gp.x[1]

    # showMyPlots(gp)

    # parameter tuning is finished, make clusters using the best parameters
    dbSCAN = DBSCAN(bestEps, bestMinSamples, n_jobs=-1)
    predictions = dbSCAN.fit_predict(myDataNormalized)

    clusterIndices = np.unique(predictions)

    # additionally, for each outlier, we create a new cluster to assign it to
    if np.isin(-1, clusterIndices):

        myCluster = clusterIndices.max() + 1
        for i in range(len(predictions)):
            if predictions[i] == -1:
                predictions[i] = myCluster
                myCluster += 1

    numClusters = len(np.unique(predictions))
    clusters = [0] * numClusters

    # create ranges for each cluster and assign for each datapoint
    for i in range(0, numClusters):
        # for the current cluster, find the indices of the datapoints that belong to this cluster
        myClusterIndices = np.where(predictions == i)
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


def showMyPlots(gp):
    plt.tight_layout()
    plot_convergence(gp)
    plt.show()

    _ = plot_objective(gp)
    plt.show()


class DBSCANClustering:
    def __init__(self):
        pass

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
