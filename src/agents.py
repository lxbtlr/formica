from enum import Enum
import numpy as np
from model import MAX_FIDELITY
import turningkernel as tk
import helperfunctions as hf
#TODO: Specify what is being imported explicitly

class CardinalDirection(Enum):
    NORTH = (0, 1)
    NORTHEAST = (1, 1)
    EAST = (1, 0)
    SOUTHEAST = (1, -1)
    SOUTH = (0, -1)
    SOUTHWEST = (-1, -1)
    WEST = (-1, 0)
    NORTHWEST = (-1, 1)


class Agent():
    def __init__(self, **kwargs):
        # kwargs
        self.tk             = kwargs.get('tk',tk.TurningKernel())
        self.DEBUG          = kwargs.get('debug', False) 
        self.MAX_SATURATION = kwargs.get('MAX_SATURATION',6)
        self.MIN_FIDELITY   = kwargs.get('MIN_FIDELITY',6)
        # Default constants
        self.saturation = 0
        self.x = 127
        self.y = 127
        # Random first orientation
        self.direction:int =  np.random.randint(0, 9)*45
                                # in degrees
        #FIXME: Create a direction function / class that can be imported across classes
        if self.DEBUG: print(self.direction)
        self.lost = True

    def get_position(self):
        return (self.x, self.y)

    def explore(self):
        matrix = self.tk.calc(direction=self.direction)
        if self.DEBUG: print(f"Exploring ({self.direction}):\n{matrix}")
        outcome = hf.roll8(matrix, self.direction)
        self.x += outcome//3 -1
        self.y -= outcome%3 - 1
        self.direction = DIRECTIONS[outcome%3][outcome//3]
        if self.DEBUG: print(f"I'm going: {self.direction}")
        self.lost = True

    # TODO: Add second forking algorithm
    def forking(self,matrix)->int:
        ''' 
        This function interprets the forking algorithm that is explicitly 
        defined in the original paper.
        @param nmatrix 3x3 Numpy array representing the normalized strength of 
        nearby pheromone. The graphic below illustrates this matrix 
        0 , 1 , 2
        3 ,>A<, 5
        6 , 7 , 8 

        @return position the forking algorithm has chosen to move into
        where -1 means explore
        '''
        
        #NOTE: Case 0: if there is no trails sensed, explore
        if np.sum(matrix) ==0:
            return -1
        

        #NOTE: Case 1: if there is trail straight ahead, follow it

        x, y = hf.deg2position(self.direction)
        if matrix[x][y] > 0:
            return (y*3)+x
        
        #NOTE: Case 2: if there are two or more trails of ~ the same strength, explore
        
        min_distance = .10
        
        weighted_matrix = matrix * self.tk.calc(self.direction)
        if self.DEBUG: print(f"weighted_matrix:\n{weighted_matrix}")
        # Normalize Matrix
        normalized_matrix = weighted_matrix/weighted_matrix.sum()
        if self.DEBUG: print(f"normalized_matrix:\n{normalized_matrix}")

        flattened = normalized_matrix.ravel()
        flattened = np.nan_to_num(flattened)
        
        sorted_ind = np.argsort(flattened)
        # Extract the three smallest values based on sorted indices
        strongest_trails = flattened[sorted_ind[-3:]]
        # Calculate absolute differences between the three smallest values
        absolute_differences = np.diff(strongest_trails)
        # Check if all absolute differences are within the minimum distance
        are_within_distance = all(abs(diff) <= min_distance 
                                  for diff in absolute_differences)
        
        if are_within_distance:
            return -1
        
        #NOTE: Case 3: if neither case above is true, take the 
        # stronger of the options
        
        top2 = flattened[sorted_ind[-2:]]
        ntop2 = top2 / top2.sum()
        choice = hf.flip(ntop2[0])
        
        #HACK: This is a great example of how to NOT use match case statments
        #print(f"NTOP2: {ntop2}\ntop2: {top2}\nchoice: {choice}")
        #match choice:
        #    case True:
        #        # print("path chosen",True, sorted_ind[0])
        #        return sorted_ind[-1]
        #    case False:
        #        # print("path chosen",False, sorted_ind[1])
        #        return sorted_ind[-2]
        #return
        
        #NOTE: Using the sorted_ind array since we want the indicies, 
        # not the values
        if choice:
            return sorted_ind[-2]
        else:
            return sorted_ind[-1]

    def update_trail(self,update:bool|None=None):
        if (not self.saturation == 0) or (self.saturation < MAX_SATURATION):
            return None
        match update:
            case False:    
                self.saturation -=1
            case True:    
                self.saturation +=1
                

    def update(self, pc):
        # using current position, check what is next it, 
        mat = self.get_adj(pc)
        
        # Check if matrix is the correct size, if not, we repair it
        if mat.shape == (2,3) or mat.shape == (3,2):
            if self.DEBUG: print(f"old mat:\n{mat}")
            mat = np.resize(mat, [3,3])
       
        if self.DEBUG: print(f"matrix:\n{mat}")
        
        self.update_trail(mat[1][1]>0)
       
        # staying at the same position is not an option
        mat[1][1] = 0

        choice = hf.flip(hf.saturation_to_fidelity(csat=self.saturation, max_sat=self.MAX_SATURATION, min_fid=self.MIN_FIDELITY, )/MAX_FIDELITY)
        
        if not choice: 
            self.explore()
            return None

        # Apply weight of pheromone concentrations onto turning kernel 
        weighted_matrix = mat * self.tk.calc(self.direction)
        if self.DEBUG: print(f"weighted_matrix:\n{weighted_matrix}")
        # Normalize Matrix
        normalized_matrix = weighted_matrix/weighted_matrix.sum()
        if self.DEBUG: print(f"normalized_matrix:\n{normalized_matrix}")
        
        outcome:int = self.forking(normalized_matrix)
        #print(outcome)
        match outcome:
            case -1:
                self.explore()
            case None:
                print(f"NONE CASE\n{normalized_matrix}\n{weighted_matrix}")
                self.explore()
            case _:        
                # print(outcome)
                self.x += outcome//3 -1
                self.y -= outcome%3 - 1
                self.direction = DIRECTIONS[outcome%3][outcome//3]
                if self.DEBUG: print(f"I'm going: {self.direction}")
                self.lost = False

    def is_lost(self,)->bool:
        return self.lost ==True

    def get_adj(self,pheromone): 
        adj_tiles = pheromone[self.x-1:self.x+2,self.y-1:self.y+2]
        return adj_tiles

    def reset(self):
        self.saturation = 0
        self.x = 127
        self.y = 127
        self.direction:int =  int(np.random.random()*8)*45# in degrees

if __name__ == "__main__":
    pass

