import pygame 
from pygame.locals import *
from pygame.math import Vector2
from .constants import * 
from .utils import *



class GoldCoin(pygame.sprite.Sprite):

    def __init__(self, sanity_checker=None):
        super(GoldCoin, self).__init__()

        unscaled = pygame.image.load(PATH_GOLDCOIN).convert_alpha()
        self.surf = pygame.transform.scale(unscaled, (GOLDCOIN_WIDTH, GOLDCOIN_HEIGHT))
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect()

        if POSITIONING == Positioning.ALL_FIXED:
            x, y = GOLDCOIN_POSITION
        else:
            if sanity_checker is not None:
                while True:
                    x, y = getRandomPosition()
                    if sanity_checker.checkPositionIsFree((x, y)):
                        sanity_checker.positions.append((x, y))
                        break
            else:
                x, y = getRandomPosition()

        self.pos = Vector2(x, y)
        self.rect.midbottom = self.pos

    def record_update(self, frame:int, lagging_frame:int,  recording):
        recording["data"][frame]["goldcoin"]["pos"] = (self.pos[0], self.pos[1])
        return recording 