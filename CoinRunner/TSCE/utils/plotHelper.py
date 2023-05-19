import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd 
import networkx as nx
from IPython.display import display
import matplotlib.colors as colors

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import networkx as nx

def plot_heatmap(df: pd.DataFrame, title: str= "", annot: bool=True, cbar: bool=True, save: bool = False, size: tuple = (20,20), show=False):
    fig, ax = plt.subplots(figsize=size) 

    cmap = colors.LinearSegmentedColormap.from_list('custom_cmap', ['red','green'])
    ax = sns.heatmap(df, annot=annot, linewidths=.5, linecolor="grey", cbar=cbar, cmap=cmap, vmin=-1, vmax=1)
    ax.set_title(title, fontsize=8)
    if save:
        fig.savefig(title + ".png")

    if not show:
        fig.clear()


def plot_multy_heatmap(dfs: tuple[int, pd.DataFrame], annot: bool=True, cbar: bool=True, save: bool = False, size: tuple = (17,17), **kwargs):
    """Generates a heatmap for each dataframe in the tuple and displays them in a quadratic grid. There should be only 1 cbar. The title is build up from lag and **kwargs"""
    fig, ax = plt.subplots(figsize=size) 
    plt.subplots_adjust(hspace=0.6, wspace=0.6)
    cmap = colors.LinearSegmentedColormap.from_list('custom_cmap', ['red','green'])
    for i, df in enumerate(dfs):
        ax = plt.subplot(2, 2, i+1)
        highest_value_df = df[1].max().max()
        ax = sns.heatmap(df[1], annot=annot, linewidths=.5, linecolor="grey", cbar=cbar, cmap=cmap, vmin=-highest_value_df, vmax=highest_value_df)
        kwargs_str = "\n".join([f"{k}={v}" for k, v in kwargs.items()])
        ax.set_title(f"lag: {df[0]} {kwargs_str}", fontsize=8)
    if save:
        fig.savefig(f"lag: {df[0]} {kwargs_str}" + ".png")


def plot_network_graph_transition(df: pd.DataFrame, path:str, save: bool = True):

    # First Graph Only Including Nodes from Timestep 0

    def singles(startswith, notstartswith):

        G = nx.Graph()
        
        columns = [i for i in df.columns if i.startswith(startswith)]
        to_drop_columns = [i for i in df.columns if i.startswith(notstartswith)]

        df_0 = df[columns]
        for column in to_drop_columns:
            df_0 = df_0.drop(column, axis=0)

        G.add_nodes_from([i for i in columns if i.startswith(startswith)])
        G.add_nodes_from([i for i in columns if i.startswith(startswith)])


        for i in range(len(df_0.index)):
            for j in range(len(df_0.columns)):
                if df_0.iloc[i,j] != 0:
                    G.add_edge(df_0.index[i], df_0.columns[j], weight=df_0.iloc[i,j])
        pos = nx.circular_layout(G)
        nx.draw(G, pos, with_labels=True, node_size=1000, font_size=8)
        if save:
            plt.rcParams["figure.figsize"] = (15,15)
            plt.savefig(path + startswith + ".png")

        plt.clf()

    singles("0_", "1_")
    singles("1_", "0_")

    G = nx.Graph()

    nodes0 = [i for i in df.columns if i.startswith("0_")]
    nodes1 = [i for i in df.columns if i.startswith("1_")]

    df_3 = df[nodes1]
    for column in nodes1:
        df_3 = df_3.drop(column, axis=0)

    G.add_nodes_from(nodes0)
    G.add_nodes_from(nodes1)

    for i in range(len(nodes0)):
        for j in range(len(nodes1)):
            if df_3.iloc[i,j] != 0:
                G.add_edge(df_3.index[i], df_3.columns[j], weight=df_3.iloc[i,j])



    # Get positions of nodes
    pos = {}
    pos.update( (n, (1, i)) for i, n in enumerate(nodes0) ) 
    pos.update( (n, (2, i)) for i, n in enumerate(nodes1) )

    # Draw Graph
    nx.draw(G, pos, with_labels=True, node_size=750, font_size=8)

    # labels = nx.get_edge_attributes(G,'weight')
    # nx.draw_networkx_edge_labels(G,pos,edge_labels=labels)

    if save:
        plt.rcParams["figure.figsize"] = (25,25)
        plt.savefig(path)




def save_heatmap(df: pd.DataFrame, title: str= "", annot: bool=True, cbar: bool=True, save: bool = False, size: tuple = (20,20)):
    fig, ax = plt.subplots(figsize=size) 

    cmap = colors.LinearSegmentedColormap.from_list('custom_cmap', ['red','green'])
    ax = sns.heatmap(df, annot=annot, linewidths=.5, linecolor="grey", cbar=cbar, cmap=cmap, vmin=-1, vmax=1)
    ax.set_title(title, fontsize=8)
    if save:
        fig.savefig(title + ".png")



def plot_ts_gamestateidea(df, effectsOnly=[], title="", show=False):

    G = nx.DiGraph() 

    for laggedVar in df.index:
        G.add_node(laggedVar)


    for currVar in df.columns:
        G.add_node(currVar)



    for currVar in df.columns:
        for laggedVar in df.index:
            if df.loc[laggedVar, currVar] != 0:
                if effectsOnly != []:
                    if currVar in effectsOnly:
                        G.add_edge(laggedVar, currVar, weight=df.loc[laggedVar, currVar ])
                else:
                    G.add_edge(laggedVar, currVar, weight=df.loc[laggedVar, currVar])

    try:
        edges,weights = zip(*nx.get_edge_attributes(G,'weight').items())
    except:
        print("No edges found in Rollout.")
    else:
        pos = {}
        
        
        pos.update( (n, (1, i)) for i, n in enumerate([i for i in df.index]))
        pos.update( (n, (2, i)) for i, n in enumerate([i for i in df.columns]))
        

        #cmap = colors.LinearSegmentedColormap.from_list('custom_cmap', ['red','green'])
        cmap = mcolors.LinearSegmentedColormap.from_list("", ["red", "white", "green"])

        plt.figure(figsize=(17, 17))
        nx.draw(G, pos, with_labels=True,  edge_color=weights, edge_cmap=cmap, node_size=250, font_size=12, edge_vmin=-max([abs(i) for i in list(weights)]),edge_vmax=max([abs(i) for i in list(weights)]))
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin = -max([abs(i) for i in list(weights)]), vmax=max([abs(i) for i in list(weights)])))
        #nx.draw(G, pos, with_labels=True,  edge_color=weights, edge_cmap=cmap, node_size=250, font_size=12, edge_vmin=-0.1,edge_vmax=0.1)
        #sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin = -0.1, vmax=0.1))
        sm._A = []
        plt.colorbar(sm)
        plt.axis('off')
        
        if title != "":
            plt.savefig(title + ".png")
        
        
        if show:
            plt.plot()
            plt.show()

        plt.clf()



