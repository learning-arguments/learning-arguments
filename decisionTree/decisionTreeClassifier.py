from matplotlib import pyplot as plt
from sklearn import tree
import time
from skopt import BayesSearchCV
from skopt.space import Integer
from skopt.plots import plot_objective


# this class performs rule-mining based on decision trees
# note: to train the decision trees, discretization of the data is not required
# however, oneHotEncoding is required
# to do this, use oneHotEncoder.encode() from the folder preprocessing
class decisionTreeClassifier:

    def __init__(self):
        self.clf = tree.DecisionTreeClassifier(random_state=0)

    # performs hyperparameter tuning on the decision tree
    def trainDecTree(self, X, y, scoring='f1_weighted'):
        # defining the search space
        search_spaces = {
            'max_depth': Integer(1, 50),
            'max_features': Integer(1, X.shape[1]),
            'min_samples_leaf': Integer(1, 1000),
            'min_samples_split': Integer(2, 1000)
        }

        opt = BayesSearchCV(
            estimator=self.clf,
            search_spaces=search_spaces,
            scoring=scoring,
            cv=10,
            random_state=1,
            n_jobs=-1,
            refit=False)

        print('Bayesian Optimization will require', opt.total_iterations, 'iterations.\n')

        start_time = time.time()
        opt.fit(X, y)

        end_time = time.time()
        print("Time used for Tuning the model: %.2f minutes." % ((end_time - start_time) / 60))

        params = opt.best_params_

        clf = tree.DecisionTreeClassifier(**params, random_state=0)

        _ = plot_objective(opt.optimizer_results_[0],
                           dimensions=["max_depth", "max_features", "min_samples_leaf", "min_samples_split"],
                           n_minimum_search=int(1e8))

        plt.savefig("hyperVisualizations/parameterAccuracies.png", bbox_inches='tight')
        plt.close()

    def predict(self, X):
        return self.clf.predict(X)
