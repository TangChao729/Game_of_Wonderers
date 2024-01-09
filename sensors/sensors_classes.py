from sensors_constants import *
from sensors_NN import AnimalNeuralNetwork
import pygame
import math
import random
import sys
import torch


class GameOfLife:
    def __init__(self, screen_size):
        pygame.init()
        self.screen_size = screen_size
        self.screen = pygame.display.set_mode([self.screen_size, self.screen_size])
        self.preys = []
        self.predators = []

        # Initialize test prey
        self.preys.append(Prey(prey_rescaled_image, initial_x=self.screen_size // 2, initial_y=self.screen_size // 2, direction=0, speed=1))

        # 20 pre-defined semi-random initial positions for predators, for testing
        random.seed(178)
        for i in range(20):
            self.predators.append(Predator(predator_rescaled_image, initial_x=random.randint(0, self.screen_size), initial_y=random.randint(0, self.screen_size), direction=0, speed=0))

        self.epoch_length = 1000
        self.current_tick = 0
        self.total_epochs = 0

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            print(self.current_tick)
            # set a timer to stop the game after 1000 steps
            if self.total_epochs > 1:
                running = False

            self.update() 
            self.draw()

            # Update the tick count
            self.current_tick += 1
            # Check if the epoch has ended
            if self.current_tick >= self.epoch_length:
                self.end_epoch()

            pygame.display.flip()
            pygame.time.Clock().tick(60)

        pygame.quit()
        sys.exit()
    
    def end_epoch(self):
        # Evaluate the performance of the prey
        for prey in self.preys:
            
            # reward is the number of ticks the prey survived, normalized to [0, 1]
            reward = self.current_tick / self.epoch_length
            
            # Update the network (this method needs to be implemented in your Animal or Neural Network class)
            prey.learn(reward)  # This will use the reward to adjust the neural network's weights

        # Reset for the next epoch
        self.current_tick = 0
        self.total_epochs += 1
        self.respawn_preys()

    def respawn_preys(self):
        # Remove all current preys
        self.preys.clear()

        # Add a new prey for the next epoch
        self.preys.append(Prey(prey_rescaled_image, initial_x=self.screen_size // 2, initial_y=self.screen_size // 2, direction=0, speed=1))


    def check_collision(self):
        for prey in self.preys:
            for predator in self.predators:
                if prey.check_collision(predator):
                    prey.on_collision(predator)  # die
                    predator.on_collision(prey)  # gain energy

    def update(self):
        self.check_collision()
        self.check_alive()
        self.prey_actions(self.preys)
        self.predator_actions(self.predators)
   
    def check_alive(self):
        self.preys = [prey for prey in self.preys if prey.alive]
        self.predators = [predator for predator in self.predators if predator.alive and predator.energy > 0]

    def prey_actions(self, preys):
        for prey in preys:
            # prey.energy += PREY_ENERGY_INCREASE_RATE  # Preys eat grass as they move
            # if prey.energy > PREY_REPRODUCTION_THRESHOLD + random.randint(0, 100) and len(self.preys) < MAX_PREY_NUMBER:
            #     self.preys.append(prey.reproduce())
            #     prey.energy -= PREY_INITIAL_ENERGY

            # prey.turn(random.randint(-10, 10))
            # prey.turn(1)
            prey.calculate_antennas()
            prey.detect_predator(self.predators)
            prey.turn(prey.decide_direction())
            prey.move()
            
            

    def predator_actions(self, predators):
        for predator in predators:
            # predator.energy -= PREDATOR_ENERGY_CONSUMPTION_RATE # Predator consume energy when move
            if predator.energy > PREDATOR_REPRODUCTION_THRESHOLD:
                self.predators.append(predator.reproduce())
                predator.energy -= PREDATOR_INITIAL_ENERGY

            predator.turn(0)
            predator.move()

    def draw(self):
        self.screen.fill((0, 0, 0))  # Clear the screen

        for prey in self.preys:
            prey.draw(self.screen)

        for predator in self.predators:
            predator.draw(self.screen)

        self.show_life_count()
        # self.show_energy_count()

    def show_life_count(self):
        font = pygame.font.SysFont("Arial", 20)
        text = font.render(f"Preys: {len(self.preys)} Predators: {len(self.predators)}", True, (255, 255, 255))
        self.screen.blit(text, (10, 10))

    def show_energy_count(self):
        font = pygame.font.SysFont("Arial", 20)
        text = font.render("Energy: " + str(self.the_predator.energy), True, (255, 255, 255))
        screen.blit(text, (50, 30))

class Animal:
    def __init__(self, image, initial_x=400, initial_y=400, direction=0, speed=1.5):
        self.original_image = image  # Store the original image
        self.image = image

        self.x = initial_x
        self.y = initial_y

        self.rect = self.image.get_rect(center = (round(self.x), round(self.y)))

        # Initialize collision circle parameters
        self.collision_circle_center = self.rect.center
        self.collision_circle_radius = self.rect.width // 2
        self.collision_circle_color = (255, 0, 0)  # Red color for visibility

        self.direction = direction # default facing right
        self.speed = speed

        self.alive = True

    def move(self):
        # move along the direction vector
        self.x += self.speed * math.cos(math.radians(self.direction))
        self.y += self.speed * math.sin(math.radians(self.direction))

        # Adjust position to wrap around screen
        self.x %= SCREEN_SIZE
        self.y %= SCREEN_SIZE

        self.collision_circle_center = (round(self.x), round(self.y))
        
    def turn(self, angle):
        self.direction += angle
        self.direction %= 360  # Ensure rotation stays within 0-360 degrees

        # Rotate the original image
        self.image = pygame.transform.rotate(self.original_image, -self.direction)

        # Recalculate the rect
        self.rect = self.image.get_rect(center = (round(self.x), round(self.y)))
        self.collision_circle_center = (round(self.x), round(self.y))

    def check_collision(self, other):
        # Calculate distance between the centers of the two animals
        dx = self.collision_circle_center[0] - other.collision_circle_center[0]
        dy = self.collision_circle_center[1] - other.collision_circle_center[1]
        distance = math.sqrt(dx**2 + dy**2)

        # Check if distance is less than sum of radii
        return distance < (self.collision_circle_radius + other.collision_circle_radius)

    def draw(self, screen):
        # Draw the main image
        screen.blit(self.image, self.rect)
        # Draw additional lines for debugging
        # Draw outer circle
        pygame.draw.circle(screen, self.collision_circle_color, self.collision_circle_center, self.collision_circle_radius, 1)

        # Draw antennas
        # Draw antenna points and lines
        for antenna in self.antennas if hasattr(self, "antennas") else []:
            # Draw antenna points
            pygame.draw.circle(screen, self.collision_circle_color, antenna.antenna_point, 2, 0)
            # Draw antenna lines
            pygame.draw.line(screen, self.collision_circle_color, antenna.antenna_point, (antenna.start_x, antenna.start_y), 1)

        # Draw additional images for wrapping effect
        if self.rect.right > SCREEN_SIZE:
            screen.blit(self.image, (self.rect.x - SCREEN_SIZE, self.rect.y))
        if self.rect.left < 0:
            screen.blit(self.image, (self.rect.x + SCREEN_SIZE, self.rect.y))
        if self.rect.bottom > SCREEN_SIZE:
            screen.blit(self.image, (self.rect.x, self.rect.y - SCREEN_SIZE))
        if self.rect.top < 0:
            screen.blit(self.image, (self.rect.x, self.rect.y + SCREEN_SIZE))

        # Handle corners
        if self.rect.right > SCREEN_SIZE and self.rect.bottom > SCREEN_SIZE:
            screen.blit(self.image, (self.rect.x - SCREEN_SIZE, self.rect.y - SCREEN_SIZE))
        if self.rect.left < 0 and self.rect.top < 0:
            screen.blit(self.image, (self.rect.x + SCREEN_SIZE, self.rect.y + SCREEN_SIZE))
        if self.rect.right > SCREEN_SIZE and self.rect.top < 0:
            screen.blit(self.image, (self.rect.x - SCREEN_SIZE, self.rect.y + SCREEN_SIZE))
        if self.rect.left < 0 and self.rect.bottom > SCREEN_SIZE:
            screen.blit(self.image, (self.rect.x + SCREEN_SIZE, self.rect.y - SCREEN_SIZE))

class Prey(Animal):
    def __init__(self, image, initial_x=400, initial_y=400, direction=0, speed=1.5):
        super().__init__(image, initial_x, initial_y, direction, speed)
        self.energy = PREY_INITIAL_ENERGY
        self.add_antennas()
        self.sensors_lst = {
            -60: False,
            -40: False,
            -20: False,
            -10: False,
            10: False,
            20: False,
            40: False,
            60: False
        }
        self.brain = AnimalNeuralNetwork(self)
    
    def eat(self):
        self.energy += PREY_ENERGY_INCREASE_RATE

    def on_collision(self, prey):
        self.alive = False

    def reproduce(self):
        return Prey(prey_rescaled_image,
                    initial_x=self.x + random.randint(-animal_width, animal_width),
                    initial_y=self.y + random.randint(-animal_width, animal_width),
                    direction=random.randint(0, 360))

    def add_antennas(self):
        self.antennas = []
        angles = [-60, -40, -20, -10, 10, 20, 40, 60]  # Define the relative angles for each antenna
        lengths = [2, 3, 2, 4, 4, 2, 3, 2]  # Define the lengths for each antenna

        for angle, length in zip(angles, lengths):
            self.antennas.append(
                Antenna(self, angle, length)
            )

    def calculate_antennas(self):
        for antenna in self.antennas:
            antenna.update()

    def detect_predator(self, predators):
        
        for antenna in self.antennas:
            if antenna.check_collision(predators):
                self.sensors_lst.update({antenna.angle: True})
            else:
                self.sensors_lst.update({antenna.angle: False})
        return self.sensors_lst
    
    def decide_direction(self):
        # Transfer self.sensors_lst to input layer Tensors
        input_layer = torch.zeros(8)
        for idx, (key, value) in enumerate(self.sensors_lst.items()):
            if value == True:
                input_layer[idx] = 1

        # Feed input layer to neural network
        output_layer = self.brain(input_layer)
        self.last_output = output_layer
        # Decide direction based on output layer
        if output_layer[0] > output_layer[1]:
            return -10
        else:
            return 10
        
    def learn(self, reward):
        # learn from the reward to make it survive longer
        # first, convert the reward to loss
        # Convert the reward to loss
        expected_reward = torch.tensor([reward], requires_grad=True)

        # Get the last decision (turning direction)
        last_decision = self.last_output

        # Calculate the loss
        loss = self.brain.criterion(last_decision, expected_reward)

        # Zero the parameter gradients
        self.brain.optimizer.zero_grad()

        # Backpropagate the loss
        loss.backward()

        # Update the weights
        self.brain.optimizer.step()


class Predator(Animal):
    def __init__(self, image, initial_x=400, initial_y=400, direction=0, speed=1.5):
        super().__init__(image, initial_x, initial_y, direction, speed)
        self.energy = PREDATOR_INITIAL_ENERGY

    def on_collision(self, prey):
        self.eat(prey)

    def eat(self, prey):
        self.energy += prey.energy

    def reproduce(self):
        return Predator(predator_rescaled_image,
                        initial_x=self.x + random.randint(-animal_width, animal_width),
                        initial_y=self.y + random.randint(-animal_width, animal_width),
                        direction=random.randint(0, 360))
    
class Antenna:
    '''
    An antenna is a point used for collision detection.
    '''
    def __init__(self, animal, angle, length):
        self.animal = animal
        self.angle = angle
        self.length = length
        self.update()
    
    def update(self):
        # update the position of the antenna

        # start point:
        self.start_x = self.animal.x
        self.start_y = self.animal.y

        # end point:
        self.end_x = self.animal.x + self.length * animal_width * math.cos(math.radians(self.animal.direction + self.angle))
        self.end_y = self.animal.y + self.length * animal_width * math.sin(math.radians(self.animal.direction + self.angle))

        self.antenna_point = (self.end_x, self.end_y)

    def check_collision(self, predators):
        for predator in predators:
            # check if the antenna point is within the predator's collision circle
            dx = self.antenna_point[0] - predator.collision_circle_center[0]
            dy = self.antenna_point[1] - predator.collision_circle_center[1]
            distance = math.sqrt(dx**2 + dy**2)

            if distance < predator.collision_circle_radius:
                return True
        
        return False