import os 
from causal_discovery.helper import dictionary_to_string
from causal_discovery.settings import * 

from anytree import Node, RenderTree, NodeMixin, Resolver, PostOrderIter, PreOrderIter
from anytree.exporter import DotExporter
from anytree.dotexport import RenderTreeGraph

from DynamicTSCE.tree_helper import nodeattrfuncDynamicTSCE, nodenamefuncDynamicTSCE
### Creating the used causal GSI Graph 

def getContextGraphs(method, subDirectory,  transitions=1, isConcatedModel=False, usedFilters=None, verbose=False):

    # Reading all the produced Graphs 
    if usedFilters is None:
        usedFilters = [
            {
                "enemyExists": True, 
                "powerupExists": False 
            },
            {
                "enemyExists": True, 
                "powerupExists": True 
            },
            {
                "enemyExists": False, 
                "powerupExists": False 
            }
        ]
    else:
        usedFilters = usedFilters

    contextGraphs = {}
    if not isConcatedModel:
        for filter in usedFilters:
            path = os.path.join("DynTSCEGraphs", subDirectory, "data", f"{method}", dictionary_to_string(filter), f"transition_{transitions}Step")
            dfs = []
            for i in range(USE_ROLLOUT_UNTIL):
                try:
                    fileName = f"{method}_summary_transition_{transitions}Step_rollout_{i}.pkl"
                    df = pd.read_pickle(os.path.join(path, fileName))
                    dfs.append(df)
                except:
                    if verbose: print("File not found:",  fileName)

            ## Define how to process the data 
            finalDf = dfs[0]
            for i in range(1, len(dfs)):
                finalDf =  finalDf.add(dfs[i], fill_value=0)

            finalDf = finalDf / len(dfs)
            contextGraphs[str(filter)] = finalDf 

        return contextGraphs
    else:
        for filter in usedFilters:

            path = os.path.join("DynTSCEGraphs", subDirectory, "data", f"{method}", dictionary_to_string(filter), f"transition_{transitions}Step")
            dfs = []
            try:
                #fileName = f"{method}_summary_transition_{transitions}Step_rollout_0_until_100.pkl"
                fileName = f"{method}_summary_transition_{transitions}Step_rollout_0_until"
                files = list(os.listdir(path))
                for file in files :
                    if file.startswith(fileName) and not "model" in file:
                        fileName = file

                print("Read concated model:", fileName, "from:", dictionary_to_string(filter))
                df = pd.read_pickle(os.path.join(path, fileName))
                dfs.append(df)
            except:
                if verbose: print("File not found:",  fileName, "from:", dictionary_to_string(filter))

            ## Define how to process the data 
            finalDf = dfs[0]
            contextGraphs[str(filter)] = finalDf 

        return contextGraphs



def findPairVarValue(rollout, varName, value, verbose=False):
    ids = [] 
    for counter, gamestate in enumerate(rollout):
        if gamestate[varName] == value:
            ids.append(counter)
    
    if verbose: print(ids)
    return ids


def generateTreeImage(rootNode:Node, filepath):
    RenderTreeGraph(rootNode, nodenamefunc=nodenamefuncDynamicTSCE, nodeattrfunc=nodeattrfuncDynamicTSCE).to_picture(filepath)

    

def printFrameByID(rollout, id, last=False):
    if not last:
        for frame in rollout:
            if frame["frameID"] == id:
                print(json.dumps(frame, indent=4, sort_keys=True))
    else:
        cClosest = None 
        for frame in rollout:
            if frame["frameID"] < id:
                if cClosest == None:
                    cClosest = frame 
                else:
                    if frame["frameID"] > cClosest["frameID"]:
                        cClosest = frame


        print(json.dumps(cClosest, indent=4, sort_keys=True))