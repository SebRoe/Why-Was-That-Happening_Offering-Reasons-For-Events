import numpy as np 

class EntrySCE():

    def __init__(self, value:np.ndarray, name:str, lut_names:dict, i2n:dict, id:int):
        self.id = id 
        self.value = value 
        self.name = name
        self.lut_names = lut_names
        self.i2n = i2n

    def get_value(self):
        return self.value

    def get_name(self):
        return self.name

    def get_id(self):
        return self.id

