from neat_constants import *
import pygame
import math
import random

class Animal:
    def __init__(self, image, initial_x=400, initial_y=400, direction=0.0, velocity=0.0):
        
        # original configs
        self.original_image = image
        self.initial_x = initial_x
        self.initial_y = initial_y
        self.initial_velocity = velocity
        self.initial_angle = direction

        # Life parameters
        self.alive = True
        self.time_lived = 0
        self.fitness = 0

        self.reset()

    def reset(self):
        # movement parameters
        self.velocity = self.initial_velocity
        self.angle = self.initial_angle

        self.image = pygame.transform.rotate(self.original_image, -self.angle)
        # Position parameters
        self.x = self.initial_x
        self.y = self.initial_y
        self.rect = self.image.get_rect(center = (round(self.x), round(self.y)))

        # Collision circle parameters
        self.collision_circle_center = self.rect.center
        self.collision_circle_radius = animal_width // 2
        # self.collision_circle_color = (255, 0, 0)  # Red color for visibility

        # Life parameters
        self.alive = True
        self.fitness = 0
        self.time_lived = 0

        # self.turn(0)

    def act(self, action):
        if action[0] == 1:
            self.move(1)
        if action[1] == 1:
            self.move(-1)
        if action[2] == 1:
            self.turn(-1)
        if action[3] == 1:
            self.turn(1)
        if action[0] == 0 and action[1] == 0:
            self.move(0)

        if self.alive:
            self.time_lived += 1
            self.fitness += self.velocity

    def move(self, acceleration):
        # update acceleration
        if acceleration > 0:
            if self.velocity < 5:
                self.velocity += 0.5
        elif acceleration < 0:
            self.velocity -= 0.5
            if self.velocity < 0:
                self.velocity = 0
        else:
            self.velocity *= 0.9

        # move along the direction vector
        self.x += self.velocity * math.cos(math.radians(self.angle))
        self.y += self.velocity * math.sin(math.radians(self.angle))

        # Adjust position to wrap around screen
        self.x %= SCREEN_SIZE
        self.y %= SCREEN_SIZE

        self.rect = self.image.get_rect(center = (round(self.x), round(self.y)))
        self.collision_circle_center = (round(self.x), round(self.y))
        
    def turn(self, steering):

        # update angle
        if steering > 0:
            self.angle += 5
        elif steering < 0:
            self.angle -= 5

        self.angle %= 360  # Ensure rotation stays within 0-360 degrees
        
        # Rotate the original image
        self.image = pygame.transform.rotate(self.original_image, -self.angle)

        # Recalculate the rect
        self.rect = self.image.get_rect(center = (round(self.x), round(self.y)))
        self.collision_circle_center = (round(self.x), round(self.y))

    def check_collision(self, other):
        # Calculate distance between the centers of the two animals
        dx = self.collision_circle_center[0] - other.collision_circle_center[0]
        dy = self.collision_circle_center[1] - other.collision_circle_center[1]
        distance = math.sqrt(dx**2 + dy**2)

        # # debug print:
        # print(f"self: {self.collision_circle_center}, other: {other.collision_circle_center}, distance: {distance}")

        # Check if distance is less than sum of radii
        return distance < (self.collision_circle_radius + other.collision_circle_radius)

    def draw(self, screen):
        # Draw the main image
        screen.blit(self.image, self.rect)
        # Draw additional outcircle for debugging
        # pygame.draw.circle(screen, self.collision_circle_color, self.collision_circle_center, self.collision_circle_radius, 1)

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
    def __init__(self, image, initial_x=400, initial_y=400, direction=0, velocity=1.0):
        super().__init__(image, initial_x, initial_y, direction, velocity)
        self.energy = PREY_INITIAL_ENERGY
        self.build_antenna()
    
    def eat(self):
        self.energy += PREY_ENERGY_INCREASE_RATE

    def on_collision(self, prey):
        self.alive = False

    def reproduce(self):
        return Prey(prey_rescaled_image,
                    initial_x=self.x + random.randint(-animal_width, animal_width),
                    initial_y=self.y + random.randint(-animal_width, animal_width),
                    direction=random.randint(0, 360))
    
    def build_antenna(self):
        # Build antennas
        antennas_angles = [-60, -30, 0, 30, 60]
        antennas_lengths = [100, 150, 200, 150, 100]
        # antennas_angles = [0]
        # antennas_lengths = [200]

        # antennas_angles = [self.angle]
        self.antennas = []
        for angle, length in zip(antennas_angles, antennas_lengths):
            antenna = Antenna(self.collision_circle_center[0], self.collision_circle_center[1], angle, self, length)
            self.antennas.append(antenna)
    
    def update_antenna(self, predators):
        for antenna in self.antennas:
            antenna.update(predators)

    def draw_antenna(self, screen):
        for antenna in self.antennas:
            antenna.draw(screen)

    def draw(self, screen):
        super().draw(screen)
        self.draw_antenna(screen)

    def sense(self):
        return [antenna.length - antenna.default_length for antenna in self.antennas]

class Predator(Animal):
    def __init__(self, image, initial_x=400, initial_y=400, direction=0, velocity=1.0):
        super().__init__(image, initial_x, initial_y, direction, velocity)
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
    def __init__(self, x, y, angle, animal, max_length, default_length=21):
        self.animal = animal
        self.angle = angle
        self.direction = self.animal.angle + self.angle

        self.default_length = default_length
        self.length = default_length
        self.max_length = max_length

        self.x = x
        self.y = y
        self.end_x = int(self.x + math.cos(math.radians(self.angle % 360)) * self.length)
        self.end_y = int(self.y + math.sin(math.radians(self.angle % 360)) * self.length)

    def update(self, predators):
        self.x = self.animal.collision_circle_center[0]
        self.y = self.animal.collision_circle_center[1]
        self.direction = self.animal.angle + self.angle
        
        self.length = self.default_length
        self.end_x = int(self.x + math.cos(math.radians(self.direction % 360)) * self.length)
        self.end_y = int(self.y + math.sin(math.radians(self.direction % 360)) * self.length)

        touching_predator = False
        while self.length < self.max_length and not touching_predator:
            
            self.end_x = int(self.x + math.cos(math.radians(self.direction % 360)) * self.length)
            self.end_y = int(self.y + math.sin(math.radians(self.direction % 360)) * self.length)


            # check if the antenna is touching a predator
            for predator in predators:

                dx = self.end_x - predator.x
                dy = self.end_y - predator.y
                distance = int(math.sqrt(dx**2 + dy**2))
                
                if distance < predator.collision_circle_radius:
                    touching_predator = True
                    break
            
            self.length += 1

    def get_lines(self, line_start, line_end, screen_size=SCREEN_SIZE):

        lines = []
        lines.append((line_start, line_end))
        
        x1, y1 = line_start
        x2, y2 = line_end
        
        '''
        situations:

        1: x2 <= 0               y2 <= 0                    3 lines
        2: x2 <= 0               0 < y < screen_size        2 lines
        3: x2 <= 0               y2 >= screen_size          3 lines
        4: 0 < x2 < screen_size  y2 <= 0                    2 line
        5: 0 < x2 < screen_size  0 < y < screen_size        1 line
        6: 0 < x2 < screen_size  y2 >= screen_size          2 lines
        7: x2 >= screen_size     y2 <= 0                    3 lines
        8: x2 >= screen_size     0 < y < screen_size        2 lines
        9: x2 >= screen_size     y2 >= screen_size          3 lines
        '''

        if 0 < x2 and x2 < screen_size:
            if y2 <= 0: # situ 4
                new_line_start = (x1, y1 + screen_size)
                new_line_end = (x2, y2 + screen_size)
                lines.append((new_line_start, new_line_end))

            if 0 < y2 and y2 < screen_size: # situ 5
                pass

            if y2 >= screen_size: # situ 6
                new_line_start = (x1, y1 - screen_size)
                new_line_end = (x2, y2 - screen_size)
                lines.append((new_line_start, new_line_end))

        elif x2 <= 0:
            if y2 <= 0:
                new_line_start = (x1 + screen_size, y1)
                new_line_end = (x2 + screen_size, y2)
                lines.append((new_line_start, new_line_end))

                new_line_start = (x1, y1 + screen_size)
                new_line_end = (x2, y2 + screen_size)
                lines.append((new_line_start, new_line_end))

                new_line_start = (x1 + screen_size, y1 + screen_size)
                new_line_end = (x2 + screen_size, y2 + screen_size)
                lines.append((new_line_start, new_line_end))

            if 0 < y2 and y2 < screen_size:
                new_line_start = (x1 + screen_size, y1)
                new_line_end = (x2 + screen_size, y2)
                lines.append((new_line_start, new_line_end))

            if y2 >= screen_size:
                new_line_start = (x1 + screen_size, y1)
                new_line_end = (x2 + screen_size, y2)
                lines.append((new_line_start, new_line_end))

                new_line_start = (x1, y1 - screen_size)
                new_line_end = (x2, y2 - screen_size)
                lines.append((new_line_start, new_line_end))

                new_line_start = (x1 + screen_size, y1 - screen_size)
                new_line_end = (x2 + screen_size, y2 - screen_size)
                lines.append((new_line_start, new_line_end))

        elif x2 >= screen_size:
            if y2 <= 0:
                new_line_start = (x1 - screen_size, y1)
                new_line_end = (x2 - screen_size, y2)
                lines.append((new_line_start, new_line_end))

                new_line_start = (x1, y1 + screen_size)
                new_line_end = (x2, y2 + screen_size)
                lines.append((new_line_start, new_line_end))

                new_line_start = (x1 - screen_size, y1 + screen_size)
                new_line_end = (x2 - screen_size, y2 + screen_size)
                lines.append((new_line_start, new_line_end))

            if 0 < y2 and y2 < screen_size:
                new_line_start = (x1 - screen_size, y1)
                new_line_end = (x2 - screen_size, y2)
                lines.append((new_line_start, new_line_end))

            if y2 >= screen_size:
                new_line_start = (x1 - screen_size, y1)
                new_line_end = (x2 - screen_size, y2)
                lines.append((new_line_start, new_line_end))

                new_line_start = (x1, y1 - screen_size)
                new_line_end = (x2, y2 - screen_size)
                lines.append((new_line_start, new_line_end))

                new_line_start = (x1 - screen_size, y1 - screen_size)
                new_line_end = (x2 - screen_size, y2 - screen_size)
                lines.append((new_line_start, new_line_end))

        return lines
        



    def draw(self, screen):
        lines_to_draw = self.get_lines((self.x, self.y), (self.end_x, self.end_y))
        for line in lines_to_draw:
            pygame.draw.line(screen, (0, 255, 0), line[0], line[1], 1)
            pygame.draw.circle(screen, (0, 255, 0), line[1], 5)


class SimulationStats:
    def __init__(self):
        self.avg_fitnesses = []
        self.max_fitnesses = []



   




            
