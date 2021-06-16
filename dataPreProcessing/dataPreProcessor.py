from dataPreProcessing.discretizations import discretizations
import dataEncoder
import oneHotEncoder


# This is the wrapper class for all of the files in this folder.
# It allows for data discretization of the training dataframe, and also uses oneHotEncoding if specified so.
# When new data is predicted, this class transforms the new data to the same format as the discretized training set.
# Again, oneHotEncoding can be used here if desired so.

class dataPreProcessor:
    discretizedTrain = None
    myCols = None

    # this method is used to discretize the training set before learning
    # the variable "algorithm" decides which algorithm is used for discretization
    def discretizeTrain(self, train, algorithm, oneHotEncoding=False):
        # save the numeric columns that will be discretized
        self.myCols = train._get_numeric_data().columns

        # discretize the dataframe and save it
        self.discretizedTrain = discretizations.discretize(train, algorithm)

        # use ohe if specified so
        if oneHotEncoding:
            return oneHotEncoder.encode(self.discretizeTrain)
        return self.discretizedTrain

    def discretizeTest(self, test, oneHotEncoding=False):
        result = dataEncoder.fitToDomain(test, self.discretizedTrain, self.myCols)

        # use ohe if specified so
        if oneHotEncoding:
            return oneHotEncoder.encode(result)
        return result
