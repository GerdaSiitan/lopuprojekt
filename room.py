import pygame
import sys

from sprites import Player, Block, SlotMachineSprite
from config import *


class SolidCollider(pygame.sprite.Sprite):
    """Invisible 1-tile collider that blocks movement (belongs to room.blocks)."""
    def __init__(self, room, tx, ty):
        super().__init__()
        self.image = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
        self.rect = pygame.Rect(tx * tile_size, ty * tile_size, tile_size, tile_size)
        room.blocks.add(self)


class SlotRoom:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen

        # Groups expected by Player.update() in sprites.py
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.blocks = pygame.sprite.Group()
        self.npcs = pygame.sprite.Group()

        # Attributes ROBOLAHING.py expects
        self.player = None
        self.slot_machine_sprite = None  # ✅ keep this name

        # Internal helpers
        self._slot_collider = None
        self.machine_tile = None
        self.player_tile = None

        self._build_world()

    def _build_world(self):
        # Build walls and find A and P
        for y, row in enumerate(tilemap):
            for x, cell in enumerate(row):
                if cell == "W":
                    Block(self, x, y)
                elif cell == "A":
                    self.machine_tile = (x, y)
                elif cell == "P":
                    self.player_tile = (x, y)

        # Fallbacks
        if self.machine_tile is None:
            self.machine_tile = ((win_width // 2) // tile_size, 2)
        if self.player_tile is None:
            self.player_tile = ((win_width // 2) // tile_size, (win_height - 2 * tile_size) // tile_size)

        mx, my = self.machine_tile
        px, py = self.player_tile

        # --- Slot machine at A ---
        # Your SlotMachineSprite behaves like it wants PIXEL coords, so pass pixels.
        sm = SlotMachineSprite(self, mx * tile_size, my * tile_size)

        # Ensure drawn
        if sm not in self.all_sprites:
            self.all_sprites.add(sm)

        # Align to tile (stand on the tile)
        tile_rect = pygame.Rect(mx * tile_size, my * tile_size, tile_size, tile_size)
        sm.rect.midbottom = tile_rect.midbottom

        # Expose expected attribute name
        self.slot_machine_sprite = sm

        # Collider blocks player from walking through the machine tile
        self._slot_collider = SolidCollider(self, mx, my)

        # --- Player at P (tile coords like your normal room) ---
        self.player = Player(self, px, py)
        if self.player not in self.all_sprites:
            self.all_sprites.add(self.player)

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                # use proximity to collider (more reliable than big sprite rect)
                if self.player.rect.colliderect(self._slot_collider.rect.inflate(tile_size, tile_size)):
                    import slotimasin
                    slotimasin.main()

    def update(self):
        self.all_sprites.update()

    def draw(self):
        self.screen.fill((150, 150, 150))
        self.all_sprites.draw(self.screen)

        if self.player.rect.colliderect(self._slot_collider.rect.inflate(tile_size, tile_size)):
            font = pygame.font.Font(None, 36)
            text = font.render("Press E to use slot machine", True, (255, 255, 0))
            text_rect = text.get_rect(center=(win_width // 2, 40))
            self.screen.blit(text, text_rect)
