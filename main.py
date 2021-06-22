import pandas as pd
import datetime as dt
import os
from load_data import load_csv_data, bin_data_set, bin_labels
import dataPreProcessing.discretizations.discretizations
from sklearn.model_selection import train_test_split
from evaluation import evaluate_decision_trees, evaluate_rule_mining, evaluate_hero_algorithm
from itertools import product
from dataPreProcessing import dataPreProcessor

import warnings

warnings.filterwarnings("ignore")

if __name__ == "__main__":

    evaluation_results = pd.DataFrame()
    for param in list(product(["BostonHousing.csv", 'IRIS.csv'], ['EDBinning', 'DBSCAN', 'kMeans', 'EWBinning'])):
        hyper_parameters = {'dataset': param[0], 'binning_method': param[1]}
        try:
            print('start: %s' % hyper_parameters)
            myDataPath = os.path.join('data', hyper_parameters.get('dataset'))
            df = pd.read_csv(myDataPath)
            df.dropna(inplace=True)
            train_test_split(df, test_size=0.2, random_state=1)
            train, test = train_test_split(df, test_size=0.2, random_state=1)

            preProcessor = dataPreProcessor.dataPreProcessor()
            discretized_train = preProcessor.discretizeTrain(train, algorithm=hyper_parameters.get('binning_method'),
                                                             oneHotEncoding=True)
            discretized_test = preProcessor.discretizeTest(test, oneHotEncoding=True)

            columns = list(discretized_train.columns[10:14])
            target_col = list(filter(lambda x: x.split('_')[0] == 'medv', discretized_train.columns))

            # Train Set Decision Trees
            model_eval_dt_train, decision_tree = evaluate_decision_trees(discretized_train, target_col, columns,
                                                                         hyper_parameters)
            model_eval_dt_test, _ = evaluate_decision_trees(discretized_train, target_col, columns, hyper_parameters,
                                                            decision_tree)
            model_eval_dt_test['training_runtime'] = model_eval_dt_train.get('training_runtime')
            evaluation_results = evaluation_results.append(model_eval_dt_train, ignore_index=True)
            evaluation_results = evaluation_results.append(model_eval_dt_test, ignore_index=True)
            print(model_eval_dt_train, '\n', model_eval_dt_test)
        except Exception as e:
            print("Exception %s %s" % (hyper_parameters, e))
            continue

    for param in list(
            product(["BostonHousing.csv"], [2, 3, 4, 5], ['equal_depth', 'equal_width'], [5, 10, 20], [2, 4, 6])):
        hyper_parameters = {'dataset': param[0], 'no_bins': param[1], 'binning_method': param[2],
                            'search_depth': param[3], 'max_premises': param[4]}
        try:
            print('start: %s' % hyper_parameters)

            boston_housing_data_raw = load_csv_data(hyper_parameters.get('dataset'))
            binned_data = bin_data_set(boston_housing_data_raw, n_bins=hyper_parameters.get('no_bins'),
                                       method=hyper_parameters.get('binning_method'))

            columns = list(binned_data.columns[10:14])
            categories = dict([(column, bin_labels(hyper_parameters.get('no_bins'))) for column in columns])
            df = binned_data[columns]
            train, test = train_test_split(df, test_size=0.2, random_state=1)
            target_col = 'medv'

            # Train Set Rule Mining
            model_eval_rm_train, theory = evaluate_rule_mining(train, categories, target_col,
                                                               search_depth=hyper_parameters.get('search_depth'),
                                                               max_premise_size=hyper_parameters.get('max_premises'))
            model_eval_rm_train.update(hyper_parameters)

            # Test Set Rule Mining
            model_eval_rm_test, _ = evaluate_rule_mining(test, categories, target_col,
                                                         search_depth=hyper_parameters.get('search_depth'),
                                                         max_premise_size=hyper_parameters.get('max_premises'),
                                                         theory=theory)
            model_eval_rm_test.update(hyper_parameters)
            model_eval_rm_test['training_runtime'] = model_eval_rm_train.get('training_runtime')

            evaluation_results = evaluation_results.append(model_eval_rm_train, ignore_index=True)
            evaluation_results = evaluation_results.append(model_eval_rm_test, ignore_index=True)
            print(model_eval_rm_train, '\n', model_eval_rm_test)
        except Exception as e:
            print("Exception %s %s" % (hyper_parameters, e))
            continue

    undiscretized_data = True

    if undiscretized_data:
        try:
            target_col = 'medv'
            boston_housing_data_raw = load_csv_data("BostonHousing.csv")

            # choose one of the algorithms here to discretize the target values
            myAlgorithm = 'kMeans'
            # discretizing only works on dataframes so we need to cast it
            myData = pd.DataFrame(boston_housing_data_raw[target_col])
            # discretize the target column:
            boston_housing_data_raw[target_col] = \
                dataPreProcessing.discretizations.discretizations.discretize(myData, myAlgorithm)

            columns = list(boston_housing_data_raw.columns[10:14])
            train, test = train_test_split(boston_housing_data_raw[columns], test_size=0.2, random_state=1)
            model_eval_dt_train, decision_tree = evaluate_decision_trees(train, target_col)

            # Train Set Decision Trees
            model_eval_dt_train, decision_tree = evaluate_decision_trees(train, target_col)
            model_eval_dt_train.update(hyper_parameters)
            model_eval_dt_train['data_type'] = 'train'
            evaluation_results = evaluation_results.append(model_eval_dt_train, ignore_index=True)

            # Test Set Decision Trees
            model_eval_dt_test, _ = evaluate_decision_trees(test, target_col, decision_tree)
            model_eval_dt_test.update(hyper_parameters)
            model_eval_dt_test['training_runtime'] = model_eval_dt_train.get('training_runtime')
            model_eval_dt_test['data_type'] = 'test'
            evaluation_results = evaluation_results.append(model_eval_dt_test, ignore_index=True)
        except Exception as e:
            print('Exception Undiscretized Decision Tree %s' % e)

        # evaluate_hero_algorithm(train, categories, target_col)
    evaluation_results.to_csv('evaluation_result_%s.csv' % dt.datetime.now().strftime("%Y_%m_%d_%H_%M"), index=False)
