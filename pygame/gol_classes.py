from gol_constants import *
import pygame
import math
import random
import sys

class GameOfLife:
    def __init__(self, screen_size):
        pygame.init()
        self.screen_size = screen_size
        self.screen = pygame.display.set_mode([self.screen_size, self.screen_size])
        self.preys = []
        self.predators = []

        # Initialize animals
        for i in range(9):
            self.preys.append(Prey(prey_rescaled_image, initial_x=random.randint(0, screen_size), initial_y=random.randint(0, screen_size), direction=random.randint(0, 360)))
            self.predators.append(Predator(predator_rescaled_image, initial_x=random.randint(0, screen_size), initial_y=random.randint(0, screen_size), direction=random.randint(0, 360)))

        # Special predator to check its status
        self.the_predator = Predator(predator_rescaled_image, initial_x=screen_size // 2, initial_y=screen_size // 2, direction=random.randint(0, 360))
        self.predators.append(self.the_predator)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.update() 
            self.draw()

            pygame.display.flip()
            pygame.time.Clock().tick(60)

        pygame.quit()
        sys.exit()

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
            prey.energy += PREY_ENERGY_INCREASE_RATE  # Preys eat grass as they move
            if prey.energy > PREY_REPRODUCTION_THRESHOLD + random.randint(0, 100) and len(self.preys) < MAX_PREY_NUMBER:
                self.preys.append(prey.reproduce())
                prey.energy -= PREY_INITIAL_ENERGY

            prey.turn(random.randint(-10, 10))
            prey.move()

    def predator_actions(self, predators):
        for predator in predators:
            predator.energy -= PREDATOR_ENERGY_CONSUMPTION_RATE # Predator consume energy when move
            if predator.energy > PREDATOR_REPRODUCTION_THRESHOLD:
                self.predators.append(predator.reproduce())
                predator.energy -= PREDATOR_INITIAL_ENERGY

            predator.turn(random.randint(-10, 10))
            predator.move()

    def draw(self):
        self.screen.fill((0, 0, 0))  # Clear the screen

        for prey in self.preys:
            prey.draw(self.screen)

        for predator in self.predators:
            predator.draw(self.screen)

        self.show_life_count()
        self.show_energy_count()

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
        # Draw the collision circle for visualization
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
    def __init__(self, image, initial_x=400, initial_y=400, direction=0, speed=1.5):
        super().__init__(image, initial_x, initial_y, direction, speed)
        self.energy = PREY_INITIAL_ENERGY
    
    def eat(self):
        self.energy += PREY_ENERGY_INCREASE_RATE

    def on_collision(self, prey):
        self.alive = False

    def reproduce(self):
        return Prey(prey_rescaled_image,
                    initial_x=self.x + random.randint(-animal_width, animal_width),
                    initial_y=self.y + random.randint(-animal_width, animal_width),
                    direction=random.randint(0, 360))

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

