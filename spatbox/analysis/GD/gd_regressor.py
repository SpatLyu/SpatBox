import numpy as np
from sklearn.base import BaseEstimator,RegressorMixin
from sklearn.cluster import KMeans
from sklearn.utils.random import check_random_state
from sklearn.utils.validation import check_is_fitted
from spatbox.utils import groupby

class GeoDetectorRegressor(RegressorMixin, BaseEstimator):
    """

    The GeoDetector has a sklearn-like interface which can be used to detect
    the spatial stratified heterogeneity of a variable Y,or the determinant
    power of a covariate X of Y.
    The predict method of GeoDetector returns the mean of Y in each subgroup.
    
    Parameters
    ----------
    method: {ClusterMixin, str}, default=None
        method is the method to split x into subgroups.
        method can be a sklearn-like cluster method, or a string pre-defined
        in GeoDetector. such as "kmeans".
        
        if method is None, the dtype of X must be int.
        
        if method is a sklearn-like cluster method, then x will be clustered 
        by the method then the GeoDetector will be applied to the clustered x.
        
        if method is a string, then the pre-defined method will be used to
        cluster x. 
        Pre-defined methods include: kmeans (nature_breaks).
    
    Example:
    >>> from geodetector import GeoDetector
    >>> from geodetector.datasets import load_demo
    >>> gd = GeoDetector()
    >>> gd.fit(load_demo())
    
    References
    ----------
    .. [1] Wang JF, Li XH, Christakos G, Liao YL, Zhang T, Gu X & Zheng XY. 2010.
    Geographical detectors-based health risk assessment and its application in 
    the neural tube defects study of the Heshun region, China. International 
    Journal of Geographical Information Science 24(1): 107-127.
    
    .. [2] Wang JF, Zhang TL, Fu BJ. 2016.A measure of spatial stratified 
    heterogeneity. Ecological Indicators 67(2016): 250-256. 
    """

    def __init__(self, *, method=None, random_state=42):
        # method is the method to split x into subgroups.
        self.method = method
        self.random_state = random_state  # random state

    def fit(self, X, y):
        """fit the model

        Parameters
        ----------
        X : {numpy array, pandas DataFrame}
            the variable to be used to detect the spatial stratified
        y : {numpy array, pandas Series}
            the dependent variable
        """
        random_state = check_random_state(self.random_state)
        X, y = self._validate_data(X, y, reset=True, y_numeric=True)

        if self.method is not None:
            # cluster each col of x when method is not None
            if isinstance(self.method, str):
                self.method = self._get_method(self.method)

            X = self._cluster(X, self.method)

        # assert dtype of x is int
        try:
            X = X.astype(np.int_)
        except ValueError:
            raise ValueError("dtype of X must be int when method is None.")

        assert issubclass(X.dtype.type, np.integer), "dtype of X must be int."

        # group y by x
        # group_val is a dict, key is the layer ,and value is the array of y
        group_val = groupby(X, y)
        judge_dic = {key: val.mean() for key, val in group_val.items()}
        self.judge_dic = judge_dic  # map group to layer_mean

    def predict(self, X):
        """predict the spatial stratified heterogeneity of X

        Parameters
        ----------
        X : {numpy array, pandas DataFrame}
            the variable to be used to detect the spatial stratified

        Returns
        -------
        numpy array
            the spatial stratified heterogeneity of X
        """
        check_is_fitted(self)
        X = self._validate_data(X, reset=False)

        if self.method is not None:
            X = self._cluster(X, self.method)
        else:
            X = X.astype(np.int_)

        y = np.array([self.judge_dic[tuple(x)] for x in X])
        return y

    def _cluster(self, X, method):
        """use method to cluster each col of X

        Parameters
        ----------
        X : numpy array 
            the input data to be clustered
        method : sklearn-like cluster method 
            the method to cluster x
            
        Returns
        -------
        numpy array
            the clustered x
        """
        shape = X.shape
        clustered_X = np.zeros(shape)
        for i in range(shape[1]):
            clustered_X[:, [i]] = method.fit_predict(X[:, [i]]).reshape(-1, 1)
        return clustered_X

    def _get_method(self, method):
        method = method.lower()
        if method == "kmeans" or method == "nb":
            return KMeans(random_state=self.random_state, n_clusters=5)
        elif method.startswith("kmeans") or method.startswith("nb"):
            n_clusters = int(method.split("_")[1])
            return KMeans(random_state=self.random_state,
                          n_clusters=n_clusters)
        else:
            raise ValueError(f"method {method} is not supported.")
