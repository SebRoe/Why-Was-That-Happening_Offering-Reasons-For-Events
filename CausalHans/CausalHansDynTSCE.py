from DynTSCE.DataDynamicTSCE import DataDynamicTSCE 
from DynTSCE.EntryDynamicTSCE import EntryDynamicTSCE
from DynTSCE.InterpreterDynamicTSCE import InterpreterDynamicTSCE
from DynTSCE.CausalNodeDynamicTSCE import CausalNodeDynamicTSCE, nodenamefuncDynamicTSCE
from DynTSCE.tree_helper import * 
import numpy as np 
import pandas as pd 
import json, ast 

class CausalHansDataDynTSCE(DataDynamicTSCE):
    def __init__(self, data):
        """Receives a single Game Rollout. It should be preprocessed the same way as the used causal graph."""
        super().__init__()
        
        data = data[:3000]

        self.rollout = dict() 
        for cPerson, cPersonData in enumerate(data):
            self.rollout[cPerson] = dict() 
            for cTs, cTsData in enumerate(cPersonData):
                A, F, H, M = np.hsplit(cTsData, 4)
                self.rollout[cPerson][cTs] = {"Age":A[0], "Nutrition":F[0], "Health":H[0], "Mobility":M[0]}

        self.varNames = ["Age", "Nutrition", "Health", "Mobility"]


class CausalHansInterpreterDynTSCE(InterpreterDynamicTSCE):
   
   def __init__(self, data:CausalHansDataDynTSCE):
        super().__init__()
        self.contextGraphs = {}
        cColumns = [f"-1_{i}" for i in ["Age", "Nutrition", "Health", "Mobility"]] + [f"0_{i}" for i in ["Age", "Nutrition", "Health", "Mobility"]]

        causalGraphBelow = pd.DataFrame(columns=cColumns, index=cColumns)
        # Instantaneous causal relations
        causalGraphBelow.loc["0_Age", "0_Nutrition"] = -1
        causalGraphBelow.loc["0_Age", "0_Health"] = -2
        causalGraphBelow.loc["0_Nutrition", "0_Health"] = 1
        causalGraphBelow.loc["0_Health", "0_Mobility"] = 1

        # Delayed causal relations
        causalGraphBelow.loc["-1_Age", "0_Age"] = 1
        causalGraphBelow.loc["-1_Nutrition", "0_Nutrition"] = 1
        causalGraphBelow.loc["-1_Health", "0_Health"] = 1
        causalGraphBelow.loc["-1_Mobility", "0_Mobility"] = 1
        causalGraphBelow.fillna(0, inplace=True)

        causalGraphAbove= pd.DataFrame(columns=cColumns, index=cColumns)
        # Instantaneous causal relations
        causalGraphAbove.loc["0_Age", "0_Nutrition"] = 1
        causalGraphAbove.loc["0_Age", "0_Health"] = -2
        causalGraphAbove.loc["0_Nutrition", "0_Health"] = 1
        causalGraphAbove.loc["0_Health", "0_Mobility"] = 1

        # Delayed causal relations
        causalGraphAbove.loc["-1_Age", "0_Age"] = 1
        causalGraphAbove.loc["-1_Nutrition", "0_Nutrition"] = 1
        causalGraphAbove.loc["-1_Health", "0_Health"] = 1
        causalGraphAbove.loc["-1_Mobility", "0_Mobility"] = 1
        causalGraphAbove.fillna(0, inplace=True)

        self.contextGraphs["BelowEqual25"] = causalGraphBelow
        self.contextGraphs["Above25"] = causalGraphAbove

        self.data = data 
        self.contexts = ["BelowEqual25", "Above25"]

