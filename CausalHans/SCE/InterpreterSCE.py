import numpy as np 

from Utils.logger import get_spec_logger
from .CausalNodeSCE import * 
from .DataSCE import DataSCE

logger = get_spec_logger(__name__)


class InterpreterSCE():

    def __init__(self):
        self.R = lambda x,y: x < y
        self.R_desc = "below average"
        self.CEM = None
        self.TSCEM = None

        self.S1 = [lambda x,y: x < y, lambda x,y: x > y] # Scenario 1, R1 =: x < y, R2 =: x > y
        self.S2 = [lambda x,y: x > y, lambda x,y: x < y] # Scenario 2, R1 =: x > y, R2 =: x < y
        self.outcomes = [(self.S1, 1), (self.S2, -1)]

    ##########################################
    # Prerequirements for SCE (Step 1)
    ##########################################

    def Q(self, data: DataSCE , idxChild: int):
        # Single Why Question 
        entry = data.get_entry().get_value()
        if self.R(entry[idxChild], data.get_mean(idxChild)):
            return (idxChild, entry)
        else:
            raise Exception("Question is a False Statement")

    def pronounce_Q(self, data: DataSCE, question):
        idxChild, _ = question
        patient_name  = data.get_entry().get_name()
        idxChild = data.lut_names[data.i2n[idxChild]]
        relation_description = self.R_desc
        pronounciation  = "Why is {} {} {}?".format(patient_name, idxChild, relation_description)
        return pronounciation

    ##########################################
    #### Helper Calculations for SCE #########
    ##########################################

    def mu(self, x):
        return np.mean(x)

    def pa(self, idx_node, vals=False):
        pa_idx = np.where(self.CEM[:, idx_node] != 0)[0]
        if vals:
            return  self.CEM[pa_idx, idx_node]
        else:
            return pa_idx


    def g(self, idxParent, idxChild):
        return self.CEM[idxParent, idxChild]


    ##########################################
    ###### SCE Calculations (Step 2) #########
    ##########################################



    def r1(self, parentIdx, childIdx, valueParent, valueChild, muParent, muChild, crossTS=False):

        act_sign = np.sign(self.g(parentIdx, childIdx))
     
        for (R1, R2), outcome in self.outcomes:
            if (act_sign < 0 and R2(valueParent, muParent) and R1(valueChild, muChild)) or (act_sign > 0 and R2(valueParent, muParent) and R2(valueChild, muChild)):
                return outcome

        return 0


    def r2(self, parentIdx, childIdx, valueParent, valueChild, muParent, muChild, crossTS=False):

        act_sign = np.sign(self.g(parentIdx, childIdx))

        for (R1, R2), outcome in self.outcomes:
            if (act_sign > 0 and R2(valueParent, muParent) and R1(valueChild, muChild)) or (act_sign < 0 and R2(valueParent, muParent) and R2(valueChild, muChild)):
                return outcome
        
        return 0
  


    def r3(self, parentIdx, childIdx, crossTS=False):
        # For now only implemented in a simple fashion. The part "mostly" is only referred to either the timestep or the time shift.
        # Not both at once. 

        if len(np.unique(abs(self.pa(childIdx)))) > 1:
            gs = [abs(self.g(parent, childIdx)) for parent in self.pa(childIdx)]
            Z = self.pa(childIdx)[np.argmax(gs)]
            return 1 if parentIdx == Z else 0
        else:
            return 0

    def indicator(self, parentIdx, childIdx, valueParent, valueChild, muParent, muChild, crossTS=False):
        """
        Indicator function for the SCI.
        For better understanding of the indicator function:
        [-1, 0, X] -> "because of low"
        [ 1, 0, X] -> "because of high"
        [ 0,-1, X] -> "although the low"
        [ 0, 1, X] -> "although the high"
        """
        p1 = self.r1(parentIdx, childIdx, valueParent, valueChild, muParent, muChild, crossTS)
        p2 = self.r2(parentIdx, childIdx, valueParent, valueChild, muParent, muChild, crossTS)
        p3 = self.r3(parentIdx, childIdx, crossTS)
        return (p1, p2, p3)

    ##########################################
    #### SCE /w Anytree ######################
    ##########################################
    def SCE(self, data:DataSCE, Q_C, node:Node=None):
        
        idxChild, entry = Q_C
        parents = self.pa(idxChild)

        # Base case for recursion
        if len(parents) == 0:
            return

        # Recursive case
        for parent in parents:
            muParent = data.get_mean(parent)
            muChild = data.get_mean(idxChild)
            valueParent = entry[parent]
            valueChild = entry[idxChild]
            ind = self.indicator(parent, idxChild, valueParent, valueChild, muParent, muChild)
            #R.append((ind, (data.i2n[parent], data.i2n[idxChild])))

            name = f"{data.lut_names[data.i2n[parent]]}"
            
            tmp_node = CausalNodeSCE(
                name,
                parent=node,
                indicator=ind,
                causalParent=data.i2n[parent],
                causalChild = data.i2n[idxChild], 
                muParent=muParent,
                muChild=muChild,
                valueParent=valueParent,
                valueChild=valueChild)

            self.SCE(data, (parent, entry), tmp_node)
            
            logger.debug("Indexes of nodes (Parent) (Current), {} {}".format(parent, idxChild))
            logger.debug("{:<25} {:.2f} vs {:.2f}".format("Value vs Mean (Parent)", entry[parent], muParent))
            logger.debug("{:<25} {:.2f} vs {:.2f}".format("Value vs Mean (Current)", entry[idxChild], muChild))
            logger.debug("{:<25} {}".format("Indicator", ind))
            logger.debug("") 

    def pronounce_SCE(self, pQ, rootNode:Node, removeDuplicates=False):
        # humand understandable reading (pronounciation)      

        S = pQ.split("Why is ")[1].capitalize()[:-1]
        S = S.split(" ")
        S.insert(2, "is")
        S = " ".join(S)
        seen_Nodes = []

        def pronounciate(node: Node):

            children = list(node.children)

            if len(children) > 0:
                S = "" 

                for idx, child in enumerate(children):
    
                    mapping = child.indicator
                    parent = node

                    if removeDuplicates:
                        if child.name in seen_Nodes:
                            continue
                        else:
                            seen_Nodes.append(child.name)

                    if mapping[2]:
                        S += "mostly "

                    if mapping[:2] == (1, 0): 
                        S += "because of high "
                    elif mapping[:2] == (-1, 0): 
                        S += "because of low "
                    elif mapping[:2] == (0, 1): 
                        S += "although the high "
                    elif mapping[:2] == (0, -1): 
                        S += "although the low "
                    else:
                        S += " for unknown reasons (noise term explanation) "

                    S += child.name + " "

                    if len(list(child.children)) > 0:
                        deeper = pronounciate(child)
                        if deeper != "":
                            S += "which is " + deeper

            return S 

        pronounciation = pronounciate(rootNode)
        return S + " " + pronounciation

   