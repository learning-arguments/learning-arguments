from load_data import load_csv_data, bin_data_set
from sklearn.model_selection import train_test_split
from hero import defeasible_theory_search
from learning import Theory
from logic import CaseModel


def test_example_1():
    x = [["a", "b", "c"], ["a", "b", "not c"], ["a", "not b", "not c"]]
    y = ["d", "not d", "d"]
    theory = defeasible_theory_search(x, y)
    rules = [rule for rule, _ in theory]
    assert len(rules) == 2
    assert ([], "d") in rules
    assert (["b", "not c"], "not d") in rules


def test_case_model_1():
    case_model = CaseModel.fromStr([(1, "sus, ¬mis, wit"), (0, "mis, wit")])
    theory = Theory.learn_with_hero(case_model)
    assert len(theory.presumptively_valid_arguments) > 0


def test_case_model_2():
    case_model = CaseModel.fromStr([(1, "inn, ¬gui"), (0, "¬inn, gui, evi")])
    theory = Theory.learn_with_hero(case_model)
    assert len(theory.presumptively_valid_arguments) > 0


def test_case_model_3():
    case_model = CaseModel.fromStr(
        [(1, "pun, gui, evi"), (0, "¬pun, gui, evi, jus"), (0, "¬gui, evi, ali")]
    )
    theory = Theory.learn_with_hero(case_model)
    assert len(theory.presumptively_valid_arguments) > 0


def test_data_set():
    df = load_csv_data("BostonHousing.csv")
    n_bins = 3
    binned_data = bin_data_set(df, n_bins=n_bins)
    columns = list(binned_data.columns[11:14])
    df = binned_data[columns]
    train, test = train_test_split(df, test_size=0.95, random_state=1)
    train, test = train.values.tolist(), test.values.tolist()
    x, y = [a[:-1] for a in train], [a[-1] for a in train]
    theory = defeasible_theory_search(x, y)
    for rule, _ in theory:
        print(rule)
    assert len(theory) > 0
