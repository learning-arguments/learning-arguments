from load_data import load_csv_data, bin_data_set, bin_labels
import dataPreProcessing.discretizations.discretizations
from sklearn.model_selection import train_test_split
from evaluation import evaluate_decision_trees, evaluate_rule_mining, evaluate_hero_algorithm
from itertools import product
import pandas as pd
import datetime as dt

if __name__ == "__main__":

    evaluation_results = pd.DataFrame()
    for parameter in list(product(["BostonHousing.csv"], [3], ['equal_depth'])):

        boston_housing_data_raw = load_csv_data(parameter[0])
        n_bins = parameter[1]
        binned_data = bin_data_set(boston_housing_data_raw, n_bins=n_bins, method=parameter[2])
        parameter_dict = {'dataset': parameter[0], 'no_bins': parameter[1], 'binning_method': parameter[2]}
        print(parameter_dict)

        # Data
        columns = list(binned_data.columns[10:14])
        categories = dict([(column, bin_labels(n_bins)) for column in columns])
        df = binned_data[columns]
        train, test = train_test_split(df, test_size=0.2, random_state=1)
        target_col = 'medv'

        # Train Set Decision Trees
        model_eval_dt_train, decision_tree = evaluate_decision_trees(train, target_col)
        model_eval_dt_train.update(parameter_dict)
        model_eval_dt_train['data_type'] = 'train'
        evaluation_results = evaluation_results.append(model_eval_dt_train, ignore_index=True)

        # Test Set Decision Trees
        model_eval_dt_test, _ = evaluate_decision_trees(test, target_col, decision_tree)
        model_eval_dt_test.update(parameter_dict)
        model_eval_dt_test['training_runtime'] = model_eval_dt_train.get('training_runtime')
        model_eval_dt_test['data_type'] = 'test'
        evaluation_results = evaluation_results.append(model_eval_dt_test, ignore_index=True)

        for rule_mining_parameter in list(product([5, 50], [6])):
            rule_mining_parameter_dict = {'search_depth': rule_mining_parameter[0],
                                          'max_premises': rule_mining_parameter[1]}
            print(rule_mining_parameter_dict)

            # Train Set Rule Mining
            model_eval_rm_train, theory = evaluate_rule_mining(train, categories, target_col,
                                                               search_depth=rule_mining_parameter[0],
                                                               max_premise_size=rule_mining_parameter[1])
            model_eval_rm_train.update(parameter_dict)
            model_eval_rm_train.update(rule_mining_parameter_dict)
            model_eval_rm_train['data_type'] = 'train'
            evaluation_results = evaluation_results.append(model_eval_rm_train, ignore_index=True)

            # Test Set Rule Mining
            model_eval_rm_test, _ = evaluate_rule_mining(test, categories, target_col,
                                                         search_depth=rule_mining_parameter[0],
                                                         max_premise_size=rule_mining_parameter[1],
                                                         theory=theory)
            model_eval_rm_test.update(parameter_dict)
            model_eval_rm_test['data_type'] = 'test'
            model_eval_rm_test.update(rule_mining_parameter_dict)
            model_eval_rm_test['training_runtime'] = model_eval_rm_train.get('training_runtime')
            evaluation_results = evaluation_results.append(model_eval_rm_test, ignore_index=True)

    undiscretized_data = False

    if undiscretized_data:

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
        model_eval_dt_train.update(parameter_dict)
        model_eval_dt_train['data_type'] = 'train'
        evaluation_results = evaluation_results.append(model_eval_dt_train, ignore_index=True)

        # Test Set Decision Trees
        model_eval_dt_test, _ = evaluate_decision_trees(test, target_col, decision_tree)
        model_eval_dt_test.update(parameter_dict)
        model_eval_dt_test['training_runtime'] = model_eval_dt_train.get('training_runtime')
        model_eval_dt_test['data_type'] = 'test'
        evaluation_results = evaluation_results.append(model_eval_dt_test, ignore_index=True)

        # evaluate_hero_algorithm(train, categories, target_col)
    evaluation_results.to_csv('evaluation_result_%s.csv' % dt.datetime.now().strftime("%Y_%m_%d_%H_%M"), index=False)
