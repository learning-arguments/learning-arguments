import pandas as pd

def encode(X):
    cols = X.columns
    numeric_cols = X._get_numeric_data().columns
    categorical_cols = list(set(cols) - set(numeric_cols))
    result = pd.get_dummies(X,
                            columns=categorical_cols,
                            drop_first=False)
    return result