import numpy as np
import pandas as pd
import xgboost
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
from fastai.tabular.data import *
from fastai.tabular.learner import *
from fastai.basics import *
from fastai.tabular.core import *
from fastai.tabular.model import *


def process_hans(cl_type, data):

    df = data 
    featlst=list(df.columns)
    featlst.remove('Mobility')

    y=df['Mobility']
    X_train, X_test, y_train, y_test = train_test_split(df, y, test_size=0.5, random_state=1)

    feat=list(df.columns)
    feat.remove('Mobility')
    if cl_type=="randomforest":
        # Hyperparameters adjustment
        clf = RandomForestClassifier(n_estimators=15, max_depth=5, min_samples_split=5, max_features="sqrt", random_state=0)

    print("Training on columns", feat)
    clf.fit(X_train[feat], y_train)

    # Perform cross validation
    scores = cross_val_score(clf, X_train[feat], y_train, cv=5)
    print("Cross-validation scores: ", scores)
    print("Average cross-validation score: ", scores.mean())

    pred= (clf.predict(X_test[feat]))
    pred = [int(round(value)) for value in pred]

    pd.options.mode.chained_assignment = None  # default='warn'

    X_test['Mobility']  = pred
    
    return (X_train[feat],y_train,X_test[feat],pred,clf)