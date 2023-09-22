import pygame
import pygame.freetype
import numpy as np
import sys
import time

class Sim_Window():
    def __init__(self, **kwargs):
        
        # KWARGS 
        self.kernel = kwargs.get('kernel',)
        self.agents = kwargs.get('agents',100)
        self.MIN_FIDELITY = kwargs.get('min_fidelity',0)
        self.MAX_FIDELITY = kwargs.get('MAX_FIDELITY',100)
        self.MAX_PHEROMONE_STRENGTH = kwargs.get('MAX_PHEROMONE_STRENGTH', 3)
        self.max_time = kwargs.get('max_time',1500)
        self.tao = kwargs.get('tao', 10) 
        self.WINDOW_SIZE = kwargs.get('window_size',(400,400))
        self.GRID_SIZE = kwargs.get('grid_size',100)  # Number of squares in each row and column
        
        # Constants
        self.START_TIME = '-'.join(time.ctime().split()[1:4])
        self.SQUARE_SIZE =self.WINDOW_SIZE[0] // self.GRID_SIZE
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        
        # Pygame
        pygame.init() 
        self.font = pygame.freetype.SysFont('Comic Sans MS', 30)
        self.screen = pygame.display.set_mode(self.WINDOW_SIZE)
        pygame.display.set_caption(f"Agent Model") 

    def metrics(self, lost:int, time: int):
        '''
        Draw the metrics of the simulation onto the board.

        @param lost an integer describing how many ants are lost at the current time.
        @param time an integer describing the current time in the simulation
        @return None
        '''
        self.font.render_to(self.screen,(80,40),f"ANTS LOST:{lost}", self.WHITE)
        self.font.render_to(self.screen,(80,80),f"SIM. TIME: {int(time)}", self.WHITE)
        self.font.render_to(self.screen,(80,120),f"Fid. Range: ({self.MIN_FIDELITY}-{self.MAX_FIDELITY}%)", self.WHITE)

    def update(self, pheromone, ant_locs):
        '''
        Update the board with all new values for pheromones and ants on the board.
        
        @param pheromone Numpy array containing the strength of pheromone across the board
        @param ant_locs Nunpy array containing the locations on the 2d array that has ants
        @return None
        '''
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close(True)
                 
        # Clear the screen
        self.screen.fill(self.BLACK)
        # Draw the grid of squares based on the data
        combi = np.stack((pheromone, ant_locs), axis=-1)
        for row_num, combi_row in enumerate(combi):
            for col_num, combi_point in enumerate(combi_row):
                # I could really use a c code like switch case statement right about now
                if np.all(combi_point==0):
                    #NOTE: Case where there is nothing to draw in this location
                    continue 
                
                if combi_point[1]:
                    #NOTE: Case where there is an ant on this space
                    pygame.draw.rect(self.screen, self.WHITE, 
                        (col_num * self.SQUARE_SIZE, row_num * self.SQUARE_SIZE, self.SQUARE_SIZE, self.SQUARE_SIZE))
                    continue
                
                if combi_point[0]:
                    #NOTE: Case where there is no ant on this location, and only pheromone
                    data_value = combi_point[0]
                    
                    if data_value >= 255:
                        data_value = 255
                    color = (data_value, 0, 0, data_value)
                    pygame.draw.rect(self.screen, color, 
                        (col_num * self.SQUARE_SIZE, row_num * self.SQUARE_SIZE, self.SQUARE_SIZE, self.SQUARE_SIZE))
         
        # Update the display
        pygame.display.flip()
    
    def updatePheromone(self,pheromone_c, x,y):

        #NOTE: update pheromone trails
        for _x,_y in zip(x, y):
            
            if pheromone_c[_x][_y] >= self.tao*self.MAX_PHEROMONE_STRENGTH:
                pheromone_c[_x][_y] = self.tao*self.MAX_PHEROMONE_STRENGTH
            else:
                pheromone_c[_x][_y] += self.tao

        # pheromone_concentration[xtmp][ytmp] = tao
        #NOTE: decrement all pheromone trails
        pheromone_c  -= 1
        #NOTE: prevent any negative values
        pheromone_concentration = np.maximum(pheromone_c,0)
        return pheromone_concentration

    def close(self, prg=True):
        '''
        Closes the simulation and possibly the program 
        
        @param prg boolean value to determine whether we close the whole program 
                   in addition to the simulation window
        @return None
        '''
        # Quit Pygame
        pygame.quit()
        if prg: sys.exit()

    def save_to_disc(self, imgdir=None, extra:str|None=None):
        '''
        Write state of pygame simulation to img/ directory
        @param imgdir The subdirectory for images to be saved to, 
                      this is very helpful when making gifs
        @param extra Allows the user to add an extra string to the end of the 
                     image filename  
        @return None
        '''
        if extra is None:
            name = f"{self.START_TIME}-{self.kernel}-{self.agents}-{self.max_time}-{self.tao}.jpg"
        else:
            name = f"{self.START_TIME}-{self.kernel}-{self.agents}-{self.max_time}-{self.tao}-{extra}.jpg"
        if imgdir == "":
            pygame.image.save(self.screen, f"img/{name}") 
        else:
            pygame.image.save(self.screen, f"img/{imgdir}/{name}") 

if __name__ == "__main__":
    pass
