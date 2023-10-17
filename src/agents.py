from enum import Enum
import numpy as np
from src.turningkernel import TurningKernel
import src.helperfunctions as hf
from src.helperfunctions import execution_times, timing
#TODO: Specify what is being imported explicitly


#DIRECTIONS = ((1, 0),(0, 0),(0, 1),
#              (0, 2),(0,0), (1, 2),
#              (2, 2),(2, 1),(2, 0),
#                     (0, 0))

class Agent():
    @timing("agent init")
    def __init__(self, **kwargs):
        # kwargs
        self.tk             = kwargs.get('tk',TurningKernel())
        self.DEBUG          = kwargs.get('debug', False) 
        self.MAX_SATURATION = kwargs.get('MAX_SATURATION',20)
        self.MIN_FIDELITY   = kwargs.get('MIN_FIDELITY',60)
        self.MAX_FIDELITY   = kwargs.get('MAX_FIDELITY',100)
        # Default constants
        self.saturation = 0
        self.x = 127
        self.y = 127
        # Random first orientation
        self.direction:int =  np.random.randint(0,4)*90  # in degrees
        if self.DEBUG: print(self.direction)
        self.lost = True

    @timing("agent pos")
    def get_position(self):
        return (self.x, self.y)

    @timing("agent explore")
    def explore(self):
        matrix = self.tk.calc(direction=self.direction)
        if self.DEBUG: print(f"Exploring ({self.direction}):\n{matrix}")
        outcome = hf.roll8(matrix, self.direction)
        if self.DEBUG: print(f"out:{outcome}")
        self.direction = outcome*45
        
        x, y, _, _ = hf.deg2position(self.direction)
        self.x += x 
        self.y += y 

        if self.DEBUG: print(f"I'm going: {self.direction}")
        self.lost = True
        if self.DEBUG: print("++++++++++++++++++++++")

    # TODO: Add second forking algorithm
    @timing("agent forking")
    def forking(self,matrix)->tuple[int,int]:
        ''' 
        This function interprets the forking algorithm that is explicitly 
        defined in the original paper.
        @param nmatrix 3x3 Numpy array representing the normalized strength of 
        nearby pheromone. The graphic below illustrates this matrix 
        0 , 1 , 2
        3 ,>A<, 5
        6 , 7 , 8 

        @return position the position the forking algorithm has chosen to move into
        where -1 means explore
        '''
        
        #NOTE: Case 0: if there is no trails sensed, explore
        if np.sum(matrix) ==0:
            if self.DEBUG: print("Case 0: Explore")
            return (1,1)
        

        #NOTE: Case 1: if there is trail straight ahead, follow it 
        print(self.direction, end=" | ")
        x, y, ind_x, ind_y = hf.deg2position(self.direction)
        print(x,y)
        #FIXME: THIS MAY BE CORRECT BELOW 
        # x, y = DIRECTIONS[(self.direction//45)] 
        if matrix[ind_x,ind_y] > 0:
            if self.DEBUG: print("Case 1: forward")
            return (x,y)
        
        #NOTE: Case 2: if there are two or more trails of ~ the same strength, explore
        
        min_distance = .020
        
        weighted_matrix = matrix * self.tk.calc(self.direction)
        if self.DEBUG: print(f"weighted_matrix:\n{weighted_matrix}")
        # Normalize Matrix
        normalized_matrix = weighted_matrix/weighted_matrix.sum()
        if self.DEBUG: print(f"normalized_matrix:\n{normalized_matrix}")

        flattened = normalized_matrix.ravel()
        flattened = np.nan_to_num(flattened)
        
        sorted_ind = np.argsort(flattened)
        # Extract the three largest values based on sorted indices
        strongest_trails = flattened[sorted_ind[-3:]]
        # Calculate absolute differences between the three largest values
        absolute_differences = np.diff(strongest_trails)
        # Check if all absolute differences are within the minimum distance
        are_within_distance = all(abs(diff) <= min_distance 
                                  for diff in absolute_differences)
        
        if are_within_distance:
            if self.DEBUG: print("Case 2: Determine if there is a fork")
            return (1,1)
        
        #NOTE: Case 3: if neither case above is true, take the 
        # stronger of the options
        
        top2 = flattened[sorted_ind[-2:]]
        ntop2 = top2 / top2.sum()
        choice = hf.flip(ntop2[0])
        
        #NOTE: Using the sorted_ind array since we want the indicies, 
        # not the values

        if self.DEBUG: print("Case 3: Strongest trail")
        print(sorted_ind[-2:])
        if choice:
            return tuple(hf.displacement[sorted_ind[-2]%3][sorted_ind[-1]//3])
        else:
            return tuple(hf.displacement[sorted_ind[-1]%3][sorted_ind[-2]//3])

    @timing("agent update t")
    def update_trail(self,update:bool|None=None):
        if (not self.saturation == 0) or (self.saturation < self.MAX_SATURATION):
            return None
        match update:
            case False:    
                self.saturation -=1
            case True:    
                self.saturation +=1
                
        return None

    @timing("agent update")
    def update(self, pc):
        # using current position, check what is next it, 
        mat = self.get_adj(pc)
        
        # Check if matrix is the correct size, if not, we repair it
        if mat.shape == (2,3) or mat.shape == (3,2):
            if self.DEBUG: print(f"old mat:\n{mat}")
            mat = np.resize(mat, [3,3])
       
        if self.DEBUG: print(f"dir:{self.direction}\nmatrix:\n{mat}")
        
        self.update_trail(mat[1][1]>0)
       
        # staying at the same position is not an option
        mat[1][1] = 0
        fid = hf.saturation_to_fidelity(csat=self.saturation, 
                                max_sat=self.MAX_SATURATION, 
                                min_fid=self.MIN_FIDELITY, )
        
        choice = hf.flip(fid/self.MAX_FIDELITY)
        
        if not choice: 
            self.explore()
            return None

        # Apply weight of pheromone concentrations onto turning kernel 
        weighted_matrix = mat * self.tk.calc(self.direction)
        if self.DEBUG: print(f"weighted_matrix:\n{weighted_matrix}")
        # Normalize Matrix
        normalized_matrix = weighted_matrix/weighted_matrix.sum()
        if self.DEBUG: print(f"normalized_matrix:\n{normalized_matrix}")
        
        outcome:tuple[int,int] = self.forking(normalized_matrix)
        print(f"OUTCOME:{outcome}")
        if outcome == (1,1):
            self.explore()
        else:
            
            self.x += outcome[0]
            self.y += outcome[1]   #tmpr = np.radians(self.direction) 
            #self.x += int(np.round(np.cos(tmpr)))
            #self.y += int(np.round(np.sin(tmpr)))
            #tx,ty = np.where(hf.displacement==outcome)
            tx, ty = np.where(np.logical_and(hf.displacement[:, :, 0] == outcome[0], hf.displacement[:, :, 1] == outcome[1]))
            _dir = hf.DIRECTIONS[tx[0]][ty[0]]
            print(_dir)
            
            self.direction = _dir
            
            if self.DEBUG: print(f"I'm going: {self.direction}")
            self.lost = False
        if self.DEBUG: print("++++++++++++++++++++++")


    @timing("agent lost")
    def is_lost(self,)->bool:
        return self.lost ==True

    @timing("agent getadj")
    def get_adj(self,pheromone): 
        adj_tiles = pheromone[self.x-1:self.x+2,self.y-1:self.y+2]
        return adj_tiles

    @timing("agent reset")
    def reset(self):
        self.saturation = 0
        self.x = 127
        self.y = 127
        self.direction:int =  int(np.random.randint(0,4))*90# in degrees

if __name__ == "__main__":
    pass

