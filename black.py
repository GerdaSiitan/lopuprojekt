import pygame
import sys
from config import *

class Blackscreen:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True

        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.slides = [
            "The Emperor lost consciousness...",
            "After a while,\nthe Emperor slowly started to wake up...",
            "The place where the Emperor woke up\nfelt strange and unfamiliar..."
        ]

        self.current_slide = 0

    def draw(self):
        self.screen.fill((0, 0, 0))

        if self.current_slide >= len(self.slides):
            return  # prevent out-of-range errors

        lines = self.slides[self.current_slide].split("\n")
        y = win_height // 2 - len(lines) * 20

        for line in lines:
            text = self.font.render(line, True, (255, 255, 255))
            rect = text.get_rect(center=(win_width // 2, y))
            self.screen.blit(text, rect)
            y += 40

        hint = self.small_font.render("Press E to continue", True, (180, 180, 180))
        self.screen.blit(hint, (win_width // 2 - 90, y + 20))

        pygame.display.update()

    def run(self):
        while self.running:
            self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                    self.current_slide += 1
                    if self.current_slide >= len(self.slides):
                        self.running = False  # stop loop once all slides shown

            # Only draw if not past last slide
            if self.current_slide < len(self.slides):
                self.draw()
