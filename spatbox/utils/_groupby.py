import numpy as np
import numpy.typing as npt


def groupby(X: npt.NDArray[np.int_], y: npt.NDArray[np.float_]):
    """group y by x

    Parameters
    ----------
    X : an numpy ndarray, shape (n_samples, n_features), dtype int
        the data clustered
    y : an numpy array, shape (n_samples,), dtype float
        the dependent variable
        
    Returns
    -------
    Dict[Union[int, str], numpy array], each key is cluster id, each value is the array
    
    Examples
    --------
    >>> X = np.array([[1, 2], [1, 3], [1, 2],[2, 3],[2, 4],[2, 5]])
    >>> y = np.array([1.7, 2.5, 3.3, 4.1, 5.6, 6.2])
    >>> y_by_x = group_by(X, y)
    >>> y_by_x
    {(1, 2): array([1.7, 3.3]), (1, 3): array([2.5]), (2, 3): array([4.1]), (2, 4): array([5.6]), (2, 5): array([6.2])}
    """
    # sort by each col
    col_num = X.shape[1]

    # index
    idx = np.arange(X.shape[0]).reshape(-1, 1)

    # add index to X
    X_idx = np.hstack((X, idx))

    # sort each col
    for i in range(col_num - 1, -1, -1):
        X_idx = X_idx[X_idx[:, i].argsort(kind="stable")]

    X = X_idx[:, :-1]  # sorted X
    idx = X_idx[:, -1].astype(int)  # sorted index
    y = y[idx]  # sorted y

    # group by each col
    unique_val, unique_idx = np.unique(X, axis=0, return_index=True)
    layer_y = np.split(y, unique_idx)[1:]
    result = dict(zip(map(tuple, unique_val), layer_y))
    return result
