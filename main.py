from load_data import load_csv_data, bin_data_set, generate_case_model, bin_labels
from learning import Theory
from helpers import histogram
from logic import Fact, Argument
from sklearn.model_selection import train_test_split
from typing import *


if __name__ == "__main__":
    boston_housing_data_raw = load_csv_data("BostonHousing.csv")
    n_bins = 3
    binned_data = bin_data_set(boston_housing_data_raw, n_bins=n_bins)
    # We restrict the number of columns because learning is not feasible for too many columns.
    columns = list(binned_data.columns[10:14])
    df = binned_data[columns]
    train, test = train_test_split(df, test_size=0.2)
    categories = dict([(column, bin_labels(n_bins)) for column in columns])
    case_model = generate_case_model(train, categories)

    # Training
    theory = Theory.learn_with_pruned_search(
        case_model, depth=4, max_premise_size=4, log=True
    )
    print(theory)
    with open('output/BostonHousing.verheij', 'w') as file:
        file.write(str(theory))

    # Evaluation
    print("Number of arguments:", theory.size)
    col = len(columns) - 1
    l: List[bool] = []
    for i in test.index:
        values = list(test.loc[i])
        # Try to predict each column where the values of all other columns are known.
        X, y = values[:col] + values[col + 1 :], values[col]
        prediction = theory.predict(
            [Fact.fromStr(s, categories[s.split("_", 1)[1]]) for s in X],
            columns[col],
        )
        if isinstance(prediction, tuple):
            y = Fact.fromStr(y, categories[y.split("_", 1)[1]])
            y_, argument = prediction
            l.append(y_ == y)
    print(col, "accuracy", len([a for a in l if a]) / len(l))
