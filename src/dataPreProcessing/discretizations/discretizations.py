# Wrapper for the discretization algorithms.
from dataPreProcessing.discretizations import kMeansClustering, DBSCANClustering, ewBinning, edBinning


def discretize(myData, algorithm, no_bins=None):
    if algorithm == "kMeans":
        kMeans = kMeansClustering.kMeansClustering(no_bins)
        return kMeans.transform(myData)

    if algorithm == "DBSCAN":
        dbSCAN = DBSCANClustering.DBSCANClustering()
        return dbSCAN.transform(myData)

    if algorithm == "EWBinning":
        ewBin = ewBinning.ewBinning(no_bins)
        return ewBin.transform(myData)

    if algorithm == "EDBinning":
        edBin = edBinning.edBinning(no_bins)
        return edBin.transform(myData)

    raise Exception("No valid discretization algorithm has been selected.")
