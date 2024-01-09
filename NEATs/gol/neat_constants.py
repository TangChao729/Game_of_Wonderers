import pygame

# ANIMALS
PREY_FILE_PATH = "./sprits/prey.png"
PREDATOR_FILE_PATH = "./sprits/predator.png"

# SCREEN
SCREEN_SIZE = 800

# GAME RULE
# 1. Prey
MAX_PREY_NUMBER = 100
PREY_INITIAL_ENERGY = 100
PREY_ENERGY_INCREASE_RATE = 1
PREY_REPRODUCTION_THRESHOLD = 200

# 2. Predator
PREDATOR_INITIAL_ENERGY = 1000
PREDATOR_ENERGY_CONSUMPTION_RATE = 1
PREDATOR_REPRODUCTION_THRESHOLD = 2000

# Materials
rescaling_factor = 5
# Read prey image
prey_original_image = pygame.image.load(PREY_FILE_PATH)
prey_original_image = pygame.transform.rotate(prey_original_image, 90)
prey_rescaled_image = pygame.transform.scale(prey_original_image, (prey_original_image.get_rect().width // rescaling_factor, prey_original_image.get_rect().height // rescaling_factor))

# Read predator image   
predator_original_image = pygame.image.load(PREDATOR_FILE_PATH)
predator_original_image = pygame.transform.rotate(predator_original_image, 90)
predator_rescaled_image = pygame.transform.scale(predator_original_image, (predator_original_image.get_rect().width // rescaling_factor, predator_original_image.get_rect().height // rescaling_factor))

animal_width = prey_rescaled_image.get_rect().width

# Set up the screen [width, height]
screen = pygame.display.set_mode([SCREEN_SIZE, SCREEN_SIZE])

