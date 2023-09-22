import pygame
import pygame.freetype
import numpy as np
import sys
import time

from model import MAX_FIDELITY, START_TIME

class Sim_Window():
    def __init__(self, wSize=(400, 400), gridSize:int=100, ):

        # Initialize Pygame
        pygame.init()
        # Constants
        self.START_TIME = '-'.join(time.ctime().split()[1:4])
        self.WINDOW_SIZE = wSize
        self.GRID_SIZE = gridSize  # Number of squares in each row and column
        self.SQUARE_SIZE =self.WINDOW_SIZE[0] // self.GRID_SIZE
        self.font = pygame.freetype.SysFont('Comic Sans MS', 30)
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.screen = pygame.display.set_mode(self.WINDOW_SIZE)
        pygame.display.set_caption(f"Agent Model") 
        # Main loop
        self.running = True

    def set_constants(self, tao, max_time, kernel, agents, min_fidelity, max_fidelity):
        
        #FIXME: move to using kwards in the init function
        self.kernel = kernel
        self.agents = agents
        self.MIN_FIDELITY = min_fidelity
        self.MAX_FIDELITY = MAX_FIDELITY
        self.max_time = max_time
        self.tao = tao
        pass


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
        pass

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



