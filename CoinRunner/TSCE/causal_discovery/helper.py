import sys 
import os 
import pandas as pd 
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ))
from utils.preprocessing import *
from constants import *
from utils.graphs import * 
from causallearn.search.ConstraintBased.FCI import fci
from causallearn.search.ConstraintBased.PC import pc 
from methods.LassoGranger import LassoGranger
from methods.VARGranger import VARGranger
from methods.MyVARLiNGAM import MyVARLiNGAM
try:
    from settings import * 
except:
    from .settings import * 

np.random.seed(42)

### Helpers for PC algorithm
def reduce_pc(dataframe):
    causal_effectsDf = pd.DataFrame(index=dataframe.columns, columns=dataframe.columns)

    for col in dataframe.columns:
        for row in dataframe.index:
            if dataframe.loc[row, col] == -1 and dataframe.loc[col, row] == 1:
                #print(f"{col} is a direct cause of {row}")
                #print("\n")
                causal_effectsDf.loc[col, row] = 1
                        
            if dataframe.loc[row, col] == 1 and dataframe.loc[col, row] == 1:
                causal_effectsDf.loc[row, col] = 1
                causal_effectsDf.loc[col, row] = 1

    causal_effectsDf.fillna(0, inplace=True)
    return causal_effectsDf


def reduce_pc_time(dataframe):
    causal_effectsDf = pd.DataFrame(index=dataframe.columns, columns=dataframe.columns)

    for col in dataframe.columns:
        for row in dataframe.index:

            t_row = int(row.split("_")[0])
            t_col = int(col.split("_")[0])
            
            if dataframe.loc[row, col] == -1 and dataframe.loc[col, row] == 1:
                #print(f"{col} is a direct cause of {row}")
                #print("\n")

                if t_col <= t_row:
                    causal_effectsDf.loc[col, row] = 1
                    
            if dataframe.loc[row, col] == 1 and dataframe.loc[col, row] == 1:
                if t_row <= t_col:
                    causal_effectsDf.loc[row, col] = 1
                
                if t_col <= t_row:
                    causal_effectsDf.loc[col, row] = 1

    causal_effectsDf.fillna(0, inplace=True)
    return causal_effectsDf

def run_pc(data: pd.DataFrame, indep_test="fisherz"):
    try:
        # Input for pc is (n_samples, n_features) -> Resulting in a (n_features, n_features) matrix and respectively a (n_features, n_features) graph
        matrix = data.to_numpy()
        G_pred = pc(matrix, indep_test=indep_test, verbose=False, alpha=0.05, node_names=data.columns)
        return G_pred
    except Exception as er:
        print(er)
        return None

### Helper for FCI Algorithm 

def reduce_fci(dataframe):
    causal_effectsDf = pd.DataFrame(index=dataframe.columns, columns=dataframe.columns)

    for col in dataframe.columns:
        for row in dataframe.index:
            if dataframe.loc[row, col] == -1 and dataframe.loc[col, row] == 1:
                #print(f"{col} is a direct cause of {row}")
                #print("\n")
                causal_effectsDf.loc[col, row] = 1
                        
            if dataframe.loc[row, col] == 2 and dataframe.loc[col, row] == 2:
                causal_effectsDf.loc[row, col] = 1
                causal_effectsDf.loc[col, row] = 1

    causal_effectsDf.fillna(0, inplace=True)
    return causal_effectsDf


def reduce_fci_time(dataframe):
    causal_effectsDf = pd.DataFrame(index=dataframe.columns, columns=dataframe.columns)

    for col in dataframe.columns:
        for row in dataframe.index:

            t_row = int(row.split("_")[0])
            t_col = int(col.split("_")[0])

            # if t_col < t_row:
            #     continue

            if dataframe.loc[row, col] == -1 and dataframe.loc[col, row] == 1:
                #print(f"{col} is a direct cause of {row}")
                #print("\n")

                if t_col <= t_row:
                    causal_effectsDf.loc[col, row] = 1
                        
            if dataframe.loc[row, col] == 2 and dataframe.loc[col, row] == 2:

                if t_row <= t_col:
                    causal_effectsDf.loc[row, col] = 1
                
                if t_col <= t_row:
                    causal_effectsDf.loc[col, row] = 1

    causal_effectsDf.fillna(0, inplace=True)
    return causal_effectsDf


def run_fci(data: pd.DataFrame, indep_test="fisherz", depth=-1):
    try:
        matrix = data.to_numpy()
        G_pred = fci(matrix, indep_test=indep_test, verbose=False, alpha=0.05, depth=depth, node_names=data.columns)
        return G_pred
    except Exception as er:
        raise Exception(er)

### Helper for Notears Algorithm 
def reduce_notears_time(df):

    """Columns and Indexes are the same. Columns timesteps are encoded as t_name. Make sure that there are no causal effects from the future to the past."""
    
    idx = []

    for row in df.index:
        t_row = row.split("_")[0]
        for col in df.columns:
            t_col = col.split("_")[0]
            if t_col < t_row:
                idx.append((row, col))
                

    # idx is a list of tuples. Each tuple is a pair of rows and columns that are not allowed to be causal effects.
    for row, col in idx:
        df.loc[row, col] = 0

    return df

### Other helpers 
def create_directory(subfolder):
    path = os.path.join("TSCE", "causal_discovery", "results", subfolder)
    os.makedirs(path, exist_ok=True)
    return path


def dictionary_to_string(dictionary):
    string = ""
    for key, value in dictionary.items():
        string += f"{key}-{value}_"
    return string 




