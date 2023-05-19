import pygame 
from .constants import *
import random 

def load_bg_image():
    unscaled = pygame.image.load(PATH_BG_IMAGE).convert()
    return pygame.transform.scale(unscaled, (GAME_WIDTH, GAME_HEIGHT))


def getRandomPosition():

    x_positions = [i for i in range(20, GAME_WIDTH, 40)]
    y_positions = [i for i in range(40, GAME_HEIGHT, 40)] 

    x = random.choice(x_positions)
    y = random.choice(y_positions)

    return x, y


def getRandoPositionGoal():
    positions = [ (20, 40) , (GAME_WIDTH - 20, GAME_HEIGHT), (GAME_WIDTH - 20, 40), (20, GAME_HEIGHT)]
    x, y = random.choice(positions)
    return x, y


def reduceInformationsToUserInput(current_informations):
    dataJson = current_informations["data"]
    frames = [] 
    for key in dataJson.keys():
        frames.append(dataJson[key])

    unique_frames = []
    for frame in frames:
        if frame["player"]["pressedKeys"] != []:
            unique_frames.append(frame)
        elif frame["terminated"]:
            unique_frames.append(frame)

    return unique_frames 
        

def spawnRoulette(existence_perc):
    number = random.randint(0, 100)
    if number <= existence_perc * 100:
        return True
    else:
        return False