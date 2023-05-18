import numpy as np 

class DataSCE():

    def __init__(self, data: np.ndarray, lut_names:dict, i2n:dict):
        self.data = data
        self.lut_names = lut_names
        self.i2n = i2n
        self.n2i = {v: k for k, v in self.i2n.items()}

    def get_mean(self, idx:int):
        return np.mean(self.data[:, idx]) 

    def get_entry(self):
        return self.entry 

    def get_data(self):
        return self.data

    def print_means_by_iteration(self, idx):
        data = self.get_data_by_iteration(idx)
        print("\nPrinting means by iteration: ", idx)
        for i in range(4):
            print("{:<10} : {:.2f}".format(self.lut_names[self.i2n[i]],  np.mean(data[i,:])))
        print("\n")