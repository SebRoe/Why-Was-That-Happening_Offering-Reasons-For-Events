import numpy as np 
import pandas as pd 
class DataTSCE():

    def __init__(self):
        self.rollout = None #Overwrite this in the child class

    def get_mean(self, ts:int, variable:str):

        cValues = []
        for cPerson in self.rollout.keys():
            cValues.append(self.rollout[cPerson][ts][variable])
        return np.array(cValues).mean()


    def get_person_at_ts(self, ts:int, person:int):
        return self.rollout[person][ts]
    
    def get_person_at_ts_variable(self, person:int, ts:int, variable:str):
        return self.rollout[person][ts][variable]
    
