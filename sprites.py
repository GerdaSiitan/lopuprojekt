import pygame
from config import *
import math
import random

class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self.groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)

        self._layer = PLAYER_LAYER

        self.x = x * tile_size
        self.y = y * tile_size
        self.width = tile_size
        self.height = tile_size
        
        self.image = pygame.Surface((self.width, self.height))
        self.image = pygame.image.load("img/capybara.png")

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def movement(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.rect.x -= 5
        if keys[pygame.K_d]:
            self.rect.x += 5
        if keys[pygame.K_w]:
            self.rect.y -= 5
        if keys[pygame.K_s]:
            self.rect.y += 5
    
    def update(self):
        self.movement()
