import random
from constants import *

class Animal:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alive = True

    def get_surrounding(self, wonderland):
        # check if up down left right has empty cell, if so, move to that cell
        surroundings = [
            ((self.x - 1) % N, self.y),
            ((self.x + 1) % N, self.y),
            (self.x, (self.y - 1) % N),
            (self.x, (self.y + 1) % N),
        ]
        
        occupied_locations = wonderland.get_occupied_locations()
        to_remove = []
        for surrounding in surroundings:
            if surrounding in occupied_locations:
                to_remove.append(surrounding)

        for surrounding in to_remove:
            surroundings.remove(surrounding)

        random.shuffle(surroundings)
        return surroundings
    
    def _move_to(self, new_x, new_y):

        self.x = new_x
        self.y = new_y
'''
A prey moves randomly, once it stays alive for a certain number of steps, it reproduces
once it reaches a certain age, it dies
'''
class Prey(Animal):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = PREY
        self.age = 0

    # a prey moves randomly
    def move(self, wonderland):
        
        # check if up down left right has empty cell, if so, move to that cell
        empty_surrounding = self.get_surrounding(wonderland)
        if len(empty_surrounding) > 0:
            new_x, new_y = empty_surrounding[0]
            self._move_to(new_x, new_y)
        
        # cannot move, die
        else:
            self.alive = False
            
        # check if it can reproduce
        self.reproduce(wonderland)
        self.grow()

        
    def reproduce(self, wonderland):
        # when it reaches a certain age, it reproduces

        if self.age > PREY_STEPS_TO_REPRODUCE and self.age % PREY_STEPS_TO_REPRODUCE == 0 and self.alive:
            # check if there is an empty cell around
            empty_surrounding = self.get_surrounding(wonderland)
            if len(empty_surrounding) > 0:
                baby_x, baby_y = empty_surrounding[0]
                wonderland.preys.append(Prey(baby_x, baby_y))


    def grow(self):
        # a prey lives for a certain number of steps, then it dies
        self.age += 1
        if self.age > PREY_MAX_AGE and self.alive:
            self.alive = False


'''
A predator already hunts around its location, if it can find a prey, it moves to that location and eat it
if it cannot find a prey, it moves randomly
once it eats enough preys, it reproduces
'''    
class Predator(Animal):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = PREDATOR
        self.energy = PREDATOR_INITIAL_ENERGY

    # a predator moves randomly, but it prefers to move to a cell occupied by a prey and eat it
    def move(self, wonderland):
        
        # if hunt successfully, it moved already
        if self.hunt(wonderland):
            # check if it can reproduce
            self.reproduce(wonderland)
            return
        
        empty_surrounding = self.get_surrounding(wonderland)
        if len(empty_surrounding) > 0:
            self._move_to(empty_surrounding[0][0], empty_surrounding[0][1])                
            # once it move to a new location, its energy decreases
            self.energy -= 1   
            if self.energy <= 0:
                self.alive = False

            # check if it can reproduce
            self.reproduce(wonderland)

        else:
            self.alive = False
    
    def hunt(self, wonderland):
        # check around to see if there is a prey, if so, eat it
        for i in range(-1, 2):
            for j in range(-1, 2):
                for prey in wonderland.preys:
                    
                    if (self.x + i) % N == prey.x and (self.y + j) % N == prey.y:

                        self._move_to(prey.x, prey.y)
                        prey.alive = False
                        self.energy += PREDATOR_GAIN_FROM_EATING
                        
                        return True
        return False
                    
    def reproduce(self, wonderland):
        # when it reaches a certain age, it reproduces

        if self.energy >= PREDATOR_ENERGY_TO_REPRODUCE * 2 and self.alive:
            # check if there is an empty cell around
            empty_surrounding = self.get_surrounding(wonderland)
            if len(empty_surrounding) > 0:
                baby_x, baby_y = empty_surrounding[0]
                wonderland.predators.append(Predator(baby_x, baby_y))

           
        
            