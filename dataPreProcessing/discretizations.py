import kMeansClustering

# Wrapper for the discretization algorithms.

def discretize(myData, algorithm):

    if algorithm == "kMeans":
        kMeans = kMeansClustering.kMeansClustering()
        return kMeans.transform(myData)