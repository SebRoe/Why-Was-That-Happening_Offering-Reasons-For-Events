from SCE.CausalNodeSCE import *
from SCE.EntrySCE import *
from SCE.DataSCE import *
from SCE.InterpreterSCE import *
import numpy as np 

class CausalHansEntrySCE(EntrySCE):
    def __init__(self, entry: np.ndarray, name: str, lut_names: dict, i2n:dict , id:int):
        super().__init__(entry, name, lut_names, i2n, id)


    def __str__(self):
        introduction = "\nPatient: {} \n\n".format(self.name)
        A, F, H, M = np.hsplit(self.entry, 4)
        A, F, H, M = A.flatten().round(2), F.flatten().round(2), H.flatten().round(2), M.flatten().round(2)
        introduction += "A: {} \n\n".format(A)
        introduction += "F: {} \n\n".format(F)
        introduction += "H: {} \n\n".format(H)
        introduction += "M: {} \n\n".format(M)
        return introduction




class CausalHansDataSCE(DataSCE):

    def __init__(self, data: np.ndarray):
        self.data = data
        self.lut_names = {'A': 'Age', 'F': 'Nutrition', 'H': 'Health', 'M': 'Mobility'}
        self.i2n = {0: 'A', 1: 'F', 2: 'H', 3: 'M'}
        self.n2i = {v: k for k, v in self.i2n.items()}

        super().__init__(data, self.lut_names, self.i2n)


    def select_entry(self, idx:int, name:str='Unnamed'):
        self.entry = CausalHansEntrySCE(self.data[idx], name, self.lut_names, self.i2n, idx)



class CausalHansInterpreterSCE(InterpreterSCE):
    def __init__(self) -> None:
        super().__init__()
        self.CEM = np.array([
            # The static/old representation of the CEM or the base case CEM
            # A  F  H  M
            [0, 1, -2, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
            [0, 0, 0, 0]
        ]) 