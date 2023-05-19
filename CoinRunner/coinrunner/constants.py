import os 
from .enums import Positioning, DistanceMetric, TargetingMetric
### CoinRunner Settings ###

# Screen Settings
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)


GAME_WIDTH = 800 
GAME_HEIGHT = 800
GAME_SIZE = (GAME_WIDTH, GAME_HEIGHT)


SIDE_WIDTH = 400 
SIDE_HEIGHT = 800
SIDE_SIZE = (SIDE_WIDTH, SIDE_HEIGHT)

# Custom Font 
PATH_FONT = os.path.join("assets", "fonts", "SHPinscher-Regular.otf")

# Game Settings
FPS = 10
ENEMY_MOVING = False  
POSITIONING = Positioning.ALL_FIXED
DISTANCE_METRIC = DistanceMetric.MANHATTEN
TARGETING_METRIC = TargetingMetric.COSINE_SIMILARITY

# Sprite Sizes 
PLAYER_HEIGHT, PLAYER_WIDTH = 40, 40
POWERUP_HEIGHT, POWERUP_WIDTH = 30, 30
GOAL_HEIGHT, GOAL_WIDTH = 40, 40
GOLDCOIN_HEIGHT, GOLDCOIN_WIDTH = 40, 40
ENEMY_HEIGHT, ENEMY_WIDTH = 40, 40
PLAYER_PU_SWORD_HEIGHT, PLAYER_PU_SWORD_WIDTH = 20, 20
BRICK_HEIGHT, BRICK_WIDTH = 40, 40
GRASS_HEIGHT, GRASS_WIDTH = 30, 30

# Image Assets 
#PATH_BG_IMAGE = os.path.join("assets", "backgrounds", "background-2", "airadventurelevel1.png")

PATH_PLAYER_IMAGE_STANDING = os.path.join("assets", "kenney", "Players", "Variable sizes", "Blue", "alienBlue_front.png")
PATH_PLAYER_IMAGE_JUMPING = os.path.join("assets", "kenney", "Players", "Variable sizes", "Blue", "alienBlue_jump.png")
PATH_PLAYER_IMAGE_WALKING_1 = os.path.join("assets", "kenney", "Players", "Variable sizes", "Blue", "alienBlue_walk1.png")
PATH_PLAYER_IMAGE_WALKING_2 = os.path.join("assets", "kenney", "Players", "Variable sizes", "Blue", "alienBlue_walk2.png")

PATH_PLAYER_PU_IMAGE_STANDING = os.path.join("assets", "kenney", "Players", "Variable sizes", "Yellow", "alienYellow_front.png")
PATH_PLAYER_PU_IMAGE_JUMPING = os.path.join("assets", "kenney", "Players", "Variable sizes", "Yellow", "alienYellow_jump.png")
PATH_PLAYER_PU_IMAGE_WALKING_1 = os.path.join("assets", "kenney", "Players", "Variable sizes", "Yellow", "alienYellow_walk1.png")
PATH_PLAYER_PU_IMAGE_WALKING_2 = os.path.join("assets", "kenney", "Players", "Variable sizes", "Yellow", "alienYellow_walk2.png")

PATH_ENEMY_IMAGE = os.path.join("assets", "kenney", "Enemies", "barnacle_dead.png")
PATH_BRICK_PLATTFORM = os.path.join("assets", "kenney", "Tiles", "brickBrown.png")

PATH_CLOUDS = os.path.join("assets", "kenney", "Tiles", "snow.png")

PATH_POWERUP = os.path.join("assets", "custom", "Items", "sword.png")
PATH_GOAL = os.path.join("assets", "kenney", "Items", "flagRed1.png")
PATH_GOLDCOIN = os.path.join("assets", "kenney", "Items", "coinGold.png")

PATH_GROUND_BRICK = os.path.join("assets", "kenney", "Tiles","brickBrown.png" )
PATH_GROUND_GRASS = os.path.join("assets", "kenney", "Tiles", "cactus.png")

# Predefined ALL FIXED - Positioning 
PLAYER_POSITION = (500, 80)
ENEMY_POSITION = (340, 280)
POWERUP_POSITION = (700, 400)
GOLDCOIN_POSITION = (180, 160)
#GOAL_POSITION = (GAME_WIDTH - 20, GAME_HEIGHT)
GOAL_POSITION = (GAME_WIDTH - 20, 40)

# Existence of Objects
#EXISTENCE_GOLDCOIN = 0.5
#EXISTENCE_ENEMY = 0.75
#EXISTENCE_POWERUP = 0.75

EXISTENCE_GOLDCOIN = 1
EXISTENCE_ENEMY = 1
EXISTENCE_POWERUP = 1