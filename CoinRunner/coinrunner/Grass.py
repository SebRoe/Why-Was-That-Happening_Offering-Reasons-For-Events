import pygame, random  
from pygame.locals import * 
from  pygame.math import Vector2

from .constants import *
from .utils import *


class Grass(pygame.sprite.Sprite):

    def __init__(self):
        super(Grass, self).__init__()

        unscaled = pygame.image.load(PATH_GROUND_GRASS).convert_alpha()

        self.surf = pygame.transform.scale(unscaled, (GRASS_WIDTH, GRASS_HEIGHT))
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect()

        x, y, = getRandomPosition()
        
        self.pos = Vector2(x, y)    
        self.rect.midbottom = self.pos