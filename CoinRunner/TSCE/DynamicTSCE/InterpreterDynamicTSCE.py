import numpy as np 
import pandas as pd 
from CoinRunnerVarMapping import VarTypes, VarProperties
from collections import defaultdict
import re, random 
from .CausalNodeDynamicTSCE import *
from .DataDynamicTSCE import DataDynamicTSCE
from .pronunciation_helper import * 
from .tree_helper import *


class InterpreterDynamicTSCE():


    def __init__(self):
        self.contextGraphs = None # Override this 
        self.data = None # Override this
        self.contexts = None # Override this
        self.var2info = None # Override this
        self.max_explanation_depth = 999 # Override this
        self.max_anticipation_depth = 999 # Override this
        self.min_causal_effect = 0.1 # Override this
        self.i2w = {
            (1,0): "because",
            (0,0): "altough",
            (0,1): "postive",
            (0,-1): "negative",
        }
        self.show_causal_strength = False 





    def validateQBehaviour(self, varName:str, ts:int, verbose=True):
        gamestate = self.data.get_timestep(ts)
        if gamestate is None:
            raise Exception(f"Time step {ts} does not exist in the data.")
        else:
            value = gamestate[varName]
            if value:
                if verbose: print(f"Question: Why is Mario {varName} ..? Is correct.")
                return True 
            else:
                if verbose: print(f"Question: Why is Mario {varName} ..? Is NOT correct.")
                return False 

    def _getContextGraph(self, ts:int):
        gamestate = self.data.get_timestep(ts)
        for context in self.contexts:
            cContextValid = True 
            for key, value in context.items():
                if value != gamestate[key]:
                    cContextValid = False 

            if cContextValid:
                return context 
        return None 
    
    def _getDirectCauses(self, contextGraph: pd.DataFrame, varName:str):
        cAllCauses:pd.Series = contextGraph[f"0_{varName}"]
        #cAllCauses = cAllCauses.sort_values(ascending=False)
        cAllCauses = cAllCauses.reindex(cAllCauses.abs().sort_values(ascending=False).index) 
        cAllCauses = cAllCauses[:self.max_explanation_depth]
        cAllCauses = cAllCauses[cAllCauses != 0]
        cAllCauses = cAllCauses[cAllCauses.abs() > self.min_causal_effect]
        return cAllCauses 
    

    def _getDirectEffects(self, contextGraph: pd.DataFrame, varName:str, fromLag:int=-1):
        cAllEffects: pd.Series = contextGraph.loc[f"{fromLag}_{varName}"]
        cAllEffects = cAllEffects.reindex(cAllEffects.abs().sort_values(ascending=False).index)
        cAllEffects = cAllEffects[:self.max_anticipation_depth]
        cAllEffects = cAllEffects[cAllEffects != 0]
        cAllEffects = cAllEffects[cAllEffects.abs() > self.min_causal_effect]
        return cAllEffects

    
    def _splitDirectCauses(self, directCauses:pd.Series):
        cIndex = list(directCauses.index)
        cLags = [int(i.split("_")[0]) for i in cIndex]
        cVarNames = [i.split("_")[1] for i in cIndex]
        return cLags, cVarNames 
    
    def _r1Binary(self, cValueCausalParent, cValueCausalChild, cRelationship):
        """child -> parent (Causality); 1 means Because, 0 means altough"""
        if cRelationship > 0:
            if (cValueCausalChild == 0 and cValueCausalParent == 0) or (cValueCausalChild == 1 and cValueCausalParent == 1):
                return 1 
            
            elif (cValueCausalChild == 1 and cValueCausalParent == 0) or (cValueCausalChild == 0 and cValueCausalParent == 1):
                return 0
            
        elif cRelationship < 0:
            if (cValueCausalChild == 0 and cValueCausalParent == 0) or (cValueCausalChild == 1 and cValueCausalParent == 1):
                return 0 
            
            elif (cValueCausalChild == 1 and cValueCausalParent == 0) or (cValueCausalChild == 0 and cValueCausalParent == 1):
                return 1
            

        print("cValueCausalChild", cValueCausalChild)
        print("cValueCausalParent", cValueCausalParent)
        print("cRelationship", cRelationship)
        raise Exception("Something went wrong in _r1Binary")


    def _r1Numeric(self, cRelationship):
        if cRelationship > 0: 
            return 1 
        else:
            return -1 
        
    def _r2(self, nodeChild, lag, cDirectCauses):
        
        cCauseName = nodeChild.causalParent

        if len(cDirectCauses) == 1:
            return 0
        
        cIndices = list(cDirectCauses.index)
        cCurrentIsMax = True 
        cMaxCauseStrength = cDirectCauses.max()
        cMinCauseStrength = cDirectCauses.min()

        if abs(cMinCauseStrength) > cMaxCauseStrength:
            cMaxCauseStrength = cMinCauseStrength
        else:
            cMaxCauseStrength = cMaxCauseStrength

        cStrongestIndices = []
        for cIndex in cIndices:
            cValue = cDirectCauses[cIndex]
            if cValue == cMaxCauseStrength:
                cStrongestIndices.append(cIndex)

        if len(cStrongestIndices) > 1:
            return 0 
        if len(cStrongestIndices) == 1 and cStrongestIndices[0] == f"{lag}_{nodeChild.causalParent}":
            return 1
        return 0



        # if cDirectCauses.loc[f"{lag}_{cCauseName}"] == max(cDirectCauses.values):
        #     return 1 
        # else:
        #     return 0 
        

    def _getIndicator(self, nodeChild, contextGraph, lag, cDirectCauses):

        cValueCausalParent = nodeChild.valueCausalParent
        cValueCausalChild = nodeChild.valueCausalChild


        cRelationship = contextGraph.loc[f"{lag}_{nodeChild.causalParent}", f"0_{nodeChild.causalChild}"]

        try:       
            if self.var2info[nodeChild.causalParent][1] == VarTypes.BOOLEAN and self.var2info[nodeChild.causalChild][1] == VarTypes.BOOLEAN:
                cR1Binary = self._r1Binary(cValueCausalParent, cValueCausalChild, cRelationship)
                cR1Numeric = 0

            else:# self.var2info[nodeChild.causalParent][1] == VarTypes.NUMERIC:
                cR1Binary = 0
                cR1Numeric = self._r1Numeric(cRelationship)
                
        except:
            print(nodeChild.causalChild)
            print(nodeChild.causalParent)
            raise
        cR2 = self._r2(nodeChild, lag, cDirectCauses)
        return (cR1Binary, cR1Numeric, cR2)



    def getExpTreeBehaviour(self, varName:str, ts:int, verbose=True):

        # Recursion creating the Explanation Tree 
        
        if not self.validateQBehaviour(varName, ts, verbose=verbose):
            return None 

        if verbose: print("The Rollout has", len(self.data.rollout), "Frames.")
        cEigenkantenStore = set()

        def recursion(node:CausalNodeDynamicTSCE, ts:int):
            if ts < 0:
                return 

            cContext = self._getContextGraph(ts)
            cContextAsStr = str(cContext)
            if cContextAsStr in self.contextGraphs:
                cContextGraph = self.contextGraphs[str(cContext)] 
            else:
                print("Context Graph not found", node.name, node.timestepCausalChild, node.timestepCausalParent)
                return
            cDirectCauses = self._getDirectCauses(cContextGraph, node.name)
            cLags, cVarNames = self._splitDirectCauses(cDirectCauses)

            for lag, varName in zip(cLags, cVarNames):

                cNode = CausalNodeDynamicTSCE(  
                    name=varName,
                    timestepCausalParent=ts - abs(lag), 
                    timestepCausalChild=ts, 
                    causalParent=varName,
                    causalChild=node.name,
                    valueCausalChild=self.data.get_timestep(ts)[node.name],
                    valueCausalParent=self.data.get_timestep(ts - abs(lag))[varName],
                    causalContext=cContext, 
                    relationStrength=cDirectCauses.loc[f"{lag}_{varName}"]
                )

 
                cNode.indicator = self._getIndicator(cNode, cContextGraph, lag, cDirectCauses)

                

                cCheckTS = ts - abs(lag)

                if cCheckTS > 0:
                    
                    if abs(lag) == 0:
                        #print("Called Eigenkante")
                        cEigenItem = (cNode.name, cNode.timestepCausalChild)
                        if cEigenItem in cEigenkantenStore:
                            continue 
                        else:
                            cEigenkantenStore.add(cEigenItem)
                            
                            #print("Eigenkante", cEigenItem, "Value:", cContextGraph.loc[f"{lag}_{cNode.name}", f"0_{cNode.causalParent}"])
                            cNode.addAttr("hasEigenkante", 1)
                            cNode.addAttr("eigenkanteCausalStrength", cContextGraph.loc[f"{lag}_{cNode.causalParent}", f"0_{cNode.causalChild}"]) 
                            
                    else:
                        
                        cNode.parent = node 
                        if not node.containsSimilarSubTree(cNode):    
                            recursion(cNode, cCheckTS)


        cContext = self._getContextGraph(ts)
        cRoot = CausalNodeDynamicTSCE(name=varName, timestepCausalChild=ts, timestepCausalParent=ts, causalContext=cContext, valueCausalChild=self.data.get_timestep(ts)[varName], valueCausalParent=self.data.get_timestep(ts)[varName])
        recursion(cRoot, ts)

        if verbose: print("Explanation Tree created. Finding sequences...")
        # find_sequences(cRoot)
        find_sequences2(cRoot)
        if verbose: print("Explanation Tree Sequences were marked.")
        return cRoot
    

    def getExplanations(self, node: CausalNodeDynamicTSCE):

        cVerbose = True 
        cContexts = list(set([cChild.causalContext for cChild in node.children]))
        rExplanations = defaultdict(list) 
        cExplainedUUIDs = []
        cTimeQAsked = node.timestepCausalChild
        
        def _helperVarType(cChild):
            if self.var2info[cChild.name][1] == VarTypes.BOOLEAN:
                if cChild.valueCausalParent == 1:
                    return ""
                else:
                    return "not "
            return ""
        
        def _helperFillerWords(cNode):
            cIndicators = [cChild.indicator for cChild in cNode.children]
            cFillerWords = [] 
            cChildrenSorted = [] 
            if len(set([i[:2] for i in cIndicators])) == 1:
                for cChild in cNode.children:
                    cFillerWords.append(",")
                    cChildrenSorted.append(cChild)

                if len(cFillerWords) > 2:
                    cFillerWords[-2] = " and"
                elif len(cFillerWords) == 2:
                    cFillerWords[0] = " and"

                cFillerWords[-1] = "." 
            else:
                cIndicators = list(set([i[:2] for i in cIndicators]))
                for counter, cIndicator in enumerate(cIndicators):
                    for cChild in [cChild for cChild in cNode.children if cChild.indicator[:2] == cIndicator]:
                        cFillerWords.append(",")
                        cChildrenSorted.append(cChild)

                    if counter != len(cIndicators) - 2:
                        cFillerWords[-1] = " and"

                if len(cFillerWords) > 2:
                    cFillerWords[-2] = " and"
                elif len(cFillerWords) == 2:
                    cFillerWords[0] = " and"

                cFillerWords[-1] = "."

            return cFillerWords, cChildrenSorted
        
        def _randomPronounciationHelper():
            return random.choice(["with the", "through the", "due to the"])


        def _helperTimeInformations(cNode, askingRoot:bool = False):

            cPronounValue = self.var2info[cNode.name][5].value
            cPronounType = self.var2info[cNode.name][5]
            cLambda = lambda x: _randomPronounciationHelper() if x == VarProperties.ACTION else ""

            if askingRoot:
                if cNode.timestepCausalParent == cTimeQAsked:
                    #return f" this {cPronounValue}"
                    return " "
                elif cNode.timestepCausalParent== cTimeQAsked - 1:
                    return f" last {cPronounValue}"
                else:
                    return f" {cTimeQAsked - cNode.timestepCausalParent} {cPronounValue}(s) ago"
            else:
                if cNode.timestepCausalParent == cNode.timestepCausalChild:
                    return f" {cLambda(cPronounType)} current {cPronounValue}" 
                elif cNode.timestepCausalParent == cNode.timestepCausalChild - 1 :
                    #return " due to the last action"
                    return f" {cLambda(cPronounType)} the {cPronounValue} before"
                else:
                    return f" {cLambda(cPronounType)} {abs(cNode.timestepCausalChild - cNode.timestepCausalParent)}th {cPronounValue} before"
            
        def _helperTimeInformationContinuous(cNode, askingRoot:bool = False):
            
            cPronounValue = self.var2info[cNode.name][5].value
            cPronounType = self.var2info[cNode.name][5]
            cLambda = lambda x: _randomPronounciationHelper() if cPronounType == VarProperties.ACTION else f"in the"

            if askingRoot:
                if cNode.timestepCausalParent == cNode.timestepCausalChild:
                    # return " in the objected ts"
                    return f" in the objected {cPronounValue}" 
                elif cNode.timestepCausalParent - 1 == cNode.timestepCausalChild:
                    return f" continously one {cPronounValue} ago"
                else:
                    return f" continously {abs(cNode.timestepCausalParent - cNode.timestepCausalChild)} {cPronounValue}(s) ago"
            else:
                if cNode.timestepCausalParent == cNode.timestepCausalChild:
                    return f" {cLambda(cPronounType)} {cPronounValue} in the objected " 
                elif cNode.timestepCausalParent == cNode.timestepCausalChild  - 1:
                    return f" continously {cLambda(cPronounType)} previous {cPronounValue} "
                else:
                    return f" continously {abs(cNode.timestepCausalParent - cNode.timestepCausalChild)} {cPronounValue}(s) before"

        def _addCausalStrength(cNode: CausalNodeDynamicTSCE):
            if self.show_causal_strength:
                return  f"({round(cNode.relationStrength, 3)})"
            else:
                return "" 


        def _getExplanation(node: CausalNodeDynamicTSCE):

            cPronounValue = self.var2info[node.name][5].value
            cPronounType = self.var2info[node.name][5]
            cLambda = lambda x: _randomPronounciationHelper() if cPronounType == VarProperties.ACTION else f"in the"

            if node.is_leaf:
                return 
            
            if node.causalSequenceUUID in cExplainedUUIDs:
                for cChild in node.children:
                    _getExplanation(cChild)
                return 
            else:
                cExplainedUUIDs.append(node.causalSequenceUUID)

            cSequenceNodes = findall_by_attr(node, node.causalSequenceUUID, "causalSequenceUUID")
            cSequenceNodes = sorted(cSequenceNodes, key=lambda x: x.timestepCausalParent, reverse=True)
            cMinTS = cSequenceNodes[0].timestepCausalParent
            cMaxTS = cSequenceNodes[-1].timestepCausalParent
            cExplanation = ""

            timefunction = _helperTimeInformations

            if cMinTS == cMaxTS:
                cPrefix = f"{self.var2info[node.name][2](_helperVarType(node))} {timefunction(node, askingRoot=True)}"
            else:
                cPrefix = f"{self.var2info[node.name][2](_helperVarType(node))}, constantly over {cPronounValue}(s) {cMaxTS} to {cMinTS},"
                timefunction = _helperTimeInformationContinuous

            cFillerWords, cChildrenSorted = _helperFillerWords(node)
            if len(cFillerWords) != len(cChildrenSorted):
                raise ValueError("Filler words and children do not match")



            for cFiller, cChild in zip(cFillerWords, cChildrenSorted):
                cIndicator = cChild.indicator
                cMostly = " mostly" if cIndicator[2] == 1 else "" 
                cRelation = self.i2w[cIndicator[:2]]
                cExplanation += f"{cMostly} {self.var2info[cChild.name][0](cRelation, _helperVarType(cChild))} {_addCausalStrength(cChild)}" # {timefunction(cChild, False)}"  #  ({round(cChild.relationStrength, 3)})"
                cExplanation += f"{cFiller}"
                _getExplanation(cChild)




            rExplanations[node.causalContext].append(cPrefix + cExplanation[:-1] + timefunction(cChild, False) + ".")
            #rExplanations.append(cPrefix + cExplanation)
             
        _getExplanation(node) 


        # Cleaning up some stuff
        for context in rExplanations.keys():
            rExplanations[context] = [str(re.sub(' +', ' ', i)) for i in rExplanations[context]]
            rExplanations[context] = [i.replace(" ,", ",") for i in rExplanations[context]]
            rExplanations[context] = [i.replace(" .", ".") for i in rExplanations[context]]
            rExplanations[context] = [i.replace(" and.", ".") for i in rExplanations[context]]
            rExplanations[context] = [i.replace(" and,", ",") for i in rExplanations[context]]
            rExplanations[context] = [i.replace("the the", "the") for i in rExplanations[context]]
            rExplanations[context] = list(reversed(rExplanations[context]))


        return rExplanations 





    def getAnticipations(self, node: CausalNodeDynamicTSCE):


        # For our example we know the causal graph. We know that we have a max lag of 1. 
        # For this function we assume the variable of interest came from the last timestep.
        # Effects go from -1 -> 0.

        cCurrTimestepInGraph = -1 
        cCausalParentNode = node 
        cContextGraph = self.contextGraphs[cCausalParentNode.causalContext]
        cDirectEffects = self._getDirectEffects(cContextGraph, cCausalParentNode.name, cCurrTimestepInGraph)

        _addCausalStrength = lambda x: f"({round(x, 3)})" if self.show_causal_strength else ""


        cTupLagVarname = [(int(i.split("_")[0]), i.split("_")[1]) for i in list(cDirectEffects.index)]

        cPositives = [i for i in cTupLagVarname if cContextGraph.loc[f"{cCurrTimestepInGraph}_{cCausalParentNode.name}", f"{i[0]}_{i[1]}"] > 0]
        cNegatives = [i for i in cTupLagVarname if cContextGraph.loc[f"{cCurrTimestepInGraph}_{cCausalParentNode.name}", f"{i[0]}_{i[1]}"] < 0]

        cPrefix = f"{self.var2info[node.name][3]} now"

        if cPositives != []:
            cPrefix += " has a positive effect on"

        for cLag, cVarname in cPositives:
            cPrefix += f" {self.var2info[cVarname][4]} {_addCausalStrength(cDirectEffects[f'{cLag}_{cVarname}'])},"
        
        cPrefix = cPrefix[:-1]

        if cNegatives != []:
            cPrefix += " and a negative effect on"

        for cLag, cVarname in cNegatives:
            cPrefix += f" {self.var2info[cVarname][4]} {_addCausalStrength(cDirectEffects[f'{cLag}_{cVarname}'])},"

        try:
            cPrefix = cPrefix[:-1]

            cPrefix = cPrefix.rsplit(",", 1)[0] + " and" + cPrefix.rsplit(",", 1)[1]
            cPrefix += f" in the next time step."
        except:
            pass 

        return cPrefix
             









    def cutTreeDepth(self, node: CausalNodeDynamicTSCE, depth: int):
        cStartTimestep = node.timestepCausalChild
        cFinalTimestep = cStartTimestep - depth

        def _helper(node: CausalNodeDynamicTSCE):

            if node.timestepCausalChild > cFinalTimestep:
                for cChild in node.children:
                    _helper(cChild)
            elif node.timestepCausalChild == cFinalTimestep:
                node.children = []
                node.causalSequenceUUID = None
            
            elif node.timestepCausalChild < cFinalTimestep:
                print("In Edge case:")
                cParent = node.parent 
                cParent.children.remove(node)

                if cParent.children == []:
                    cParent.causalSequenceUUID = None

        _helper(node)
        return node 

