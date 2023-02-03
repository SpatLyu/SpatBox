from collections import OrderedDict
from itertools import combinations
from typing import List

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import r2_score

from .gd_regressor import GeoDetectorRegressor


class GeoDetector:
    """ GeoDetector proveid an easy to use interface to calculate the q values
    of the covariates.
    
    References
    ----------
    .. [1] Wang JF, Li XH, Christakos G, Liao YL, Zhang T, Gu X & Zheng XY. 2010.
    Geographical detectors-based health risk assessment and its application in 
    the neural tube defects study of the Heshun region, China. International 
    Journal of Geographical Information Science 24(1): 107-127.
    
    .. [2] Wang JF, Zhang TL, Fu BJ. 2016.A measure of spatial stratified 
    heterogeneity. Ecological Indicators 67(2016): 250-256. 
    """

    def __init__(self,
                 data: pd.DataFrame,
                 x_names: List[str] = "1:",
                 y_name: str = "0",
                 *,
                 method=None,
                 random_state=42):
        self.gd_regressor = GeoDetectorRegressor(method=method,
                                                 random_state=random_state)
        self.x_names = x_names
        self.y_name = y_name
        self.data = data

        if x_names == "1:":
            self.x_names = list(data.columns)[1:]

        if y_name == "0":
            self.y_name = list(data.columns)[0]

        self._check_valid_data(data, self.x_names,
                               self.y_name)  #  type: ignore

    def q_values(self):
        """_q_values calculate the q values of the covariates

        Returns
        -------
        dict, the key is the covariate name, and the value is the q value
        """
        # key is the name of x, value is the q value of x
        dic = OrderedDict()
        for x_name in self.x_names:
            self.gd_regressor.fit(self.data[[x_name]], self.data[self.y_name])
            y_true = self.data[self.y_name]
            # the mean of y in each group is the prediction of y
            y_pred = self.gd_regressor.predict(self.data[[x_name]])
            # 1 - SSW/SST = 1 - MSE/VAR = R2
            q = r2_score(y_true, y_pred)
            dic[x_name] = q
        return dic

    def inter_q_values(self):
        """ factor_detect detect the interaction between covariates
        
        Returns
        -------
        dict, the key is the tuple covariate name, and the value is the q value
        
        Examples
        --------
        
        """
        dic = OrderedDict()
        for x1, x2 in combinations(self.x_names, 2):
            self.gd_regressor.fit(self.data[[x1, x2]], self.data[self.y_name])
            y_true = self.data[self.y_name]
            # the mean of y in each group is the prediction of y
            y_pred = self.gd_regressor.predict(self.data[[x1, x2]])
            # 1 - SSW/SST = 1 - MSE/VAR = R2
            q = r2_score(y_true, y_pred)
            dic[(x1, x2)] = q
        return dic

    def interaction_detect(self, interaction_type=False):
        """ factor_detect detect the interaction between covariates
        Parameters
        ----------
        return_union: bool, default False
        whether return the union of the covariates

        Returns
        -------
        a dataframe, the index and columns are the covariate names, and the 
        value is the q value
        """
        df = pd.DataFrame(index=self.x_names,
                          columns=self.x_names,
                          dtype=np.float_)

        q_dic = self.q_values()
        for x_name in self.x_names:
            df.loc[x_name, x_name] = q_dic[x_name]

        inter_q_dic = self.inter_q_values()
        for cols, q in inter_q_dic.items():
            df.loc[cols[0], cols[1]] = q
            df.loc[cols[1], cols[0]] = q

        if not interaction_type:
            return df
        elif interaction_type:
            interaction_type = pd.DataFrame(index=self.x_names,
                                            columns=self.x_names,
                                            dtype=np.int_)
            for cols, q in inter_q_dic.items():
                new_q = df.loc[cols[0], cols[1]]
                q_0 = q_dic[cols[0]]
                q_1 = q_dic[cols[1]]
                if new_q < min(q_0, q_1):
                    # no linear -
                    interaction_type.loc[cols[0], cols[1]] = 0
                elif min(q_0, q_1) < new_q < max(q_0, q_1):
                    # single_no_linear -
                    interaction_type.loc[cols[0], cols[1]] = 1
                elif max(q_0, q_1) < new_q < q_0 + q_1:
                    # bi+
                    interaction_type.loc[cols[0], cols[1]] = 2
                elif new_q == q_0 + q_1:
                    # alone
                    interaction_type.loc[cols[0], cols[1]] = 3
                elif new_q > q_0 + q_1:
                    # no linear +
                    interaction_type.loc[cols[0], cols[1]] = 4
                else:
                    raise ValueError("new_q is not in the range")
            return df, interaction_type
        else:
            raise ValueError("interaction_type must be bool")

    def plot_interaction(self, show=True):
        interaction_df = self.interaction_detect(interaction_type=False)
        # plot the heatmap of the interaction
        # cbar max value is 1
        ax = sns.heatmap(
            interaction_df,
            annot=True,
            cmap="crest",
            #  vmax=1,
            #  vmin=0,
            linewidths=0.5,
            linecolor="black")

        if show:
            plt.show()
            return ax
        else:
            return ax

    def plot(self, show=True):
        q = self.q_values()
        lst = [(i, j) for i, j in q.items()]
        lst.sort(key=lambda x: x[1], reverse=True)
        key, value = zip(*lst)
        key = np.array(key)
        value = np.array(value)

        ax = sns.barplot(
            x=value,
            y=key,
            orient="h",
            palette="crest",
            width=0.5,
            edgecolor="black",
        )

        # show value in the bar
        for p in ax.patches:
            ax.annotate(
                "%.2f" % p.get_width(),
                (p.get_width() / 2, p.get_y() + p.get_height() / 2.),
                ha="left",
                va="center",
                xytext=(-30, 0),
                textcoords="offset points",
            )

        if show:
            plt.show()
            return ax
        else:
            return ax
        
    def f_value(self):
        dic = OrderedDict()
        for x_name in self.x_names:
            self.gd_regressor.fit(self.data[[x_name]], self.data[self.y_name])
            y_true = self.data[self.y_name]
            # the mean of y in each group is the prediction of y
            y_pred = self.gd_regressor.predict(self.data[[x_name]])
            # 1 - SSW/SST = 1 - MSE/VAR = R2
            q = r2_score(y_true, y_pred)
            dic[x_name] = q
        return dic
        

    def _check_valid_data(self, data: pd.DataFrame, x_names: List[str],
                          y_names: str):
        for x_name in x_names:
            assert x_name in data.columns, f"{x_name} is not in data."

        assert y_names in data.columns, f"{y_names} is not in data."
