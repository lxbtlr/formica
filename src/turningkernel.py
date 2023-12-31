import numpy as np
import src.helperfunctions as hf
from src.helperfunctions import execution_times,timing

class TurningKernel():
    # making a class for turning kernels to act as a template we can alter later
    @timing("tk init")
    def __init__(self, name:str="NA",values:list[list[float]]=[[.1,.3,.1],
                                                 [.1,0,.1],
                                                 [.1,.1,.1]])->None:
        # loading weights
        self.turningKernel = np.array(values)
        self.name = name
        
    @timing("tk calc")
    def calc(self,direction:int):
        num90s = direction//90
        tmp = np.rot90(self.turningKernel.copy(),k=num90s)
        if (direction - 90*num90s) //45:
            tmp = hf.rot45(tmp)
        return tmp
