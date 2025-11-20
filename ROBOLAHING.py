import pygame
from sprites import *
from config import *
from TitlePage import *
import sys

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((win_width, win_height))
        self.clock = pygame.time.Clock()
        self.running = True

    def new(self):
    #mäng hakkab käima
        self.playing = True
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.blocks = pygame.sprite.LayeredUpdates()
        self.enemies = pygame.sprite.LayeredUpdates()
        self.attacks = pygame.sprite.LayeredUpdates()

        self.player = Player(self, 1, 2)
        self.npc = ArchE(self, 4.5, 1)

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False

    def update(self):
        self.all_sprites.update()

    def draw(self):
        self.screen.fill((211, 211, 211))
        self.all_sprites.draw(self.screen)
        self.clock.tick(60)
        pygame.display.update()

    def main(self):
        #mängu tsükkel
        self.playing = True
        while self.playing:
            self.events()
            self.update()
            self.draw()
        self.running = False 

    def game_over(self):
        pass
 
    def intro_screen(self):
        pass

g = Game()
g.new()
g.intro_screen()
while g.running:
    g.main()
    g.game_over()

pygame.quit()
sys.exit()