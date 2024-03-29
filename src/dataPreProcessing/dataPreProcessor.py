from dataPreProcessing.discretizations import discretizations
from dataPreProcessing.dataEncoder import fitToDomain, addMyCols
from dataPreProcessing.oneHotEncoder import encode
# This is the wrapper class for all of the files in this folder.
# It allows for data discretization of the training dataframe, and also uses oneHotEncoding if specified so.
# When new data is predicted, this class transforms the new data to the same format as the discretized training set.
# Again, oneHotEncoding can be used here if desired so.

class dataPreProcessor:
    _discretizedTrain = None
    _myCols = None

    # this method is used to discretize the training set before learning
    # the variable "algorithm" decides which algorithm is used for discretization
    def discretizeTrain(self, train, algorithm, oneHotEncoding=False, no_bins=None):
        # save the numeric columns that will be discretized
        self._myCols = train._get_numeric_data().columns

        # discretize the dataframe and save it
        self._discretizedTrain = discretizations.discretize(train, algorithm, no_bins=no_bins)

        # use ohe if specified so
        if oneHotEncoding:
            df = encode(self._discretizedTrain)
            self._oheColumns = df.columns
            return df
        return self._discretizedTrain

    def discretizeTest(self, test, oneHotEncoding=False):
        result = fitToDomain(test, self._discretizedTrain, self._myCols)

        # use ohe if specified so
        if oneHotEncoding:
            df = encode(result)
            df = addMyCols(df, self._oheColumns)
            return df
        return result
