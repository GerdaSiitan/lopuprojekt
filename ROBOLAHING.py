import pygame
from sprites import *
from config import *
from TitlePage import TitlePage
from room import SlotRoom
from black import Blackscreen
import sys
import math

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((win_width, win_height))
        pygame.display.set_caption("SOMETHING")
        self.clock = pygame.time.Clock()
        
        self.running = True
        self.playing = False
        self.active_conversation = None
        self.conversation_npc = None

        # Sprites and groups
        self.all_sprites = None
        self.blocks = None
        self.npcs = None
        self.player = None

        # Room states
        self.room_mode = "normal"  # normal / slot_room
        self.slot_room = None

    # ================= TITLE SCREEN =================
    def show_title_screen(self):
        title_page = TitlePage(self.screen)
        return title_page.run()

    # ================= NEW GAME =================
    def new(self):
        self.playing = True
        self.room_mode = "normal"

        # Initialize sprite groups
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.blocks = pygame.sprite.Group()
        self.npcs = pygame.sprite.Group()

        # Create overworld tilemap
        self.create_tilemap(slot_room=False)

        # Spawn player at 'P' tile
        if not self.player:
            for row_index, row in enumerate(tilemap):
                for col_index, cell in enumerate(row):
                    if cell == 'P':
                        self.player = Player(self, col_index, row_index)
                        break

    # ================= TILEMAP =================
    def create_tilemap(self, slot_room=False):
        for row_index, row in enumerate(tilemap):
            for col_index, cell in enumerate(row):
                x = col_index
                y = row_index
                if cell == 'W':
                    Block(self, x, y)
                elif cell == 'A' and not slot_room:
                    npc = ArchE(self, x, y)
                    self.npcs.add(npc)

    # ================= NPC CHECK =================
    def check_talkable(self):
        if not self.player:
            return
        for npc in self.npcs:
            dist = math.hypot(
                self.player.rect.centerx - npc.rect.centerx,
                self.player.rect.centery - npc.rect.centery
            )
            npc.talkable = dist < 80

    # ================= EVENTS =================
    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False

            if event.type == pygame.KEYDOWN:
                # ===== NPC DIALOG =====
                if self.active_conversation and self.conversation_npc:
                    npc = self.conversation_npc
                    if not npc.advance_dialog():
                        if npc.dialog_sequence[-1]["text"] == "*beats up emperor*":
                            Blackscreen(self.screen).run()
                            # Open slot room
                            self.slot_room = SlotRoom(self)
                            self.room_mode = "slot_room"
                        self.active_conversation = False
                        self.conversation_npc = None
                        npc.reset_dialog()

                # ===== START TALKING =====
                elif event.key == pygame.K_e:
                    if self.room_mode == "normal":
                        for npc in self.npcs:
                            if npc.talkable:
                                self.active_conversation = True
                                self.conversation_npc = npc
                                npc.in_conversation = True
                                break
                    elif self.room_mode == "slot_room" and self.slot_room:
                        if pygame.sprite.collide_rect(self.slot_room.player, self.slot_room.slot_machine_sprite):
                            import slotimasin
                            slotimasin.main()

                elif event.key == pygame.K_ESCAPE:
                    self.playing = False

    # ================= UPDATE =================
    def update(self):
        if self.room_mode == "normal":
            if self.all_sprites:
                self.all_sprites.update()
            self.check_talkable()
        elif self.room_mode == "slot_room" and self.slot_room:
            self.slot_room.update()

    # ================= DIALOG =================
    def draw_dialog(self):
        if self.active_conversation and self.conversation_npc:
            npc = self.conversation_npc
            current_dialog = npc.get_current_dialog()
            if current_dialog:
                font = pygame.font.Font(None, 28)
                small_font = pygame.font.Font(None, 24)
                speaker_text = f"{current_dialog['speaker']}:"
                dialog_text = current_dialog['text']
                lines = self.wrap_text(dialog_text, font, self.screen.get_width() - 140)
                text_height = len(lines) * 35
                total_height = text_height + 60
                box = pygame.Rect(50, self.screen.get_height() - total_height - 20,
                                  self.screen.get_width() - 100, total_height)
                pygame.draw.rect(self.screen, (0, 0, 0), box)
                pygame.draw.rect(self.screen, (255, 255, 255), box, 2)
                speaker_color = (255, 100, 100) if current_dialog["speaker"] == "Arche" else (100, 100, 255)
                speaker_surface = font.render(speaker_text, True, speaker_color)
                self.screen.blit(speaker_surface, (box.x + 20, box.y + 15))
                y_offset = box.y + 50
                for line in lines:
                    text_surface = font.render(line, True, (255, 255, 255))
                    self.screen.blit(text_surface, (box.x + 20, y_offset))
                    y_offset += 35
                if npc.current_line < len(npc.dialog_sequence) - 1:
                    instruct = small_font.render("Press any key to continue...", True, (150, 150, 150))
                    self.screen.blit(instruct, (box.x + 20, box.y + box.height - 30))

    # ================= TEXT WRAP =================
    def wrap_text(self, text, font, max_width):
        words = text.split(' ')
        lines = []
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_width = font.size(test_line)[0]
            if test_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        return lines

    # ================= DRAW =================
    def draw(self):
        self.screen.fill((150, 150, 150))

        if self.room_mode == "normal":
            if self.all_sprites:
                self.all_sprites.draw(self.screen)
            if not self.active_conversation and self.npcs:
                for npc in self.npcs:
                    if npc.talkable:
                        font = pygame.font.Font(None, 24)
                        text = font.render("Press E to talk", True, (255, 255, 0))
                        text_rect = text.get_rect(center=(npc.rect.centerx, npc.rect.top - 20))
                        self.screen.blit(text, text_rect)
            self.draw_dialog()
        elif self.room_mode == "slot_room" and self.slot_room:
            self.slot_room.draw()

        # Menu hint
        hint_font = pygame.font.Font(None, 20)
        hint_text = hint_font.render("Press ESC to return to menu", True, (100, 100, 100))
        self.screen.blit(hint_text, (10, 10))

        pygame.display.update()

    # ================= MAIN LOOP =================
    def main(self):
        choice = self.show_title_screen()
        if choice == "play":
            self.new()
            while self.running and self.playing:
                self.events()
                self.update()
                self.draw()
                self.clock.tick(60)
        elif choice == "quit":
            self.running = False

if __name__ == "__main__":
    g = Game()
    g.main()
    pygame.quit()
    sys.exit()
