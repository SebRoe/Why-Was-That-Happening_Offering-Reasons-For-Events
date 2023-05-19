import pandas as pd 

# Merging different dataframes into one 
# def sumDataframes(dfs: list):
#     sum_df = dfs[0]
#     for df in dfs[1:]:
#         for col in sum_df.columns:
#             col1 = df[col].values
#             col2 = sum_df[col].values
#             sum_df[col] = col1 + col2
#     return sum_df


def sumDifferentDfs(dfs: list, plainDf: pd.DataFrame):

    print(plainDf.columns[20:25])

    sum_df = plainDf
    for df in dfs:
        sum_df = sum_df.add(df, fill_value=0)


    print(sum_df.columns[20:25])

    return sum_df.astype(float)


def joinDifferentDfs(dfs: list, plainDf: pd.DataFrame):
    newDf = plainDf.copy()

    for df in dfs:
        for row in df.index:
            for col in df.columns:
                if df.loc[row, col] != 0:
                    newDf.loc[row, col] = df.loc[row, col]

    return newDf




def createMostCommonDf(dfs: list, plainDf: pd.DataFrame, threshold: float):
    """
    dfs: list of dataframes containing causal relationships between variables.
    plainDf: dataframe containing all variables in the dataset. Index and Columns are the same. 
    
    Rows have a causal effect on columns. Dfs may not have all columns or indices. We search for the most common connections independent of the causal effect in uniques dataframes.  

    returns a dataframe with the most common causal relationships between variables. 
    """
    dfs_binary = []
    for df in dfs:
        tmp = df.copy()
        tmp[tmp != 0] = 1
        dfs_binary.append(tmp)

    sum_df = sumDifferentDfs(dfs_binary, plainDf)
    sum_df[sum_df < threshold] = 0
    sum_df[sum_df >= threshold] = 1

    return sum_df.astype(float)






