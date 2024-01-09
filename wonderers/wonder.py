import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.colors as mcolors
#Import os Library
import os

#print the current process id
print (os.getpid())

from constants import *
from classes.class_map import Map

# Update Function for Animation
def update(frameNum, board, wonderland, prey_text, predator_text):
    for prey in wonderland.preys:
        if prey.alive:
            prey.move(wonderland)

    for predator in wonderland.predators:
        if predator.alive:
            predator.move(wonderland)

    wonderland.update_grid()

    board.set_data(wonderland.grid)

    # Update text annotations
    prey_text.set_text(f'Prey: {len([prey for prey in wonderland.preys if prey.alive])}')
    predator_text.set_text(f'Predator: {len([predator for predator in wonderland.predators if predator.alive])}')

    return board, prey_text, predator_text

# Initialize Map
def start():
    wonderland = Map(N)
    wonderland.add_animal(NUM_PREYS)
    wonderland.add_predator(NUM_PREDATORS)
    wonderland.update_grid()

    # Define Custom Colormap
    cmap = mcolors.ListedColormap(['black', 'white', 'red']) 

    # Set up plot
    fig, ax = plt.subplots()
    board = ax.imshow(wonderland.grid, interpolation='nearest', cmap=cmap, vmin=0, vmax=2)

    # Initialize Text Annotations
    prey_text = ax.text(1.02, 0.5, f'Prey: {NUM_PREYS}', transform=ax.transAxes)
    predator_text = ax.text(1.02, 0.6, f'Predator: {NUM_PREDATORS}', transform=ax.transAxes)

    # Animation
    ani = animation.FuncAnimation(fig, update, fargs=(board, wonderland, prey_text, predator_text), frames=60)
    plt.show()

if __name__ == '__main__':
    start()