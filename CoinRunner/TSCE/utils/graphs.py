import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import pandas as pd
import matplotlib.colors as colors
import os, pickle 
from .plotHelper import plot_multy_heatmap

def create_simple_dag(df, lag):
    G = nx.DiGraph() 


    for row in df.index:
        for column in df.columns:
            if df.loc[row, column] != 0:
                G.add_edge("0_" + row, lag + "_" + column, weight=df.loc[row, column])


    pos = {}
    pos.update( ("0_" + n, (1, i)) for i, n in enumerate([i for i in df.index]) )
    pos.update( (f"{lag}_" + n, (2, i)) for i, n in enumerate([i for i in df.columns]) )

    plt.figure(figsize=(10, 8))
    nx.draw(G, pos, with_labels=True, node_size=750, font_size=8)
    plt.plot()


def create_timeseries_dag(dfs: tuple[int, pd.DataFrame], sourceOnly: list[str] = [], effectOnly: list[str] = [], useBinary: bool=False, **kwargs):
    G = nx.DiGraph() 

    indices = dfs[0][1].index 
    for idx in indices:
        G.add_node(f"0_{idx}")

    for lag, df in dfs:
        for col in df.columns:
            G.add_node(f"{lag}_{col}")


    for row in indices:

        if sourceOnly != [] and row not in sourceOnly:
            continue

        for lag, df in dfs:
            for col in df.columns: 
                if effectOnly != [] and col not in effectOnly:
                    continue
                elif df.loc[row, col] != 0:
                    G.add_edge(f"{0}_{row}", f"{lag}_{col}", weight=df.loc[row, col])

    edges,weights = zip(*nx.get_edge_attributes(G,'weight').items())

    pos = {}
    pos.update( (f"{0}_{n}", (1, i)) for i, n in enumerate([i for i in indices]))
    pos.update( (f"{lag}_{n}", (int(lag) + 1, i)) for lag, df in dfs for i, n in enumerate([i for i in df.columns]) )

    cmap = colors.LinearSegmentedColormap.from_list('custom_cmap', ['red','green'])
  
    plt.figure(figsize=(17, 17))
    if useBinary:
        nx.draw(G, pos, with_labels=True,  edge_color=weights, edge_cmap=cmap, node_size=250, font_size=12, edge_vmin=-1,edge_vmax=1)
    else:
        nx.draw(G, pos, with_labels=True,  edge_color=weights, edge_cmap=cmap, node_size=250, font_size=12, edge_vmin=-max([abs(i) for i in list(weights)]),edge_vmax=max([abs(i) for i in list(weights)]))
    kwargs_str = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
    plt.title(f"{kwargs_str} \n sourceOnly: {sourceOnly} | effectOnly: {effectOnly}")
    plt.axis('off')
    plt.plot()


def ts_dag_accompanion(base_path, fileOfInterest, lags, threshold_binary=None, threshold_effect=None, sourceOnly=[], effectOnly=[], **kwargs):
    """Prints the associated Heatmaps for the given ts_dag. If sourceOnly or effectOnly is not None, the Heatmaps will be filtered accordingly."""

    useBinary = False 

    if threshold_binary is None and threshold_effect is None:
        raise Exception("At least one threshold has to be set!")
    
    elif threshold_binary is None:
        threshold = threshold_effect
    
    elif threshold_effect is None:
        useBinary = True
        threshold = threshold_binary


    dfs = [] 
    for lag in lags:
        extended_path = os.path.join(base_path, lag)
        with open(os.path.join(extended_path, fileOfInterest), "rb") as f:
            df = pickle.load(f)

            if useBinary:
                df = df[df > threshold]
            else:
                df = df[(df < -threshold) | (df > threshold)]

            if sourceOnly != []:
                df = df.loc[sourceOnly]
            if effectOnly != []:
                df = df[effectOnly]

            # Remove columns which are all 0 or nan
            df = df.loc[:, (df != 0).any(axis=0)]
            df = df.loc[:, (df.isna().sum(axis=0) != len(df.index))]
            
        dfs.append((lag, df))

    plot_multy_heatmap(dfs, file=fileOfInterest, threshold=threshold, sourceOnly=sourceOnly, effectOnly=effectOnly, **kwargs)


def ts_dag(base_path, fileOfInterest, sourceOnly, effectOnly, threshold_binary=None, threshold_effect=None, **kwargs):

    lags = [str(i) for i in range(1, 5)]

    useBinary = False 
    if threshold_binary is None and threshold_effect is None:
        raise Exception("At least one threshold has to be set!")
    
    elif threshold_binary is None:
        threshold = threshold_effect
    
    elif threshold_effect is None:
        useBinary = True
        threshold = threshold_binary

    dfs = [] 
    for lag in lags:
        extended_path = os.path.join(base_path, lag)
        with open(os.path.join(extended_path, fileOfInterest), "rb") as f:
            df = pickle.load(f)
            if useBinary:
                df[df < threshold] = 0
            else:
                df[(df > -threshold) & (df < threshold)] = 0
            dfs.append((lag, df))


    # Check if all dfs values are 0
    if all(df[1].values.sum() == 0 for df in dfs):
        print("Nothing left after thresholding!")
        return
        
    create_timeseries_dag(dfs, sourceOnly=sourceOnly, effectOnly=effectOnly,useBinary=useBinary,  fileOfInterest=fileOfInterest, threshold=threshold, **kwargs)
    ts_dag_accompanion(base_path, fileOfInterest, lags, threshold_binary=threshold_binary, threshold_effect=threshold_effect, sourceOnly=sourceOnly, effectOnly=effectOnly, **kwargs)



def instant_df_to_graph(df, save_path):
    G = nx.DiGraph() 

    for col in df.columns:
        G.add_node(col)

    for row in df.index:
        for col in df.columns: 
            if df.loc[row, col] != 0:
                G.add_edge(row, col, weight=df.loc[row, col])

    try:
        edges,weights = zip(*nx.get_edge_attributes(G,'weight').items())
    except:
        return 

    cmap = colors.LinearSegmentedColormap.from_list('custom_cmap', ['red','green'])
  
    plt.figure(figsize=(17, 17))
    nx.draw(G, pos=nx.circular_layout(G),  with_labels=True,  edge_color=weights, edge_cmap=cmap, node_size=250, font_size=12, edge_vmin=-max([abs(i) for i in list(weights)]),edge_vmax=max([abs(i) for i in list(weights)]))
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin = -max([abs(i) for i in list(weights)]), vmax=max([abs(i) for i in list(weights)])))
    sm._A = []
    plt.colorbar(sm)
    plt.axis('off')

    if save_path is not None:
        plt.savefig(save_path)
        plt.close()
    else:
        plt.plot()



def create_timeseries_dag_overview(df, path=None):
    G = nx.DiGraph() 


    for row in df.index:
        for col in df.columns: 
            if df.loc[row, col] != 0:

                if col not in G.nodes:
                    G.add_node(col)
                
                if row not in G.nodes:
                    G.add_node(row)

                G.add_edge(f"{row}", f"{col}", weight=df.loc[row, col])

    edges,weights = zip(*nx.get_edge_attributes(G,'weight').items())

    pos = {}
    vars = list(set([col.split("_")[1] for col in df.columns if col in G.nodes]))

    print("Updating pos")
    pos.update( (f"{col}", (int(col.split("_")[0]) + 1, vars.index(col.split("_")[1]))) for col in df.columns if col in G.nodes) 

    print(pos)
    cmap = colors.LinearSegmentedColormap.from_list('custom_cmap', ['red','green'])
  
    plt.figure(figsize=(50, 100))



    print("Drawing")
    nx.draw(G, pos, with_labels=True) #, edge_color=weights, edge_cmap=cmap, node_size=250, font_size=12, edge_vmin=-max([abs(i) for i in list(weights)]),edge_vmax=max([abs(i) for i in list(weights)]))
    plt.axis('off')
    print("Finished drawing")

    if path is not None:
        plt.savefig(path)
        plt.close()
    else:
        plt.plot()



def create_timeseries_dag_overview_gpt(df, path=None):
    G = nx.DiGraph() 

    for row in df.index:
        for col in df.columns: 
            if df.loc[row, col] != 0:
                if col not in G.nodes:
                    G.add_node(col)
                
                if row not in G.nodes:
                    G.add_node(row)

                G.add_edge(f"{row}", f"{col}", weight=df.loc[row, col])

    edges,weights = zip(*nx.get_edge_attributes(G,'weight').items())

    vars = list(set([col.split("_")[1] for col in df.columns if col in G.nodes]))
    num_vars = len(vars)

    plt.figure(figsize=(20*num_vars, 20*num_vars))

    for i in range(0, len(df.columns), num_vars):
        subgraph_cols = df.columns[i:i+num_vars]
        subgraph_vars = list(set([col.split("_")[1] for col in subgraph_cols if col in G.nodes]))

        H = G.subgraph(subgraph_cols)

        pos = {}
        pos.update( (f"{col}", (int(col.split("_")[0]), vars.index(col.split("_")[1]))) for col in subgraph_cols if col in H.nodes) 

        ax = plt.subplot(1, len(df.columns)//num_vars, i//num_vars + 1)
        ax.set_title(f'Time steps {i//num_vars} to {i//num_vars + num_vars - 1}', fontsize=30)
        
        cmap = colors.LinearSegmentedColormap.from_list('custom_cmap', ['red','green'])
        try:
            nx.draw(H, pos, with_labels=True, ax=ax, node_size=250, font_size=16,  connectionstyle='arc3,rad=0.2', edge_color=weights, edge_cmap=cmap, edge_vmin=-max([abs(i) for i in list(weights)]),edge_vmax=max([abs(i) for i in list(weights)]))
        except:
            nx.draw(H, pos, with_labels=True, ax=ax, node_size=250, font_size=16,  connectionstyle='arc3,rad=0.2'  )
    if path is not None:
        plt.savefig(path)
        plt.close()
    else:
        plt.show()



def create_timeseries_dag_overview_gpt2(df, path=None):
    G = nx.DiGraph() 

    for node in df.columns:
        G.add_node(node)


    for row in df.index:
        for col in df.columns: 
            if df.loc[row, col] != 0:
                G.add_edge(f"{row}", f"{col}", weight=df.loc[row, col])



    vars = list(set([col.split("_")[1] for col in df.columns]))
    num_vars = len(vars)

    plt.rcParams["figure.autolayout"] = True 
    #fig, axes = plt.subplots(1, len(df.columns)//num_vars, figsize=(3000, 35))
    fig, axes = plt.subplots(1, len(df.columns)//num_vars, figsize=(600,20), dpi=50)

    for i, ax in enumerate(axes):

        try:
            current_cols = [col for col in df.columns if col.startswith(f"{i}_")]
            nextStep_cols = [col for col in df.columns if col.startswith(f"{i+1}_")]
        except:
            continue 

        subgraph_cols = current_cols + nextStep_cols
        
        current_iterations = [int(col.split("_")[0]) for col in subgraph_cols]
        min_iter = min(current_iterations)
        max_iter = max(current_iterations)
        
        H = G.subgraph(subgraph_cols)
        
        try:
            edges,weights = zip(*nx.get_edge_attributes(H,'weight').items())
        except:
            print("No weights found.")

        #print("Num edges: ", len(edges))
        pos = {}
        pos.update( (f"{col}", (0, vars.index(col.split("_")[1]))) for col in subgraph_cols if col.startswith(f"{min_iter}_")) 
        pos.update( (f"{col}", (10, vars.index(col.split("_")[1]))) for col in subgraph_cols if col.startswith(f"{max_iter}_"))
        
        ax.set_title(f'Time steps {min_iter} to {max_iter}', fontsize=15)
        
        cmap = colors.LinearSegmentedColormap.from_list('custom_cmap', ['red','green'])
        try:
            nx.draw(H, pos, with_labels=True, connectionstyle="arc3,rad=0.1", ax=ax, node_size=250, width=2, font_size=12, edge_color=weights, edge_cmap=cmap, edge_vmin=-max([abs(i) for i in list(weights)]),edge_vmax=max([abs(i) for i in list(weights)]))
        except:
            nx.draw(H, pos, with_labels=True, connectionstyle="arc3,rad=0.1", ax=ax, node_size=250, width=2, font_size=12)
        
        ax.margins(0.15)
        
    if path is not None:
        plt.savefig(path)
        plt.close()
    else:
       plt.show()


def create_timeseries_dag_overview_gpt3(df, path=None):
    G = nx.DiGraph() 

    for node in df.columns:
        G.add_node(node)


    for row in df.index:
        for col in df.columns: 
            if df.loc[row, col] != 0:
                G.add_edge(f"{row}", f"{col}", weight=df.loc[row, col])

    try:
        edges,weights = zip(*nx.get_edge_attributes(G,'weight').items())
    except:
        pass 
    
    vars = list(set([col.split("_")[1] for col in df.columns]))
    num_vars = len(vars)
    
    plt.rcParams["figure.autolayout"] = True 
    #fig, axes = plt.subplots(1, len(df.columns)//num_vars, figsize=(3000, 35))
    fig, ax = plt.subplots(1, 1, figsize=(600,20), dpi=50)



    pos = {}
    pos.update( (f"{col}", (int(col.split("_")[0]) + 1, vars.index(col.split("_")[1]))) for col in df.columns) 
    
    
    cmap = colors.LinearSegmentedColormap.from_list('custom_cmap', ['red','green'])
    try:
        nx.draw(G, pos, with_labels=True, connectionstyle="arc3,rad=0.1", ax=ax, node_size=250, width=2, font_size=12, edge_color=weights, edge_cmap=cmap, edge_vmin=-max([abs(i) for i in list(weights)]),edge_vmax=max([abs(i) for i in list(weights)]))
    except:
        nx.draw(G, pos, with_labels=True, connectionstyle="arc3,rad=0.1", ax=ax, node_size=250, width=2, font_size=12)
    
    #ax.margins(0.15)
    
    if path is not None:
        plt.savefig(path)
        plt.close()
    else:
       plt.show()







def create_timeseries_dag_gsi_1(df, path=None):
    G = nx.DiGraph() 

    for node in df.columns:
        G.add_node(node)


    for row in df.index:
        for col in df.columns: 
            if df.loc[row, col] != 0:
                G.add_edge(f"{row}", f"{col}", weight=df.loc[row, col])

    try:
        edges,weights = zip(*nx.get_edge_attributes(G,'weight').items())
    except:
        pass 
    
    vars = list(set([col.split("_")[1] for col in df.columns]))
    num_vars = len(vars)
    
    plt.rcParams["figure.autolayout"] = True 
    fig, axes = plt.subplots(1, 1, figsize=(50, 10))
    
    

    pos = {}
    pos.update( (f"{col}", (int(col.split("_")[0]) + 1, vars.index(col.split("_")[1]))) for col in df.columns) 
    
    
    cmap = colors.LinearSegmentedColormap.from_list('custom_cmap', ['red','green'])
    try:
        nx.draw(G, pos, with_labels=True, connectionstyle="arc3,rad=0.05", node_size=250, ax=axes, width=2, font_size=12, edge_color=weights, edge_cmap=cmap, edge_vmin=-max([abs(i) for i in list(weights)]),edge_vmax=max([abs(i) for i in list(weights)]))
    except:
        nx.draw(G, pos, with_labels=True, connectionstyle="arc3,rad=0.05",node_size=250,  ax=axes,width=2, font_size=12)
    
    #ax.margins(0.15)
    
    if path is not None:
        plt.savefig(path)
        plt.close()
    else:
       plt.show()


