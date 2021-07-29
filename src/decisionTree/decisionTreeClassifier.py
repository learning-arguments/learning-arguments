from matplotlib import pyplot as plt
from sklearn import tree
import time
from skopt import BayesSearchCV
from skopt.space import Integer
from skopt.utils import use_named_args
from skopt.plots import plot_objective
from sklearn.model_selection import cross_val_score
from skopt import gp_minimize
from pathlib import Path


# this class performs rule-mining based on decision trees
# note: to train the decision trees, discretization of the data is not required
# however, oneHotEncoding is required
# to do this, use oneHotEncoder.encode() from the folder preprocessing
class decisionTreeClassifier:

    def __init__(self):
        self.clf = tree.DecisionTreeClassifier(random_state=0)

    # performs hyperparameter tuning on the decision tree
    def trainDecTree(self, X, y, scoring='f1_macro'):
        # defining the search space
        search_spaces = [
            Integer(1, 50, name='max_depth'),
            Integer(1, X.shape[1], name='max_features'),
            Integer(1, 1000, name='min_samples_leaf'),
            Integer(2, 1000, name='min_samples_split')]

        @use_named_args(search_spaces)
        def objective(**params):
            self.clf = tree.DecisionTreeClassifier(**params, random_state=0)
            scores = cross_val_score(self.clf, X, y, cv=10)
            return -scores.mean()

        start_time = time.time()
        gp = gp_minimize(objective, search_spaces, n_calls=100, random_state=0)
        end_time = time.time()
        #print("Time used for Tuning the model: %.2f minutes." % ((end_time - start_time) / 60))

        params = gp.x

        self.clf = tree.DecisionTreeClassifier(max_depth=params[0],
                                               max_features=params[1],
                                               min_samples_leaf=params[2],
                                               min_samples_split=[3],
                                               random_state=0)
        self.clf.fit(X, y)
        _ = plot_objective(gp)

        Path("hyperVisualizations").mkdir(exist_ok=True)
        plt.savefig("hyperVisualizations/parameterAccuracies.png", bbox_inches='tight')
        plt.close()

    def predict(self, X):
        return self.clf.predict(X)
