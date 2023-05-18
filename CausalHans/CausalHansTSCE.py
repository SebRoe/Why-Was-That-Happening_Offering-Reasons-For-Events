from TSCE.DataTSCE import DataTSCE

from TSCE.InterpreterTSCE import InterpreterTSCE
import numpy as np 
import pandas as pd 


class CausalHansDataTSCE(DataTSCE):

    def __init__(self, rollout: np.ndarray):

        super().__init__()

        rollout = rollout[:3000]

        self.rollout = dict() 
        for cPerson, cPersonData in enumerate(rollout):
            self.rollout[cPerson] = dict() 
            for cTs, cTsData in enumerate(cPersonData):
                A, F, H, M = np.hsplit(cTsData, 4)
                self.rollout[cPerson][cTs] = {"Age":A[0], "Nutrition":F[0], "Health":H[0], "Mobility":M[0]}

        self.varNames = ["Age", "Nutrition", "Health", "Mobility"]



class CausalHansInterpreterTSCE(InterpreterTSCE):
   def __init__(self, data: DataTSCE):
        super().__init__()

        self.data = data 

        cColumns = [f"-1_{i}" for i in ["Age", "Nutrition", "Health", "Mobility"]] + [f"0_{i}" for i in ["Age", "Nutrition", "Health", "Mobility"]]
        
        self.causalGraph = pd.DataFrame(columns=cColumns, index=cColumns)

        # Instantaneous causal relations
        self.causalGraph.loc["0_Age", "0_Nutrition"] = 1
        self.causalGraph.loc["0_Age", "0_Health"] = -2
        self.causalGraph.loc["0_Nutrition", "0_Health"] = 1
        self.causalGraph.loc["0_Health", "0_Mobility"] = 1

        # Delayed causal relations
        self.causalGraph.loc["-1_Age", "0_Age"] = 1
        self.causalGraph.loc["-1_Nutrition", "0_Nutrition"] = 1
        self.causalGraph.loc["-1_Health", "0_Health"] = 1
        self.causalGraph.loc["-1_Mobility", "0_Mobility"] = 1

        self.causalGraph.fillna(0, inplace=True)



