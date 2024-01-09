import numpy as np
import random

from constants import *
from classes.class_animal import Prey, Predator

class Map:
    def __init__(self, size):
        self.size = size
        self.grid = np.zeros((size, size), dtype=int)
        self.predators = []
        self.preys = []

    def get_occupied_locations(self):
        return list(set(self.get_prey_locations() + self.get_predator_locations()))

    def get_prey_locations(self):
        return [(prey.x, prey.y) for prey in self.preys]

    def get_predator_locations(self):
        return [(predator.x, predator.y) for predator in self.predators]
    
    # def update_grid(self, )

    def add_animal(self, num_animal):
        for i in range(num_animal):
            # use while loop to find a random location that is not occupied, max N^2 times
            attempt = 0
            while attempt < self.size**2 - len(self.predators) - len(self.preys):
                x = random.randint(0, N-1)
                y = random.randint(0, N-1)
                if (x, y) not in self.get_occupied_locations():
                    self.preys.append(Prey(x, y))
                    break
                attempt += 1
        return 

    def add_predator(self, num_predator):
        for i in range(num_predator):
            # use while loop to find a random location that is not occupied, max N^2 times
            attempt = 0
            while attempt < self.size**2 - len(self.predators) - len(self.preys):
                x = random.randint(0, N-1)
                y = random.randint(0, N-1)
                if (x, y) not in self.get_occupied_locations():
                    self.predators.append(Predator(x, y))
                    break
                attempt += 1
        return    

    def update_grid(self):
        # check alive status
        prey_to_remove = []
        for prey in self.preys:
            if not prey.alive:
                prey_to_remove.append(prey)

        # remove dead prey
        for prey in prey_to_remove:
            self.preys.remove(prey)
        
        # check alive status
        predator_to_remove = []
        for predator in self.predators:
            if not predator.alive:
                predator_to_remove.append(predator)

        # remove dead predator
        for predator in predator_to_remove:
            self.predators.remove(predator)

        # update grid
        self.grid = np.zeros((self.size, self.size), dtype=int)
        for prey in self.preys:
            self.grid[prey.x, prey.y] = PREY
        for predator in self.predators:
            self.grid[predator.x, predator.y] = PREDATOR

        return