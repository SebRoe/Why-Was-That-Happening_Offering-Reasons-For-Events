import pygame 
from pygame.locals import * 
from  pygame.math import Vector2

from .constants import *
from .utils import *

class Player(pygame.sprite.Sprite):
    def __init__(self, sanity_checker=None):
        
        super(Player,self).__init__()
        
        # Initialize the player
        self.pu = False 
        self.goldCoin = False 
        self.killedEnemy = False 

        self.pressed_keys = [] 


        self.init_images() 
        self.set_image(self.front_scaled)
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect()


        if POSITIONING == Positioning.ALL_FIXED:
            x, y = PLAYER_POSITION

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
        self.vel = Vector2(0, 0)
        self.rect.midbottom = self.pos


    def init_images(self):
        if not self.pu:
            self.front_unscaled = pygame.image.load(PATH_PLAYER_IMAGE_STANDING).convert_alpha()
            self.front_scaled = pygame.transform.scale(self.front_unscaled, (PLAYER_WIDTH, PLAYER_HEIGHT))

        else:
            self.front_unscaled = pygame.image.load(PATH_PLAYER_PU_IMAGE_STANDING).convert_alpha()
            self.front_scaled = pygame.transform.scale(self.front_unscaled, (PLAYER_WIDTH, PLAYER_HEIGHT))

            self.pu_sword_unscaled = pygame.image.load(PATH_POWERUP).convert_alpha()
            self.pu_sword_scaled_right = pygame.transform.scale(self.pu_sword_unscaled, (PLAYER_PU_SWORD_WIDTH, PLAYER_PU_SWORD_HEIGHT))
            flipped = pygame.transform.flip(self.pu_sword_unscaled, True, False)
            self.pu_sword_scaled_left = pygame.transform.scale(flipped, (PLAYER_PU_SWORD_WIDTH, PLAYER_PU_SWORD_HEIGHT))

    def set_image(self, image):
        self.surf = image

        if self.pu:
            self.surf.blit(self.pu_sword_scaled_left, (20, 0))




    def move(self, pressed_keys):    
        self.pressed_keys = pressed_keys
        if pressed_keys:
            for i in pressed_keys:
                if i == K_w:
                    self.pos += Vector2(0, -40) 
                elif i == K_a:
                    self.pos += Vector2(-40, 0)
                elif i == K_s:
                    self.pos += Vector2(0, 40)
                elif i == K_d:
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



    def powerup(self):
        self.pu = True
        self.init_images() 
        self.surf = self.front_scaled
        


    def record_update(self, frame:int, lagging_frame: int,  recording):
        
        key_mapping = {K_w: "W", K_a: "A", K_s: "S", K_d: "D"}

        recording["data"][frame]["player"]["pos"] = (self.pos[0], self.pos[1])

        recording["data"][frame]["player"]["collectedPowerUp"] = self.pu
        recording["data"][frame]["player"]["collectedGoldCoin"] = self.goldCoin
        recording["data"][frame]["player"]["killedEnemy"] = self.killedEnemy

        recording["data"][frame]["player"]["collectingPowerUp"] = False 
        recording["data"][frame]["player"]["collectingGoldCoin"] = False
        recording["data"][frame]["player"]["killingEnemy"] = False
        
        recording["data"][frame]["player"]["pressedKeys"] = []
        recording["data"][lagging_frame]["player"]["pressedKeys"] = [key_mapping[i] for i in self.pressed_keys]

        return recording 