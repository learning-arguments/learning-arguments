import os
import pandas as pd
import numpy as np
from logic import Case, Fact, CaseModel

cwd = os.getcwd()


def load_csv_data(data_set_name: str) -> pd.DataFrame:
    return pd.read_csv(os.path.join(cwd, *["data", data_set_name]))


def bin_data_set(data_set: pd.DataFrame, bin_labels: list) -> pd.DataFrame:
    binned_data = pd.DataFrame()
    for col in data_set.columns:
        bin_edges = np.linspace(
            np.min(data_set[col]) - 1e-5,
            np.max(data_set[col]) + 1e-5,
            len(bin_labels) + 1,
        )
        column_labels = [label + "_" + col for label in bin_labels]
        binned_data[col + "_facts"] = pd.cut(
            data_set[col], bins=bin_edges, labels=column_labels
        )
    return binned_data


def generate_case_model(binned_data: pd.DataFrame) -> CaseModel:
    list_cases = list()
    for i in binned_data.index:
        case_name = "sample no %s" % i
        fact_set = [Fact(fact) for fact in list(binned_data.iloc[i])]
        list_cases.append(Case(facts=fact_set, probability=1 / len(binned_data)))
    case_model = CaseModel(cases=list_cases)
    return case_model
