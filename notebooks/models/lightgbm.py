# -*- encoding: UTF-8 -*-
import copy
from typing import List, Tuple

import pandas as pd

import lightgbm as lgb
from lightgbm import Booster
from models.base import Model


class LightGBM(Model):
    def train_and_predict(self, train, valid, categorical_features: List[str], target: str, params: dict) \
            -> Tuple[Booster, dict]:
        if type(train) != pd.DataFrame or type(valid) != pd.DataFrame:
            raise ValueError(
                'Parameter train and valid must be pandas.DataFrame')

        if list(train.columns) != list(valid.columns):
            raise ValueError('Train and valid must have a same column list')

        predictors = train.columns.drop(target)
        d_train = lgb.Dataset(train[predictors], label=train[target].values)
        d_valid = lgb.Dataset(valid[predictors], label=valid[target].values)

        eval_results = {}
        model = lgb.train(params['model_params'],
                          d_train,
                          categorical_feature=categorical_features,
                          valid_sets=[d_train, d_valid],
                          valid_names=['train', 'valid'],
                          evals_result=eval_results,
                          **params['train_params'])
        return model, eval_results

    def train_without_validation(self, train, categorical_features: List[str], target: str, params: dict, best_iteration: int):
        predictors = train.columns.drop(target)
        d_train = lgb.Dataset(train[predictors], label=train[target].values)
        train_params = copy.deepcopy(params['train_params'])
        train_params['num_boost_round'] = best_iteration
        if 'early_stopping_rounds' in train_params:
            del train_params['early_stopping_rounds']
        model = lgb.train(params['model_params'],
                          d_train,
                          categorical_feature=categorical_features,
                          **train_params)
        return model
