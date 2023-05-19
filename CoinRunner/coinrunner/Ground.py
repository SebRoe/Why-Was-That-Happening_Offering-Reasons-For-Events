import pygame 

from .constants import *



class Ground(pygame.sprite.Sprite):
    def __init__(self):
        super(Ground, self).__init__()

        self.x_bricks = int(GAME_WIDTH / BRICK_WIDTH)
        self.y_bricks = int(GAME_HEIGHT / BRICK_HEIGHT)

        unscaled = pygame.image.load(PATH_GROUND_BRICK).convert_alpha()
        scaled = pygame.transform.scale(unscaled, (BRICK_WIDTH, BRICK_HEIGHT))


        self.surf = pygame.Surface(GAME_SIZE)
        self.surf.fill((222,184,135))

        self.rect = self.surf.get_rect(center=(GAME_WIDTH//2, GAME_HEIGHT//2))

        for i in range(self.x_bricks):
            for j in range(self.y_bricks):
                self.surf.blit(scaled, (i * BRICK_WIDTH, j * BRICK_HEIGHT))

