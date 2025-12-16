import pygame
from config import *

class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self.groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)

        self._layer = PLAYER_LAYER
        self.width = 64
        self.height = 64

        self.images = {
            "S": pygame.transform.scale(pygame.image.load("img/emperor_S.png"), (self.width, self.height)),
            "W": pygame.transform.scale(pygame.image.load("img/emperor_W.png"), (self.width, self.height)),
            "A": pygame.transform.scale(pygame.image.load("img/emperor_A.png"), (self.width, self.height)),
            "D": pygame.transform.scale(pygame.image.load("img/emperor_D.png"), (self.width, self.height)),
        }

        self.image = self.images["S"]
        self.rect = self.image.get_rect()
        self.rect.centerx = x * tile_size + tile_size // 2
        self.rect.centery = y * tile_size + tile_size // 2

    def update(self):
        keys = pygame.key.get_pressed()
        dx = dy = 0

        if keys[pygame.K_a]: dx -= 4; self.image = self.images["A"]
        if keys[pygame.K_d]: dx += 4; self.image = self.images["D"]
        if keys[pygame.K_w]: dy -= 4; self.image = self.images["W"]
        if keys[pygame.K_s]: dy += 4; self.image = self.images["S"]

        self.rect.x += dx
        if pygame.sprite.spritecollideany(self, self.game.blocks) or pygame.sprite.spritecollideany(self, self.game.npcs):
            self.rect.x -= dx

        self.rect.y += dy
        if pygame.sprite.spritecollideany(self, self.game.blocks) or pygame.sprite.spritecollideany(self, self.game.npcs):
            self.rect.y -= dy


class ArchE(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self.groups = game.all_sprites, game.npcs
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.width = 64
        self.height = 64
        self.image = pygame.transform.scale(pygame.image.load("img/arche.png").convert_alpha(), (self.width, self.height))
        self.rect = self.image.get_rect(center=(x * tile_size + tile_size//2, y * tile_size + tile_size//2))

        self.dialog_sequence = [
            {"speaker": "Arche", "text": "Hello hello EMPEROR"},
            {"speaker": "Emperor", "text": "Hello"},
            {"speaker": "Arche", "text": "Haven't seen you here for a long time."},
            {"speaker": "Arche", "text": "*beats up emperor*"},
        ]
        self.current_line = 0
        self.talkable = False
        self.in_conversation = False

    def get_current_dialog(self):
        if self.current_line < len(self.dialog_sequence):
            return self.dialog_sequence[self.current_line]
        return None

    def advance_dialog(self):
        self.current_line += 1
        return self.current_line < len(self.dialog_sequence)

    def reset_dialog(self):
        self.current_line = 0
        self.in_conversation = False


class Block(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self.groups = self.game.all_sprites, self.game.blocks
        pygame.sprite.Sprite.__init__(self, self.groups)

        self._layer = BLOCK_LAYER
        self.width = tile_size
        self.height = tile_size
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill((100, 100, 100))
        self.rect = self.image.get_rect()
        self.rect.x = x * tile_size
        self.rect.y = y * tile_size


class SlotMachineSprite(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.image = pygame.image.load("img/slotimasin.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (96, 128))
        self.rect = self.image.get_rect(center=(x, y))
