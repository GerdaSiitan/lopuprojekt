import pygame
import sys
from sprites import Player, Block, SlotMachineSprite
from config import *

class SlotRoom:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen

        # Groups for proper collision
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.blocks = pygame.sprite.Group()
        self.npcs = pygame.sprite.Group()  # empty in this room

        self.slot_machine_sprite = None

        # Build tilemap and place slot machine where Arche was
        for row_index, row in enumerate(tilemap):
            for col_index, cell in enumerate(row):
                x = col_index
                y = row_index
                if cell == 'W':
                    Block(self, x, y)
                elif cell == 'A':
                    self.slot_machine_sprite = SlotMachineSprite(self, x, y)

        # Place player at center of slot machine
        if self.slot_machine_sprite:
            px = self.slot_machine_sprite.rect.centerx // tile_size
            py = self.slot_machine_sprite.rect.centery // tile_size
            self.player = Player(self, px, py)
            self.all_sprites.add(self.player)

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    # Player presses E on the slot machine
                    if pygame.sprite.collide_rect(self.player, self.slot_machine_sprite):
                        import slotimasin
                        slotimasin.main()

    def update(self):
        self.all_sprites.update()

    def draw(self):
        self.screen.fill((150, 150, 150))
        self.all_sprites.draw(self.screen)

        # Only show hint if player is touching the slot machine
        if pygame.sprite.collide_rect(self.player, self.slot_machine_sprite):
            font = pygame.font.Font(None, 24)
            text = font.render("Press E to use slot machine", True, (255, 255, 0))
            text_rect = text.get_rect(center=(self.slot_machine_sprite.rect.centerx,
                                              self.slot_machine_sprite.rect.top - 20))
            self.screen.blit(text, text_rect)
