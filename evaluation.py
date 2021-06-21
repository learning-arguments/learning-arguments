import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score
from decisionTree.decisionTreeClassifier import decisionTreeClassifier
from dataPreProcessing.oneHotEncoder import encode
from hero import defeasible_theory_search, predict
from load_data import generate_case_model
from learning import Theory
from logic import Fact
import time

import warnings

warnings.filterwarnings("ignore")


def compute_performance_metrics(y, y_hat):
    return {'Acc': accuracy_score(y, y_hat), 'F1': f1_score(y, y_hat, average='weighted')}


def evaluate_decision_trees(data_set: pd.DataFrame, target_column: list, data_columns: list, hyper_parameters: dict,
                            decision_tree: decisionTreeClassifier = None):
    X, y = data_set[data_columns], data_set[target_column]

    if decision_tree is None:
        t1 = time.time()
        decision_tree = decisionTreeClassifier()
        decision_tree.trainDecTree(X, y)
        t2 = time.time()
        model_eval = {'training_runtime': (t2 - t1), 'model_type': 'decision tree', 'data_type': 'train'}
    else:
        model_eval = {'training_runtime': 0, 'model_type': 'decision tree', 'data_type': 'test'}

    y_hat = decision_tree.predict(X)

    performance_metrics = compute_performance_metrics(y, y_hat)
    model_eval.update(performance_metrics)
    model_eval.update(hyper_parameters)

    return model_eval, decision_tree


def evaluate_rule_mining(data_set, categories, unknown_fact, search_depth=100, max_premise_size=10,
                         theory: Theory = None):
    if theory is None:
        t1 = time.time()
        case_model = generate_case_model(data_set, categories)
        theory = Theory.learn_with_pruned_search(case_model, depth=search_depth,
                                                 max_premise_size=max_premise_size, log=False)
        t2 = time.time()
        model_eval = {'training_runtime': (t2 - t1), 'model_type': 'rule mining', 'data_type': 'train'}
    else:
        model_eval = {'training_runtime': 0, 'model_type': 'rule mining', 'data_type': 'test'}

    y_hat, y_ = [], []
    for i in data_set.index:
        # Try to predict each column where the values of all other columns are known.
        X, y = data_set.loc[i, data_set.columns != unknown_fact], data_set[unknown_fact].loc[i]
        known_facts = [Fact.fromStr(s, categories[s.split("_", 1)[1]]) for s in X]

        prediction = theory.predict(
            known_facts,
            unknown_fact,
        )
        if isinstance(prediction, tuple):
            y_i = Fact.fromStr(y, categories[y.split("_", 1)[1]])
            y_hat_i, argument = prediction
            y_hat.append(str(y_hat_i))
            y_.append(str(y_i))

    with open("output/BostonHousing.verheij", "w", encoding='utf-8') as file:
        file.write(str(theory))

    naive_acc = sum([y_[i] == y_hat[i] for i in range(len(y_))]) / len(y_)

    y_encoded = encode(pd.DataFrame(y_)).values.tolist()
    y_hat_encoded = encode(pd.DataFrame(y_hat)).values.tolist()

    performance_metrics = compute_performance_metrics(y_encoded, y_hat_encoded)
    model_eval.update(performance_metrics)

    print("Rule Mining Accuracy: %.02f Exec Time: %.02f" % (model_eval.get('Acc'), model_eval.get('training_runtime')))
    return model_eval, theory


def evaluate_hero_algorithm(data_set, categories, unknown_fact):
    train = data_set.values.tolist()
    x, y = [a[:-1] for a in train], [a[-1] for a in train]
    t1 = time.time()
    theory = defeasible_theory_search(x, y)
    t2 = time.time()
    model_eval = {'training_runtime': (t2 - t1)}

    print('thoery done')

    y_hat, y_ = [], []
    for i in data_set.index:
        # Try to predict each column where the values of all other columns are known.
        X, y = data_set.loc[i, data_set.columns != unknown_fact], data_set[unknown_fact].loc[i]
        known_facts = [Fact.fromStr(s, categories[s.split("_", 1)[1]]) for s in X]
        y_hat_i, argument = predict(known_facts, theory)
        y_hat.append(y_hat_i)
        y_.append(y)

    performance_metrics = compute_performance_metrics(encode(y), np.array(y_hat))
    model_eval.update(performance_metrics)

    print("Hero Accuracy: %.02f Exec Time: %.02f" % (model_eval.get('Acc'), model_eval.get('training_runtime')))
    return model_eval, theory
