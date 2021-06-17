import pandas as pd

#
# LOADING THE DATA & PREPROCESSING
#

myDataPath = "..\data\weatherAUS.csv"
df = pd.read_csv(myDataPath)

# drop na values
df.dropna(inplace=True)

# For the sake of testing, we will only use a portion of the dataframe.
# This will make execution faster.
df = df.head(500)

# reformat some columns
df['year'] = pd.DatetimeIndex(df['Date']).year
df['month'] = pd.DatetimeIndex(df['Date']).month
df['day'] = pd.DatetimeIndex(df['Date']).day
df = df.drop(columns=["Date"])

# split into train and test
train_size = int(len(df) * 0.8)
train = df[:train_size]
test = df[train_size:]

#
# DISCRETIZING THE DATA
#

import dataPreProcessor
import time

preProcessor = dataPreProcessor.dataPreProcessor()
start_time = time.time()
discretized_train = preProcessor.discretizeTrain(train, algorithm="EDBinning", oneHotEncoding=False)
end_time = time.time()
print("Time used to converge:", (end_time - start_time)/60, "minutes.")
discretized_test = preProcessor.discretizeTest(test, oneHotEncoding=False)

# print the rows to show off the discretization:
rows_shown = 20
pd.set_option('display.max_columns', 7)
print("Original training data:")
print(train.head(rows_shown))
print("Discretized training data:")
print(discretized_train.head(rows_shown))

print("Original testing data:")
print(test.head(rows_shown))
print("Discretized training data:")
print(discretized_test.head(rows_shown))
