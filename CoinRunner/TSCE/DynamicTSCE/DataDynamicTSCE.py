import numpy as np 

class DataDynamicTSCE():

    def __init__(self):
        self.rollout = None # Override this  

    def __str__(self):
        return f"Class: DataDynamicTSCE\n#Timesteps: {len(self.rollout)}\n#Missing Timesteps: {len(self.get_missing_timesteps())}"

    def get_timestep(self, t:int):
        if t in self.rollout.keys():
            return self.rollout[t]
        else:
            return None

    def timestep_exits(self, t:int):
        if t in self.rollout.keys():
            return True
        else:
            return False
        
    def get_rollout_timesteps(self):
        return list(self.rollout.keys())
        
    def get_missing_timesteps(self):
        return [t for t in range(max(self.rollout.keys())) if t not in self.rollout.keys()]