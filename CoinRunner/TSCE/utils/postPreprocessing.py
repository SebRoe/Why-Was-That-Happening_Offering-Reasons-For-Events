
import numpy as np
import pandas as pd 
import random 

def allRolloutsInstant(rollouts:list, dropKeys:list):

    frames = [] 
    for rollout in rollouts:
        n_frames = len(rollout)
        for j in range(n_frames):
            tmp0 = rollout[j]
            new = {}
            for k in tmp0.keys():
                if k not in dropKeys:
                    new[k] = tmp0[k]
            frames.append(new)
    return pd.DataFrame(frames)


def singleRolloutInstant(gamestates:list, dropKeys:list):
    frames = []
    for d in gamestates:
        new = {}
        for k in d.keys():
            if k not in dropKeys:
                new[k] = d[k]
        frames.append(new)
    return pd.DataFrame(frames)


def allRolloutsTransitions(rollouts:list, dropKeys:list, transitions:int=1):
    frames = [] 
    for rollout in rollouts:
        n_frames = len(rollout)
        for j in range(n_frames - transitions):
            tmp0 = rollout[j]
            tmp1 = rollout[j + transitions]
            new = {}

            for k in tmp0.keys():
                if k not in dropKeys:
                    new["0_" + k] = tmp0[k]
                else:
                    print("Dropping: ", k)

            for k in tmp1.keys():
                if k not in dropKeys:
                    new["1_" + k] = tmp1[k]
            
            frames.append(new)
    return pd.DataFrame(frames)


def singleRolloutTransitions(gamestates:list, dropKeys:list, transitions:int=1):
    frames = [] 
    for j in range(len(gamestates) - transitions):
        tmp0 = gamestates[j]
        tmp1 = gamestates[j+transitions]
        new = {}

        for k in tmp0.keys():
            if k not in dropKeys:
                new["0_" + k] = tmp0[k]

        for k in tmp1.keys():
            if k not in dropKeys:
                new["1_" + k] = tmp1[k]
        
        frames.append(new)
    return pd.DataFrame(frames)


def singleRolloutTransitionsCorrected(gamestates:list, dropKeys:list, transitions:int=1):
    frames = [] 
    for j in range(len(gamestates) - transitions):
        tmp0 = gamestates[j]
        tmp1 = gamestates[j+transitions]
        new = {}

        for k in tmp0.keys():
            if k not in dropKeys:
                new["-1_" + k] = tmp0[k]

        for k in tmp1.keys():
            if k not in dropKeys:
                new["0_" + k] = tmp1[k]
        
        frames.append(new)
    return pd.DataFrame(frames)

def singleRolloutMultipleTransitionsCorrected(gamestates:list, dropKeys:list, transitions:int=1):
    frames = [] 
    for j in range(len(gamestates) - transitions):

        states = [gamestates[i] for i in range(j, j+transitions+1)]
        new = {}
        for i in range(len(states)):
            for k in states[i].keys():
                if k not in dropKeys:
                    new[str(i - transitions) + "_" + k] = states[i][k]        
        frames.append(new)
    return pd.DataFrame(frames)

def remove_singular_columns(df):
    corr = df.corr()
    corr_abs = np.abs(corr)
    np.fill_diagonal(corr_abs.values, 0)
    columns_to_remove = set()
    for column in corr_abs.columns:
        if column in columns_to_remove:
            continue
        correlated_columns = corr_abs[corr_abs[column] > 0.999].index
        if len(correlated_columns) == 0:
            continue
        columns_to_remove |= set(correlated_columns.difference([column]))
    
    for column in df.columns:
        unique_values = df[column].nunique()
        if unique_values == 1:
            columns_to_remove.add(column)
            
    return df.drop(columns=columns_to_remove)


def remove_singular_indices(df):
    # Swap df index and df columns 
    df = df.T
    df = remove_singular_columns(df)
    return df.T



def getCorrelatedFeaturesNames(df, threshold=0.95, dropKeys:list = []):
   
    observed_sets = []
    correlations = []
    toDrop = []
    columns = df.columns
    for col in columns:
        for col2 in columns:
            if col != col2 and set([col, col2]) not in observed_sets:

                if df[col].corr(df[col2]) > threshold:
                    correlations.append((col, col2, df[col].corr(df[col2])))
                    toDrop.append(col2)
                observed_sets.append(set([col, col2]))

    return toDrop


def getHighestCorrelations(df, threshold=0.95):
    observed_sets = []
    correlations = []
    columns = df.columns
    for col in columns:
        for col2 in columns:
            if col != col2 and set([col, col2]) not in observed_sets:
                if df[col].corr(df[col2]) > threshold:
                    correlations.append((col, col2, df[col].corr(df[col2])))
                observed_sets.append(set([col, col2]))

    correlations = sorted(correlations, key=lambda x: x[2], reverse=True)
    for c in correlations:
        print(c)

    return correlations

    


def myFilter(rollout:list, margin=5, transition=True, filter:dict = None, transitions:int=None):
    
    if filter is None:
        fil = {
            "goldcoinExists": 1,
            "enemyExists": 1,
            "powerupExists": 0,
        }

    else:
        fil = filter

    firstElementWithSetting = None 
    lastElementWithSetting = None 
    for counter, frame in enumerate(rollout):
        isImportant = True 
        for key in fil.keys():
            if key in frame.keys():
                if fil[key] != frame[key]:
                    isImportant = False
                    
        if isImportant:
            if firstElementWithSetting is None:
                firstElementWithSetting = counter 
            lastElementWithSetting = counter

    
    if firstElementWithSetting is None:
        # Return a random sequence of frames sometimes to create some noise with the length of 1/5 of the rollout length
        if random.randint(0, 100) > 95 and False:
            print("Using Noise Sequence")
            cStartHypo = 0 
            cEndHypo = len(rollout) 
            cSequenceLength = int(len(rollout) / 6)
            firstElementWithSetting = random.randint(cStartHypo, cEndHypo - cSequenceLength)
            lastElementWithSetting = firstElementWithSetting + cSequenceLength
        else:
            return None

    if firstElementWithSetting -margin >= 0:
        firstElementWithSetting -= margin
    else:
        firstElementWithSetting = 0

    if lastElementWithSetting + margin < len(rollout):
        lastElementWithSetting += margin
    else:
        lastElementWithSetting = len(rollout) - 1


    important_frames = []
    for i in range(firstElementWithSetting, lastElementWithSetting):
        important_frames.append(rollout[i])

    if transition:
        if transitions is None:
            df = singleRolloutTransitionsCorrected(important_frames, dropKeys=[], transitions=1)
        else:
            df = singleRolloutMultipleTransitionsCorrected(important_frames, dropKeys=[], transitions=transitions)
    else:
        df = singleRolloutInstant(important_frames, dropKeys=[])

    return df 


def removeImpossibleEdges(df):
    # Remove impossible causal effects
    for idx in df.index:
        for col in df.columns:
            if "0_" in idx and not "0_" in col:
                df.loc[idx, col] = 0
    return df 



def addGaussianNoise(df, noise=0.1):
    for col in df.columns:
        df[col] += np.random.normal(0, noise, df[col].shape)
    return df