import numpy as np 
from Utils.logger import get_spec_logger
from .CausalNodeTSCE import *
from .pronunciation_helper import * 
from .tree_helper import *

logger = get_spec_logger(__name__)


import pandas as pd 

class InterpreterTSCE():

    def __init__(self):
        self.causalGraph = None # Override this 
        self.data = None # Override this 

        self.R = lambda x,y: x < y
        self.R_desc = "below average"
        self.S1 = [lambda x,y: x < y, lambda x,y: x > y] # Scenario 2, R1 =: x > y, R2 =: x < y
        self.S2 = [lambda x,y: x > y, lambda x,y: x < y] # Scenario 1, R1 =: x < y, R2 =: x > y
        self.outcomes = [(self.S1, 1), (self.S2, -1)]

        self.i2w = {
            (1,0): "because of his high",
            (-1,0): "because of his low",
            (0,1): "although his high",
            (0,-1): "although his low"
        }



    def _get_valid_question_ts_and_person(self, variable:str, num=1):

        cExamples = [] 

        for cPerson in reversed(self.data.rollout.keys()):
            for cTimestep in self.data.rollout[cPerson].keys():
                if self.validateQ(cPerson, cTimestep, variable, verbose=False):
                    cExamples.append((cPerson, cTimestep))
                    if len(cExamples) == num:
                        return list(sorted(cExamples, key=lambda x: x[1], reverse=True))

        if cExamples:
            return list(sorted(cExamples, key=lambda x: x[1], reverse=True))


        raise Exception("No valid question found") 
    
    def validateQ(self,  person:int, ts:int, variable:str, verbose=True):

        # We are asking if some variable is below average 
        cPersonValue = self.data.get_person_at_ts_variable(person, ts, variable)
        cPopulationMean = self.data.get_mean(ts, variable)

        if self.R(cPersonValue, cPopulationMean):
            if verbose: print("Question is a True Statement")
            return True 
        else:
            if verbose: raise Exception("Question is a False Statement")

    def _getDirectCauses(self, variable:str): 
        cAllCauses = self.causalGraph[f"0_{variable}"]
        #cAllCauses = cAllCauses.sort_values(ascending=False)
        cAllCauses = cAllCauses.reindex(cAllCauses.abs().sort_values(ascending=False).index) 

        cAllCauses = cAllCauses[cAllCauses != 0]
        return cAllCauses 


    def _splitDirectCauses(self, cDirectCauses:pd.Series):
        cIndex = list(cDirectCauses.index)
        cLags = [int(cIndex[i].split("_")[0]) for i in range(len(cIndex))]
        cVarNames = [cIndex[i].split("_")[1] for i in range(len(cIndex))]
        return cLags, cVarNames 



    def _r1(self, cCausalValueParent, cCausalValueChild, cCausalMuParent, cCausalMuChild, cSign):

        #  self.S1 = [lambda x,y: x < y, lambda x,y: x > y] # Scenario 2, R1 =: x > y, R2 =: x < y
        #  self.S2 = [lambda x,y: x > y, lambda x,y: x < y] # Scenario 1, R1 =: x < y, R2 =: x > y
        #  self.outcomes = [(self.S1, 1), (self.S2, -1)]

        for (R1, R2), outcome in self.outcomes:
            if (cSign < 0 and R2(cCausalValueParent, cCausalMuParent) and R1(cCausalValueChild, cCausalMuChild)) or (cSign > 0 and R2(cCausalValueParent, cCausalMuParent) and R2(cCausalValueChild, cCausalMuChild)):
                return outcome
        return 0


    def _r2(self, cCausalValueParent, cCausalValueChild, cCausalMuParent, cCausalMuChild, cSign):
    
        for (R1, R2), outcome in self.outcomes:
            if (cSign > 0 and R2(cCausalValueParent, cCausalMuParent) and R1(cCausalValueChild, cCausalMuChild)) or (cSign < 0 and R2(cCausalValueParent, cCausalMuParent) and R2(cCausalValueChild, cCausalMuChild)):
                return outcome
        return 0 


    def _r3(self, cNode, lag):

        #print("In r3:", cNode.causalChild, cNode.causalChild)
        cDirectCauses = self._getDirectCauses(cNode.causalChild)

        if len(cDirectCauses) == 1:
            #print("Returning 0 because of len(cDirectCauses) == 1")
            return 0 
        # Check if the causal parent is the highest causal parent and the effect is unique 

        cIndices = list(cDirectCauses.index)
        cCurrentIsMax = True 
        cMaxCauseStrength = cDirectCauses.abs().max()
        #print(cMaxCauseStrength)
        cStrongestIndices = []
        for cIndex in cIndices:
            cValue = abs(cDirectCauses[cIndex])
            if cValue == cMaxCauseStrength:
                cStrongestIndices.append(cIndex)

        if len(cStrongestIndices) > 1:
            #print("Returning 0 because of len(cStrongestIndices) > 1", cStrongestIndices)
            return 0 
        if len(cStrongestIndices) == 1 and cStrongestIndices[0] == f"{lag}_{cNode.causalParent}":
            #print(f"Returning 1 because of len(cStrongestIndices) == 1 and cStrongestIndices[0] == f'{lag}_{cNode.causalParent}'")
            return 1
        
        #print("Returning 0 because of default")
        return 0



    def _getIndicator(self, cNode, lag):
        """
        Indicator function for the SCI.
        For better understanding of the indicator function:
        [-1, 0, X] -> "because of low"
        [ 1, 0, X] -> "because of high"
        [ 0,-1, X] -> "although the low"
        [ 0, 1, X] -> "although the high"
        """

        cCausalMuChild = self.data.get_mean(cNode.timestepCausalChild, cNode.causalChild)
        cCausalMuParent = self.data.get_mean(cNode.timestepCausalParent, cNode.causalParent)

        cCausalValueParent = self.data.get_person_at_ts_variable(cNode.person, cNode.timestepCausalParent, cNode.causalParent)
        cCausalValueChild = self.data.get_person_at_ts_variable(cNode.person, cNode.timestepCausalChild,  cNode.causalChild)

        cSign = np.sign(self.causalGraph.loc[f"{lag}_{cNode.causalParent}", f"0_{cNode.causalChild}"])
        
        p1 = self._r1(cCausalValueParent, cCausalValueChild, cCausalMuParent, cCausalMuChild, cSign)
        p2 = self._r2(cCausalValueParent, cCausalValueChild, cCausalMuParent, cCausalMuChild, cSign)
        p3 = self._r3(cNode, lag)

        return (p1, p2, p3)




    def getExpTree(self, person:int, ts:int,  variable:str, max_depth:int = 15):

        if not self.validateQ(person, ts, variable, verbose=False):
            return f"Mario's {variable} is not below average."
        
        cMaxDepthTs = ts - max_depth if ts - max_depth > 0 else 0

        def recursion(node: CausalNodeTSCE, ts:int):

            if ts <= cMaxDepthTs:
                return

            cDirectCauses = self._getDirectCauses(node.name)
            cLags, cVarNames = self._splitDirectCauses(cDirectCauses)

            for lag, varName in zip(cLags, cVarNames):

                cNode = CausalNodeTSCE(
                    name=varName, 
                    person=person, 
                    timestepCausalParent=ts-abs(lag),
                    timestepCausalChild=ts,
                    causalParent=varName, 
                    causalChild=node.name,
                    valueCausalChild=self.data.get_person_at_ts_variable(person, ts, node.name),
                    valueCausalParent=self.data.get_person_at_ts_variable(person, ts-abs(lag), varName),
                )

                cNode.indicator = self._getIndicator(cNode, lag)
                cCheckTS = ts - abs(lag)

                cNode.parent = node 
                if not node.containsSimilarSubTree(cNode):
                    recursion(cNode, cCheckTS)


        root = CausalNodeTSCE(name=variable, person=person, timestepCausalChild=ts,  timestepCausalParent=ts)
        recursion(root, ts)

        #print("Finding sequences .. ")
        cSequences = find_sequences(root)
        #print("Finding sequences is done.", len(cSequences), "sequences found")
        return root 
    




    def getExplanation(self, node:CausalNodeTSCE):

        cRoot = node.root 
        cVerbose = True 
        rExplanations = [] 
        cExplainedUUIDs = [] 
        cTimeQAsked = node.timestepCausalChild

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
                    cFillerWords[-2] = ","
                elif len(cFillerWords) == 2:
                    cFillerWords[0] = " and"

                cFillerWords[-1] = "."

            return cFillerWords, cChildrenSorted
        
        def _helperTimeInformations(cNode, askingRoot:bool = False):
            if askingRoot:
                if cNode.timestepCausalParent == cTimeQAsked:
                    return " this year" 
                elif cNode.timestepCausalParent== cTimeQAsked - 1:
                    return " last year"
                else:
                    return f" {cTimeQAsked - cNode.timestepCausalParent} years ago"
            else:
                if cNode.timestepCausalParent == cNode.timestepCausalChild:
                    return " in the same year" 
                elif cNode.timestepCausalParent - 1== cNode.timestepCausalChild:
                    return " the year before"
                else:
                    return f" {abs(cNode.timestepCausalChild - cNode.timestepCausalParent)} year before"
            
        def _helperTimeInformationContinuous(cNode, askingRoot:bool = False):
            if askingRoot:
                if cNode.timestepCausalParent == cNode.timestepCausalChild:
                    return " in the objected year" 
                elif cNode.timestepCausalParent - 1 == cNode.timestepCausalChild:
                    return " continously one year ago"
                else:
                    return f" continously {abs(cNode.timestepCausalParent - cNode.timestepCausalChild)} year ago"
            else:
                if cNode.timestepCausalParent == cNode.timestepCausalChild:
                    return " in the objected year" 
                elif cNode.timestepCausalParent - 1 == cNode.timestepCausalChild:
                    return " continously one year before"
                else:
                    return f" continously {abs(cNode.timestepCausalParent - cNode.timestepCausalChild)} year before"

        def _getExplanation(node: CausalNodeTSCE):

            if node.is_leaf:
                return 
            
            if node.sequenceTag in cExplainedUUIDs:
                for cChild in node.children:
                    _getExplanation(cChild)
                return 
            else:
                cExplainedUUIDs.append(node.sequenceTag)

            cSequenceNodes = findall_by_attr(cRoot, node.sequenceTag, "sequenceTag")
            cSequenceNodes = sorted(cSequenceNodes, key=lambda x: x.timestepCausalParent, reverse=True)
            cMinTS = cSequenceNodes[0].timestepCausalParent
            cMaxTS = cSequenceNodes[-1].timestepCausalParent

            cExplanation = "" 
            cName = "Hans" if node.is_root else "His"

            timefunction = _helperTimeInformations

            def _helperPositioning(node):
                if self.data.get_mean(node.timestepCausalParent, node.name) < self.data.get_person_at_ts(node.timestepCausalParent, node.person)[node.name]:
                    return "above"
                else:
                    return "below"

            if cMinTS == cMaxTS:
                cPrefix = f"{cName} {node.name} was {_helperPositioning(node)} average {_helperTimeInformations(node, askingRoot=True)}"
                
            else:
                cPrefix = f"{cName} {node.name} constantly over the last {cMinTS - cMaxTS + 1} years was {_helperPositioning(node)} average"          
                timefunction = _helperTimeInformationContinuous

            cFillerWords, cChildrenSorted = _helperFillerWords(node)
            if len(cFillerWords) != len(cChildrenSorted):
                raise Exception("Something went wrong with the filler words.")
            
            for cFiller, cChild in zip(cFillerWords, cChildrenSorted):
                cIndicator = cChild.indicator 
                cMostly = " mostly" if cIndicator[2] == 1 else "" 
                cRelation = self.i2w[cIndicator[:2]]
                cExplanation += f"{cMostly} {cRelation} {cChild.name}{timefunction(cChild, False)}{cFiller}"
                _getExplanation(cChild)

            rExplanations.append(cPrefix + cExplanation)


        _getExplanation(node)

        #Cleaning up some stuff 
        rExplanations = [i.replace("  ", " ") for i in rExplanations]
        rExplanations = [i.replace(" ,", ",") for i in rExplanations]
        rExplanations = [i.replace(" .", ".") for i in rExplanations]
        rExplanations = [i.replace(" and.", ".") for i in rExplanations]
        rExplanations = [i.replace(" and,", ",") for i in rExplanations]
        rExplanations = list(reversed(rExplanations))
        return rExplanations 