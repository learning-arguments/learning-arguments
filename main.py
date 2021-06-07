from load_data import load_csv_data, bin_data_set, generate_case_model, to_fact
from learning import Theory
from helpers import histogram
from logic import Fact, Argument
from sklearn.model_selection import train_test_split
from typing import *


if __name__ == "__main__":
    boston_housing_data_raw = load_csv_data("BostonHousing.csv")
    binned_data = bin_data_set(boston_housing_data_raw, n_bins=2)
    # We restrict the number of columns because learning is not feasible for too many columns.
    columns = list(binned_data.columns[8:14])
    df = binned_data[columns]
    train, test = train_test_split(df, test_size=0.2)
    case_model = generate_case_model(train, is_binary=True)
    # print("histogram of the probabilities of cases", histogram([case.probability for case in case_model.cases]))
    
    theory = Theory.learn_with_pruned_search(case_model, log=True)
    # print(theory)

    # Evaluation
    print("Number of arguments:", theory.size)
    for col in range(len(columns)):
        l: List[bool] = []
        for i in test.index:
            values = list(test.loc[i])
            # Try to predict each column where the values of all other columns are known.
            X, y = values[:col] + values[col + 1 :], values[col]
            prediction = theory.predict(
                [to_fact(s, is_binary=True) for s in X],
                "high_" + columns[col].replace("_facts", "")
            )
            if isinstance(prediction, tuple):
                y = to_fact(y, is_binary=True)
                y_, argument = prediction
                l.append(y_ == y)
        print(col, "accuracy", len([a for a in l if a]) / len(l))
