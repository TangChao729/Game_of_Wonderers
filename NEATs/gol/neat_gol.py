# TODO: 
'''
Make predator born in random direction
Make a square box predator can't get in
Refine antenna detection
Refactor game mode
'''

from neat_constants import *
from neat_animal import Predator, Prey, SimulationStats

import math
import random
import sys
import neat
import os

import matplotlib.pyplot as plt

os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame
pygame.init()

global current_generation
current_generation = 0


class GameOfLife:
    def __init__(self, screen_size, dummy=False):

        
        self.screen_size = screen_size
        self.screen = pygame.display.set_mode([self.screen_size, self.screen_size])
        self.preys = []
        self.predators = []

    def add_predator(self, predator_image, initial_x, initial_y, direction, velocity):
        new_predator = Predator(predator_image, initial_x, initial_y, direction, velocity)
        self.predators.append(new_predator)
        return new_predator

    def add_prey(self, prey_image, initial_x, initial_y, direction, velocity):
        new_prey = Prey(prey_image, initial_x, initial_y, direction, velocity)
        self.preys.append(new_prey)
        return new_prey
        
    def run_simulation(self, genomes, config):

        

    #     # Empty Collections For Nets and Cars
        nets = [] # neural networks, the brains
        self.preys = []
        self.predators = []

        safe_zone = (200, 600, 200, 600)

        # initial prey and predator
        
        for i, g in genomes:

            initial_x = random.randint(0, self.screen_size)
            initial_y = random.randint(0, self.screen_size)
            # random generate position inside of safe zone
            while initial_x not in range(*safe_zone[:2]) or initial_y not in range(*safe_zone[2:]):
                initial_x = random.randint(0, self.screen_size)
                initial_y = random.randint(0, self.screen_size)

            net = neat.nn.FeedForwardNetwork.create(g, config)
            nets.append(net)
            g.fitness = 0
            self.add_prey(prey_rescaled_image,
                            initial_x=initial_x,
                            initial_y=initial_y, 
                            direction=random.randint(0, 360), 
                            velocity=0.0)

        

        for i in range(20):
            initial_x = random.randint(0, self.screen_size)
            initial_y = random.randint(0, self.screen_size)
            # random generate position outside of safe zone
            while initial_x in range(*safe_zone[:2]) and initial_y in range(*safe_zone[2:]):
                initial_x = random.randint(0, self.screen_size)
                initial_y = random.randint(0, self.screen_size)


            self.add_predator(predator_rescaled_image,
                            initial_x=initial_x,
                            initial_y=initial_y,
                            direction=random.randint(0, 360), 
                            velocity=0.0)

        # Clock Settings
        # Font Settings & Loading Map   
        clock = pygame.time.Clock()
        

        global current_generation
        current_generation += 1

        counter = 0

        running = True
        while running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            for i, prey in enumerate(self.preys):
                # Calculate Inputs
                inputs = prey.sense()
                # Calculate Outputs
                output = nets[i].activate(inputs)
                # Take Action
                prey.act(output)

            for predator in self.predators:
                
                action = [random.randint(0, 1) for _ in range(4)]
                predator.act(action)

            self.update()
            
            still_alive = 0

            for i, prey in enumerate(self.preys):
                if prey.alive:
                    still_alive += 1
                    genomes[i][1].fitness += prey.velocity / 50.0

            if still_alive == 0:
                break

            counter += 1
            if counter == 600:
                break

            self.draw()

            # Display Info
            generation_font = pygame.font.SysFont("Arial", 30)
            text = generation_font.render("Generation: " + str(current_generation), True, (255,255,255))
            text_rect = text.get_rect()
            text_rect.center = (100, 100)
            screen.blit(text, text_rect)

            alive_font = pygame.font.SysFont("Arial", 20)
            text = alive_font.render("Still Alive: " + str(still_alive), True, (255, 255, 255))
            text_rect = text.get_rect()
            text_rect.center = (100, 200)
            screen.blit(text, text_rect)

            # show time left this round
            time_font = pygame.font.SysFont("Arial", 20)
            text = time_font.render("Time Left: " + str(int((1200-counter)/60)), True, (255, 255, 255))
            text_rect = text.get_rect()
            text_rect.center = (100, 300)
            screen.blit(text, text_rect)


            pygame.display.flip()
            # pygame.time.Clock().tick(60)

            keys = pygame.key.get_pressed()
            if keys[pygame.K_k]:
                pygame.quit()

        fitnesses = []
        for i, g in genomes:
            # debug print
            fitnesses.append(g.fitness)
            
        avg_fitness = sum(fitnesses) / (len(fitnesses) + 1e-10)
        max_fitness = max(fitnesses)

        # Append stats to the container
        global stats_container
        stats_container.avg_fitnesses.append(avg_fitness)
        stats_container.max_fitnesses.append(max_fitness)

        # check container data
        print(f"Average fitnesses: {stats_container.avg_fitnesses}")
        print(f"Max fitnesses: {stats_container.max_fitnesses}")

        # Update plot data
        line1.set_xdata(range(len(stats_container.avg_fitnesses)))
        line1.set_ydata(stats_container.avg_fitnesses)

        line2.set_xdata(range(len(stats_container.avg_fitnesses)))
        line2.set_ydata(stats_container.max_fitnesses)


        # Adjust plot limits
        ax1.relim()
        ax1.autoscale_view()

        # Redraw the plot
        fig.canvas.draw()
        fig.canvas.flush_events()

                
    def run(self, 
            auto_control_prey_num = 2,
            auto_control_predator_num = 10,
            auto_control_prey_move = True,
            auto_control_predator_move = True,):
        # safe zone, a square area in the middle of the screen
        safe_zone = (200, 600, 200, 600)

        # initial prey and predator
        self.preys = []
        manual_control_prey = self.add_prey(prey_rescaled_image, 
                                            initial_x=self.screen_size // 2, 
                                            initial_y=self.screen_size // 2, 
                                            direction=0, 
                                            velocity=0.0)
        
        
        for i in range(auto_control_prey_num):
            initial_x = random.randint(0, self.screen_size)
            initial_y = random.randint(0, self.screen_size)
            # random generate position inside of safe zone
            while initial_x not in range(*safe_zone[:2]) or initial_y not in range(*safe_zone[2:]):
                initial_x = random.randint(0, self.screen_size)
                initial_y = random.randint(0, self.screen_size)
            auto_control_prey = self.add_prey(prey_rescaled_image,
                                            initial_x=initial_x,
                                            initial_y=initial_y, 
                                            direction=random.randint(0, 360), 
                                            velocity=0.0)

        

        for i in range(auto_control_predator_num):
            initial_x = random.randint(0, self.screen_size)
            initial_y = random.randint(0, self.screen_size)
            # random generate position outside of safe zone
            while initial_x in range(*safe_zone[:2]) and initial_y in range(*safe_zone[2:]):
                initial_x = random.randint(0, self.screen_size)
                initial_y = random.randint(0, self.screen_size)


            self.add_predator(predator_rescaled_image,
                            initial_x=initial_x,
                            initial_y=initial_y,
                            direction=random.randint(0, 360), 
                            velocity=0.0)

        running = True
        while running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            keys = pygame.key.get_pressed()
            # control the prey
            for prey in self.preys:
                if prey == manual_control_prey:
                    action = [0, 0, 0, 0]
                    if keys[pygame.K_UP]:
                        action[0] = 1
                    if keys[pygame.K_DOWN]:
                        action[1] = 1
                    if keys[pygame.K_LEFT]:
                        action[2] = 1
                    if keys[pygame.K_RIGHT]:
                        action[3] = 1
                    prey.act(action)
                    # print(prey.sense())
                else:
                    if auto_control_prey_move:
                        action = [random.randint(0, 1) for _ in range(4)]
                        prey.act(action)

            if keys[pygame.K_SPACE]:
                if manual_control_prey not in self.preys:
                    self.preys.append(manual_control_prey)
                    manual_control_prey.reset()
            
            # control the predator
            for predator in self.predators:
                if auto_control_predator_move:
                    action = [random.randint(0, 1) for _ in range(4)]
                    predator.act(action)

            self.update() 
            self.draw()

            pygame.display.flip()
            pygame.time.Clock().tick(60)

        pygame.quit()
        sys.exit()

    def sensor_demo(self, 
            auto_control_prey_num = 1,
            auto_control_predator_num = 1,
            auto_control_prey_move = True,
            auto_control_predator_move = True):

        # initial prey and predator
        self.preys = []
        
        
        for i in range(auto_control_prey_num):
            initial_x = self.screen_size // 2
            initial_y = self.screen_size // 2

            auto_control_prey = self.add_prey(prey_rescaled_image,
                                            initial_x=initial_x,
                                            initial_y=initial_y, 
                                            direction=0, 
                                            velocity=0.0)

        

        for i in range(auto_control_predator_num):
            initial_x = self.screen_size // 2 + 150
            initial_y = self.screen_size // 2

            self.add_predator(predator_rescaled_image,
                            initial_x=initial_x,
                            initial_y=initial_y,
                            direction=-90, 
                            velocity=2.0)

        running = True
        while running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            keys = pygame.key.get_pressed()
            
            # control the predator
            for predator in self.predators:
                if auto_control_predator_move:
                    predator.circle()
            
            for prey in self.preys:
                print(prey.sense())
            

            self.update() 
            self.draw()
            
            pygame.display.flip()
            pygame.time.Clock().tick(20)

        pygame.quit()
        sys.exit()


    def update(self):
        self.check_collision()
        self.check_alive()

    def check_collision(self):
        for prey in self.preys:
            prey.update_antenna(self.predators)
            for predator in self.predators:
                if prey.check_collision(predator):
                    prey.on_collision(predator)  # die
                    predator.on_collision(prey)  # gain energy
   
    def check_alive(self):
        self.preys = [prey for prey in self.preys if prey.alive]
        self.predators = [predator for predator in self.predators if predator.alive and predator.energy > 0]


    def draw(self):
        self.screen.fill((0, 0, 0))  # Clear the screen

        for predator in self.predators:
            predator.draw(self.screen)

        for prey in self.preys:
            prey.draw(self.screen)

        self.show_life_count()
        # self.show_energy_count()
        # self.show_sensor(self.preys[0].sense())

    def show_life_count(self):
        font = pygame.font.SysFont("Arial", 20)
        text = font.render(f"Preys: {len(self.preys)} Predators: {len(self.predators)}", True, (255, 255, 255))
        self.screen.blit(text, (10, 10))

    def show_energy_count(self):
        font = pygame.font.SysFont("Arial", 20)
        text = font.render("Energy: " + str(self.the_predator.energy), True, (255, 255, 255))
        self.screen.blit(text, (50, 30))

    def show_sensor(self, sense):
        # Formatting each distance to have a width of 3 characters
        formatted_distances = [f"{(179 - dis):3}" for dis in sense]

        font = pygame.font.SysFont("Arial", 15)
        # Joining the formatted distances into a single string
        text = font.render("Sensor: " + ' '.join(formatted_distances), True, (255, 255, 255))
        self.screen.blit(text, (10, 30))


if __name__ == '__main__':

    # check if run with command line argument
    # if run with command line argument, "-m" means manual control, run()
    # if "-t" else run_simulation()

    game = GameOfLife(SCREEN_SIZE)

    if len(sys.argv) > 1:

        if sys.argv[1] == "-m":
            # setting
            
            game.run(auto_control_prey_num = 10,
                    auto_control_predator_num = 10,
                    auto_control_prey_move = True,
                    auto_control_predator_move = True)

        elif sys.argv[1] == "-d":

            game.sensor_demo(auto_control_prey_num = 1,
                    auto_control_predator_num = 1,
                    auto_control_prey_move = True,
                    auto_control_predator_move = True)

        elif sys.argv[1] == "-t":
            # Turn on interactive mode
            plt.ion()

            # Create figure and axis
            fig, ax1 = plt.subplots()


            # Set up lines for updating
            line1, = ax1.plot([], [], 'g-', label='Average Fitness')  # For average fitness
            line2, = ax1.plot([], [], 'b-', label='Max Fitness')  # For average live time
            
            # Adding legends
            ax1.legend(loc='upper left')


            plt.show()

            # Initialize it before running the simulation
            stats_container = SimulationStats()
            # starting NEAT training
            # Load Config
            config_path = "./config.txt"
            config = neat.config.Config(neat.DefaultGenome,
                                        neat.DefaultReproduction,
                                        neat.DefaultSpeciesSet,
                                        neat.DefaultStagnation,
                                        config_path)
            
            # Create Population And Add Reporters
            population = neat.Population(config)
            population.add_reporter(neat.StdOutReporter(True))
            stats = neat.StatisticsReporter()
            population.add_reporter(stats)
            # def run_simulation_wrapper(genomes, config):
            #     game.run_simulation(genomes, config)

            population.run(game.run_simulation, 100)

            

            
        else:
            print("Invalid command line argument. Use '-m' for manual control or '-t' for test mode.")