import pandas as pd
import numpy as np
import sklearn.datasets as samples

# This class will later be used to make artificial datasets for testing purposes.
# The code simply creates a gaussian distribution - for now.

centers = np.array([1, 2, 3, 4]).reshape(-1, 1)
n_samples = [300, 300, 300, 300]

X, y = samples.make_blobs(
    n_samples = n_samples, centers = centers, n_features = 1, cluster_std = 0.1)

X = pd.DataFrame(X)