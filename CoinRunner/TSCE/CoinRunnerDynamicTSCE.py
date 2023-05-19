from DynamicTSCE.DataDynamicTSCE import DataDynamicTSCE 
from DynamicTSCE.EntryDynamicTSCE import EntryDynamicTSCE
from DynamicTSCE.InterpreterDynamicTSCE import InterpreterDynamicTSCE
from DynamicTSCE.CausalNodeDynamicTSCE import CausalNodeDynamicTSCE, nodenamefuncDynamicTSCE
from CoinRunnerVarMapping import varMapping, VarTypes
from DynamicTSCE.tree_helper import * 
import numpy as np 
import json, ast 



class CoinRunnerDataDynTSCE(DataDynamicTSCE):

    def __init__(self, rollout):
        """Receives a single Game Rollout. It should be preprocessed the same way as the used causal graph."""
        super().__init__()
        
        # Saving the rollout. Keys are the frames in order to able to easily try out Reduction NOTHING and USERINPUT.
        self.rollout = dict()
        for counter, state in enumerate(rollout):
            self.rollout[counter] = state 

        self.varNames = list(self.rollout[0].keys())


class CoinRunnerInterpreterDynTSCE(InterpreterDynamicTSCE):
   
   def __init__(self, contextGraphs, data:CoinRunnerDataDynTSCE):
        super().__init__()
        self.contextGraphs = contextGraphs
        self.data = data 
        self.contexts = [ast.literal_eval(i) for i in self.contextGraphs.keys()]
        self.var2info = varMapping 
        self.max_explanation_depth = 4
        self.max_anticipation_depth = 6
        self.min_causal_effect = 0.01
        self.show_causal_strength = True 

