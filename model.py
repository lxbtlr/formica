import numpy as np
import multiprocessing
import argparse as ap
import sys
import pygame
from os import getcwd
import time


# NOTE: handle argparsing
parser = ap.ArgumentParser(description="A script to generate an agent based model simulating paths generated by ants and their pheromone trails")

parser.add_argument("--agents", default=100, type=int, help="Max number of concurrent agents in the model")
parser.add_argument("--kernel", type=str, help="Selected turning kernel")
parser.add_argument("--max-time", default=1000, type=int, help="Max simulation time our model will run")
parser.add_argument("--multi", default=True, type=bool, help="Toggle Multiprocess (on by default)")
parser.add_argument("--tao", default=10, type=int, help="Max trail length")
args = parser.parse_args()


# NOTE: this is serving as a preamble of init classes / importing parameters

DEBUG = False
PWD = getcwd()
MAX_FIDELITY:float = 100
MIN_FIDELITY:float = 80
MAX_SATURATION:int = 20
MAX_PHEROMONE_STRENGTH:int = 4
MULTIPROCESS = True


tao = args.tao
agents = args.agents
max_time = args.max_time
print(f"Starting model:\ntao: {tao}\nagents: {agents}\nmat time: {max_time}")


board = np.zeros((255,255))
DIRECTIONS= np.array([[315, 0, 45],[270, -1, 90],[225, 180,135]])
#DIRECTIONS= [[45, 0, 315],[90, -1, 270],[135, 180,225]]

def deg2position(degrees):
    # Convert degrees to radians using NumPy
    ind = np.where(DIRECTIONS == degrees)
    x,y = ind
    return x[0], y[0]

class TurningKernel():
    # making a class for turning kernels to act as a template we can alter later
    def __init__(self, values:list[list[float]]=[[.1,.3,.1],[.1,0,.1],[.1,.1,.1]])->None:
        # loading weights
        self.turningKernel = np.array(values)
        
    def calc(self,direction:int):
        num90s = direction//90
        tmp = np.rot90(self.turningKernel.copy(),k=num90s)
        if (direction - 90*num90s) //45:
            tmp = rot45(tmp)
        return tmp

class Agent():
    def __init__(self,
                 tk:TurningKernel = TurningKernel()):
        self.saturation = 0
        self.x = 127
        self.y = 127
        self.direction:int =  int(np.random.random()*8)*45# in degrees
        if DEBUG: print(self.direction)
        self.ontrail = False
        self.tk= tk

    def get_position(self):
        return (self.x, self.y)

    def explore(self):
        matrix = self.tk.calc(direction=self.direction)
        if DEBUG: print(f"Exploring ({self.direction}):\n{matrix}")
        outcome = roll(matrix, self.direction)
        self.x += outcome//3 -1
        self.y -= outcome%3 - 1
        self.direction = DIRECTIONS[outcome%3][outcome//3]
        if DEBUG: print(f"I'm going: {self.direction}")

    def update_trail(self,update:bool|None=None):
        if not update is None:
            self.ontrail = update
            
        match self.ontrail:
            case False:    
                if self.saturation == 0:
                    pass
                else:
                    self.saturation -=1
            case True:    
                if self.saturation < MAX_SATURATION: 
                    self.saturation +=1
                else:
                    pass
                


        pass

    def update(self, pc):
        # using current position, check what is next it, 
        # TODO: reorganize this pattern of logical checks
        mat = self.get_adj(pc)
        
        if mat.shape == (2,3) or mat.shape == (3,2):
            if DEBUG: print(f"old mat:\n{mat}")
            mat = np.resize(mat, [3,3])
       
        if DEBUG: print(f"matrix:\n{mat}")
        # case where there is no pheromone adj
        
        self.ontrail = mat[1][1]>0
        self.update_trail()

        # staying at the same position is not an option
        mat[1][1] = 0
        fidelity = saturation_to_fidelity(self.saturation)
        if not np.sum(mat)> 0:
            if DEBUG: print(f"np.sum(mat): {np.sum(mat)}")
            self.explore()
        elif flip(fidelity / MAX_FIDELITY):
            # Apply weight of pheromone concentrations onto turning kernel 
            weighted_matrix = mat * self.tk.calc(self.direction)
            if DEBUG: print(f"weighted_matrix:\n{weighted_matrix}")
            # Normalize Matrix
            normalized_matrix = weighted_matrix/weighted_matrix.sum()
            if DEBUG: print(f"normalized_matrix:\n{normalized_matrix}")
            outcome = roll(normalized_matrix, self.direction)
            self.x += outcome//3 -1
            self.y -= outcome%3 - 1
            self.direction = DIRECTIONS[outcome%3][outcome//3]
            if DEBUG: print(f"I'm going: {self.direction}")
        else:
            self.explore()
            return None

    def get_adj(self,pheromone): 
        adj_tiles = pheromone[self.x-1:self.x+2,self.y-1:self.y+2]
        return adj_tiles

    def reset(self):
        self.saturation = 0
        self.x = 127
        self.y = 127
        self.direction:int =  int(np.random.random()*8)*45# in degrees
        self.ontrail = False


def rot45(matrix, direction="left"):
    if matrix.shape[0] != matrix.shape[1]:
        raise ValueError("Input matrix must be square (n x n)")
    n = matrix.shape[0]
    shifted_matrix = np.copy(matrix)
    if direction == "right":
        # Shift the top row to the right
        shifted_matrix[0, 1:] = matrix[0, :-1]
        # Shift the right column down
        shifted_matrix[1:, -1] = matrix[:-1, -1]
        # Shift the bottom row to the left
        shifted_matrix[-1, :-1] = matrix[-1, 1:]
        # Shift the left column up
        shifted_matrix[:-1, 0] = matrix[1:, 0]
    elif direction == "left":
        # Shift the top row to the left
        shifted_matrix[0, :-1] = matrix[0, 1:]
        # Shift the left column down
        shifted_matrix[1:, 0] = matrix[:-1, 0]
        # Shift the bottom row to the right
        shifted_matrix[-1, 1:] = matrix[-1, :-1]
        # Shift the right column up
        shifted_matrix[:-1, -1] = matrix[1:, -1]
    else:
        raise ValueError("Direction must be 'left' or 'right'")

    return shifted_matrix

def flip(p_true:float)->bool:
    if p_true > 1 or p_true < 0:
        raise ValueError(f"probability true must be in range [0,1]\np={p_true}")
    return np.random.random()<p_true

def roll(nmatrix, direction)->int:
    ''' 
    0 , 1 , 2
    3 , 4 , 5
    6 , 7 , 8 
    '''
    flat = nmatrix.ravel()
    flat = np.nan_to_num(flat)
    if flat[np.argpartition(flat,-2)[-2:]].sum() > .7:
        #branches = np.count_nonzero(flat==np.max(flat))
        #if branches>2:
        #print(branches)
        x,y  = deg2position(direction)
        outcome:int = int(x + y*3)
    else:
        if flat.sum() == 0: 
            flat[1] = 1 
        outcome:int = int(np.random.choice(range(0,9),1,p=flat))
    return outcome

def saturation_to_fidelity( sat:int )->float:
    # NOTE: this method maps the saturation value to fidelity
    
    # Calculate the percentage of input value within the input range
    input_percentage = sat / MAX_SATURATION
    
    # Map the input percentage to the output range
    mapped_value = MIN_FIDELITY + (input_percentage * (MAX_FIDELITY - MIN_FIDELITY))
    if mapped_value > MAX_FIDELITY: mapped_value = MAX_FIDELITY
    return mapped_value


class Sim_Window():
    def __init__(self, wSize=(400, 400), gridSize:int=100, ):

        # Initialize Pygame
        pygame.init()
        # Constants
        self.WINDOW_SIZE = wSize
        self.GRID_SIZE = gridSize  # Number of squares in each row and column
        self.SQUARE_SIZE =self.WINDOW_SIZE[0] // self.GRID_SIZE
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.screen = pygame.display.set_mode(self.WINDOW_SIZE)
        pygame.display.set_caption(f"Agent Model (n={agents})") 
        # Main loop
        self.running = True

    def update(self, pheromone, agents):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
     
        # Clear the screen
        self.screen.fill(self.BLACK)
     
        # Draw the grid of squares based on the data
        for row in range(self.GRID_SIZE):
            for col in range(self.GRID_SIZE):
                if nboard[row][col]:
                    pygame.draw.rect(self.screen, self.WHITE, (col * self.SQUARE_SIZE, row * self.SQUARE_SIZE, self.SQUARE_SIZE, self.SQUARE_SIZE))
                    continue
                
                data_value = pheromone[row][col]
                
                if data_value >= 255:
                    data_value = 255
                color = (data_value, 0, 0, data_value)
                pygame.draw.rect(self.screen, color, (col * self.SQUARE_SIZE, row * self.SQUARE_SIZE, self.SQUARE_SIZE, self.SQUARE_SIZE))
         
        # Update the display
        pygame.display.flip()
    
    def close(self):
        # Quit Pygame
        pygame.quit()
        sys.exit()

    def save_to_disc(self):
        name = f"{'-'.join(time.ctime().split()[1:4])}-{TK}-{agents}-{max_time}-{tao}.jpg"
        pygame.image.save(self.screen, f"img/{name}") 

def split_list(long_list:list, chunk_size:int)->list[list]:
    if not (len(long_list) >6):
        return [long_list]
    return [long_list[i:i + chunk_size] for i in range(0, len(long_list), chunk_size)]

def updatePheromone(pheromone_c, x,y):

    #NOTE: update pheromone trails
    for _x,_y in zip(x, y):
        
        if pheromone_c[_x][_y] >= tao*MAX_PHEROMONE_STRENGTH:
            pheromone_c[_x][_y] = tao*MAX_PHEROMONE_STRENGTH
        else:
            pheromone_c[_x][_y] += tao

    # pheromone_concentration[xtmp][ytmp] = tao
    #NOTE: decrement all pheromone trails
    pheromone_c  -= 1
    #NOTE: prevent any negative values
    pheromone_concentration = np.maximum(pheromone_c,0)
    return pheromone_concentration

def process_section(section_agents:list[Agent])->tuple[list[Agent],list[int],list[int]]:
    _ytmp = []
    _xtmp = []
    for ant in section_agents:
        
        _x,_y = ant.get_position()
        if _x < 1 or _x>len(board)-2 or _y <1 or _y > len(board)-2:
            ant.reset()
            _x,_y = ant.get_position()
        _xtmp.append(_x) 
        _ytmp.append(_y)
        ant.update(pheromone_concentration)

    return (section_agents, _xtmp, _ytmp)

if __name__ == "__main__":
    # main program loop
    sim = Sim_Window(wSize=np.multiply(board.shape,4),
                     gridSize=len(board))

    wide_tk = TurningKernel(
            values=[[.18,.18,.18],
                    [.18,0,.18],
                    [.05,0,.05]])
    narrow_tk = TurningKernel(
            values=[[.25,.3,.25],
                    [.1,0,.1],
                    [.0,0,.0]])
    flat_tk = TurningKernel()
   
    #NOTE: Setting up multiprocessing
    
    processes = 6

    #############
    match args.kernel:
        case "flat":
            TK = flat_tk
        case "narrow":
            TK = narrow_tk
        case "wide":
            TK = wide_tk
        case _:
            TK = TurningKernel()
    # all_agents = np.array([Agent(tk=narrow_tk) for i in range(agents) ])
    all_agents:list[Agent] = []
    #all pheromones exist on their own board
    pheromone_concentration = board.copy()

    epoch = np.arange(start=0.0, stop=max_time, step=1.0) 
    #NOTE: this will serve as our update loop. 
    for ctime in epoch:
        # Every cycle of our model is updated from within this loop
        if len(all_agents) < agents:
            
            all_agents.append(Agent(tk=TK))
        
        
        nboard = board.copy()
        # NOTE: if more than 6 ants start multiprocessing
        if len(all_agents)>6 and MULTIPROCESS:
            list_chunks = list(split_list(all_agents,processes))
            with multiprocessing.Pool(processes=processes) as pool:
            # Perform computations on each chunk in parallel
                r = pool.map(process_section, list_chunks)
                
                results:list[Agent]       = [f for t in r for f in t[0]]
                xtmp:list[int]            = [f for t in r for f in t[1]]
                ytmp:list[int]            = [f for t in r for f in t[2]]
                # Flatten the results list
            # Update the original list with the processed results
            
            nboard[xtmp,ytmp] = 1
            all_agents = results
            pheromone_concentration = updatePheromone(pheromone_concentration, xtmp, ytmp)
        else:
            # update all ants
            xtmp = [] 
            ytmp = []
            for ant in all_agents:
                _x,_y = ant.get_position()
                if _x < 1 or _x>len(board)-2 or _y <1 or _y > len(board)-2:
                    ant.reset()
                    _x,_y = ant.get_position()
                xtmp.append(_x) 
                ytmp.append(_y)
                nboard[_x][_y] = 1
                ant.update(pheromone_concentration)
        #print(f"xtmp:{xtmp}\nytmp:{ytmp}") 
        pheromone_concentration =  updatePheromone(pheromone_concentration, xtmp, ytmp)
        sim.update(np.multiply(pheromone_concentration, 255//tao), nboard)
        print(f"time:\t\t{ctime}") 

    sim.save_to_disc()
    sim.close() 
