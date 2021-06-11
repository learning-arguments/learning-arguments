import kMeansClustering
import DBSCANClustering


# Wrapper for the discretization algorithms.

def discretize(myData, algorithm):
    if algorithm == "kMeans":
        kMeans = kMeansClustering.kMeansClustering()
        return kMeans.transform(myData)

    if algorithm == "DBSCAN":
        dbSCAN = DBSCANClustering.DBSCANClustering()
        return dbSCAN.transform(myData)
