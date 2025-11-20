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
        self.images = {
            "S": pygame.transform.scale(
                pygame.image.load("img/emperor_S.png"),
                (self.width, self.height)
            ),
            "W": pygame.transform.scale(
                pygame.image.load("img/emperor_W.png"),
                (self.width, self.height)
            ),
             "A": pygame.transform.scale(
                pygame.image.load("img/emperor_A.png"),
                (self.width, self.height)
            ),
             "D": pygame.transform.scale(
                pygame.image.load("img/emperor_D.png"),
                (self.width, self.height)
            )
        }
        self.image = self.images["S"]

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def movement(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.rect.x -= 5
            self.image = self.images["A"]
        if keys[pygame.K_d]:
            self.rect.x += 5
            self.image = self.images["D"]
        if keys[pygame.K_w]:
            self.rect.y -= 5
            self.image = self.images["W"]
        if keys[pygame.K_s]:
            self.rect.y += 5
            self.image = self.images["S"]
    
    def update(self):
        self.movement()

class ArchE(pygame.sprite.Sprite):
    def __init__(npc, game, x, y):
        npc.game = game
        npc.groups = npc.game.all_sprites
        pygame.sprite.Sprite.__init__(npc, npc.groups)

        npc._layer = NPC_LAYER

        npc.x = x * tile_size
        npc.y = y * tile_size
        npc.width = tile_size
        npc.height =  tile_size

        npc.image = pygame.transform.scale(
            pygame.image.load("img/arche.png").convert_alpha(),
            (npc.width, npc.height)
        )

        npc.rect = npc.image.get_rect()
        npc.rect.x = npc.x
        npc.rect.y = npc.y
        
def update(npc):
        pass