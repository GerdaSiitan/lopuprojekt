import pygame
import sys
from config import *

class TitlePage:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.options = ["PLAY", "QUIT"]
        self.selected_option = 0 
        
        self.title_font = pygame.font.SysFont('Arial', 80, bold=True)
        self.menu_font = pygame.font.SysFont('Arial', 48)
        self.instruction_font = pygame.font.SysFont('Arial', 24)
        
        self.bg_color = (0, 0, 0)  # Dark blue
        self.title_color = (255, 215, 0)  # Gold
        self.selected_color = (255, 255, 255)  # White
        self.normal_color = (150, 150, 150)  # Gray
        self.arrow_color = (255, 215, 0)  # Gold
        self.instruction_color = (100, 100, 150)  # Light blue-gray

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self.selected_option = (self.selected_option - 1) % len(self.options)
                elif event.key == pygame.K_s:
                    self.selected_option = (self.selected_option + 1) % len(self.options)
                elif event.key == pygame.K_e:
                    if self.selected_option == 0:
                        return "play"
                    elif self.selected_option == 1:
                        return "quit"
        
        return None

    def draw(self):
        self.screen.fill(self.bg_color)
        
        title_text = self.title_font.render("SOMETHING", True, self.title_color)
        title_rect = title_text.get_rect(center=(win_width // 2, win_height // 4))
        self.screen.blit(title_text, title_rect)
        
        menu_y_start = win_height // 2
        
        for i, option in enumerate(self.options):
            color = self.selected_color if i == self.selected_option else self.normal_color
            
            if i == self.selected_option:
                arrow_text = self.menu_font.render(">", True, self.arrow_color)
                arrow_rect = arrow_text.get_rect(midright=(win_width // 2 - 30, menu_y_start + i * 70))
                self.screen.blit(arrow_text, arrow_rect)
            
            option_text = self.menu_font.render(option, True, color)
            option_rect = option_text.get_rect(midleft=(win_width // 2 - 10, menu_y_start + i * 70))
            self.screen.blit(option_text, option_rect)
        
        instructions = [
            "Use W/S keys to navigate",
            "Press E to select"
        ]
        
        for i, line in enumerate(instructions):
            instr_text = self.instruction_font.render(line, True, self.instruction_color)
            instr_rect = instr_text.get_rect(center=(win_width // 2, win_height - 100 + i * 30))
            self.screen.blit(instr_text, instr_rect)
        
        pygame.display.update()

    def run(self):
        while self.running:
            result = self.handle_events()
            if result:
                return result
            
            self.draw()
            self.clock.tick(60)
        
        return "quit"