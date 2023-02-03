import os
from ._groupby import groupby

__all__ = ["available", "get_path"]

_module_path = os.path.dirname(__file__)
_available_dir = [p for p in next(os.walk(_module_path))[1] if not p.startswith("__")]
_available_csv = {'disease': 'disease.csv',
                  'example': 'example.csv',
                  'gwr': 'gwr.csv'}

_available_zip = {"china_city_pcs": "china_city_pcs.zip",
                  "china": "china.zip",
                  "lp": "lp.zip",
                  "mws": "mws.zip",
                  "nineline": "nineline.zip",
                  "xian": "xian.zip",}
available = _available_dir + list(_available_zip.keys()) + list(_available_csv.keys())


def get_path(dataset):
    """
    Get the path to the data file.

    Parameters
    ----------
    dataset : str

    """
    if dataset in _available_zip:
        fpath = os.path.abspath(os.path.join(_module_path, _available_zip[dataset]))
        return "zip://" + fpath
    elif dataset in _available_csv:
        fpath = os.path.abspath(os.path.join(_module_path, _available_csv[dataset]))
        return fpath
    else:
        msg = "The dataset '{data}' is not available. ".format(data=dataset)
        msg += "Available datasets are {}".format(", ".join(available))
        raise ValueError(msg)