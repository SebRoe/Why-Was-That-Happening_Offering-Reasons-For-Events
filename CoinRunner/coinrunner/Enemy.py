import pygame, random 
from pygame.locals import *
from pygame.math import Vector2
from .constants import * 
from .utils import *

class Enemy(pygame.sprite.Sprite):

    def __init__(self, moving=False, sanity_checker=None):

        super(Enemy, self).__init__()

        unscaled = pygame.image.load(PATH_ENEMY_IMAGE).convert_alpha()
        self.surf = pygame.transform.scale(unscaled, (ENEMY_WIDTH, ENEMY_HEIGHT))
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect()

        if POSITIONING == Positioning.ALL_FIXED:
            x, y = ENEMY_POSITION

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
        self.vel = Vector2(0,0)
        self.rect.midbottom = self.pos


        self.moving = moving 
        self.map_movement = {0: "W", 1: "A", 2: "S", 3: "D"}
        self.direction = None 

        

    def move(self):
        if self.moving:

            change_direction = True if random.randint(0, 100) < 10 else False

            if change_direction:
                direction = random.randint(0, 3)
                virt_key = self.map_movement[direction]
            else:
                if self.direction is None:
                    virt_key = self.map_movement[random.randint(0, 3)]
                else:
                    virt_key = self.direction

            if virt_key == "W":
                self.pos += Vector2(0, -40)
            elif virt_key == "A":
                self.pos += Vector2(-40, 0)
            elif virt_key == "S":
                self.pos += Vector2(0, 40)
            elif virt_key == "D":
                self.pos += Vector2(40, 0)



            # Check Boundaries of Screen
            if self.pos.x > GAME_WIDTH - 20:
                self.pos.x = GAME_WIDTH - 20
            elif self.pos.x < 20:
                self.pos.x = 20


            elif self.pos.y > GAME_HEIGHT:
                self.pos.y = GAME_HEIGHT
            elif self.pos.y < 40:
                self.pos.y = 40

            self.rect.midbottom = self.pos





    def record_update(self, frame:int, lagging_frame:int,  recording):
        recording["data"][frame]["enemy"]["pos"] = (self.pos[0], self.pos[1])
        recording["data"][frame]["enemy"]["moving"] = self.moving
        recording["data"][frame]["enemy"]["direction"] = self.direction
        return recording 