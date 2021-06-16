# Wrapper for the discretization algorithms.
from dataPreProcessing.discretizations import kMeansClustering, DBSCANClustering, ewBinning, edBinning

def discretize(myData, algorithm):
    if algorithm == "kMeans":
        kMeans = kMeansClustering.kMeansClustering()
        return kMeans.transform(myData)

    if algorithm == "DBSCAN":
        dbSCAN = DBSCANClustering.DBSCANClustering()
        return dbSCAN.transform(myData)

    if algorithm == "EWBinning":
        ewBin = ewBinning.ewBinning()
        return ewBin.transform(myData)

    if algorithm == "EDBinning":
        edBin = edBinning.edBinning()
        return edBin.transform(myData)

    raise Exception("No valid discretization algorithm has been selected.")