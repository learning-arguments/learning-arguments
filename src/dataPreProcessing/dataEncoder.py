import numpy as np
from scipy.spatial.distance import cdist


# converts a new (testing) set (variable X) to the same domain as the dataframe after discretization
# variable myColumns describes the columns to be discretized in the (testing) set
def fitToDomain(X, df, myColumns):
    result = X.copy()

    # for each of the columns to be discretized
    for col in myColumns:

        # get the ranges of the dataframe in that column
        myRanges = df[col].unique()
        ranges = np.ndarray(shape=(len(myRanges), 2))
        # convert this into a 2D array where each row represents a bin
        # each row has the two ends of the bins as entry
        for i in range(len(myRanges)):
            thisRange = myRanges[i].split("-")
            ranges[i] = thisRange

        # we will now replace each value in the column by a range
        myCol = [""] * len(X)

        for i in range(len(X)):
            # first, retrieve each value
            myValue = X[col].values[i]

            # retrieve the closest range
            closestRange = getClosestRange(myValue, ranges)

            # replace the value
            myCol[i] = closestRange

        result[col] = myCol

    return result


# returns the range that is closest to myValue in form of a string
def getClosestRange(myValue, ranges):
    # get the distances to each of the ends of the bins in the ranges
    distances = cdist([[myValue]], ranges.reshape(-1, 1)).reshape(2, len(ranges))

    # get the index of the smallest distance in the array
    # (this index is two-dimensional, because there are two ends of bins.
    # in the array, each range is represented in a row, where the two columns describe the ends of the bin.)
    index_closest = np.where(distances == np.amin(distances))
    # (we are only interested in the index of the respective bin, and not which end is the closest one)
    index_closest = index_closest[0][0]

    # convert this to a string in the same format as the original
    myRange = str(ranges[index_closest][0]) + '-' + str(ranges[index_closest][1])
    return myRange

# adds empty columns to match the discretized dataframe
def addMyCols(df, myCols):
    result = df.copy()
    dfCols = result.columns

    for column in myCols:
        if column not in dfCols:
            result[column] = 0

    return result