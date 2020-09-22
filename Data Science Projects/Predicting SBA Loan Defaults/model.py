"""
Deploys an XGBoost model to the dataset to predict defaults
of SBA loans.

Model details
  -- 80% train and 20% test sets
  -- One hot encoded categorical feature for banks
  -- Random oversampling to account for imbalanced class sizes
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import fbeta_score
from xgboost import XGBClassifier
from imblearn.over_sampling import RandomOverSampler
from imblearn.pipeline import Pipeline, make_pipeline
import pickle


def create_x_any_y(data):
    """Returns X and y DataFrames. Columns chosen for
    X were discovered to be the most significant during
    exploratory data analysis and model testing.
    """
    X = data.drop(['city', 'state', 'zip', 'bank', 'bank_state', 'naics', 'approv_date',
                      'approv_year', 'disburse_date', 'mis_status', 'balance_gross',
                      'chg_off_gross', 'gross_approve', 'sba_approve', 'sector', 'default'], axis=1)
    y = data['default']
    return X, y


def split(data):
    """Returns a train set of 80% and test set of 20%
    of the data for both features and targets.
    """
    X, y = create_x_any_y(data)
    X_train, y_train, X_test, y_test = train_test_split(X, y, test_size=.2)

    return X_train, X_test, y_train, y_test


def model(data):
    """Deploys an XGBoost model on the training data to predict
    whether or not an SBA loan will default. The model is
    then pickled for further use.

    Prints the true/false positives and
    negatives as well as an FBeta score weighting recall
    twice as important as precision.
    """

    X_train, X_test, y_train, y_test = split(data)

    pos = np.sum(y_train == 1)
    neg = np.sum(y_train == 0)
    ratio = {1: pos * 6, 0: neg}

    model = make_pipeline(RandomOverSampler(sampling_strategy=ratio),
                          XGBClassifier(n_estimators=86,
                                        max_depth=7,
                                        learning_rate=.2))

    model.fit(X_train, y_train)
    pickle.dump(model, open('final_model.pkl', 'wb'))

    tn, fp, fn, tp = confusion_matrix(y_test, model.predict(X_test)).ravel()

    print('True Positives: ', tp)
    print('True Negatives: ', tn)
    print('False Positives: ', fp)
    print('False Negatives: ', fn)
    print('FBeta: ', fbeta_score(y_test, model.predict(X_test), beta=2.0))

    return


def main():
    df = pd.read_csv('sba_data.csv')
    model(df)


main()
