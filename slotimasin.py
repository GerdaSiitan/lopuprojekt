import pygame
import random
import sys
import os
import config

FPS = 60

BET_AMOUNT = 1000
START_DEBT = 4_000_000
START_BALANCE = 0
JACKPOT_AMOUNT = 4_000_000

REEL_WIDTH = 120
REEL_HEIGHT = 120
REEL_GAP = 30

SCREEN_WIDTH = config.win_width
SCREEN_HEIGHT = config.win_height

TOTAL_WIDTH = 3 * REEL_WIDTH + 2 * REEL_GAP
START_X = (SCREEN_WIDTH - TOTAL_WIDTH) // 2
REEL_Y = 200

# --- Asset paths ---
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "img")
BACKGROUND_PATH = os.path.join(ASSETS_DIR, "slotimasin.png")

SYMBOL_IMAGE_PATHS = [
    os.path.join(ASSETS_DIR, "jakupudel.png"),
    os.path.join(ASSETS_DIR, "mangopepsi.png"),
    os.path.join(ASSETS_DIR, "tupsukarp.png"),
]


class SlotMachine:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()

        self.bet_amount = BET_AMOUNT

        # Load assets
        self.background = self._load_and_scale_background(BACKGROUND_PATH)
        self.symbol_surfaces = self._load_symbol_images(SYMBOL_IMAGE_PATHS)

        self.reel_indices = [
            random.randint(0, len(self.symbol_surfaces) - 1),
            random.randint(0, len(self.symbol_surfaces) - 1),
            random.randint(0, len(self.symbol_surfaces) - 1),
        ]

        self.target_indices = self.reel_indices[:]
        self.is_win_spin = False

        self.spinning = False
        self.reel_spinning = [False, False, False]
        self.spin_start_time = 0
        self.stop_delays = [700, 1100, 1500]
        self.last_change_time = [0, 0, 0]
        self.change_interval = 80

        self.debt = START_DEBT
        self.balance = START_BALANCE
        self.last_win_total = 0
        self.last_debt_payment = 0
        self.last_personal_gain = 0

        self.message = ""

        self.font = pygame.font.SysFont("arial", 26)
        self.small_font = pygame.font.SysFont("arial", 20)

        self.spin_button_rect = pygame.Rect(0, 0, 140, 50)
        self.spin_button_rect.centerx = SCREEN_WIDTH // 2
        self.spin_button_rect.bottom = SCREEN_HEIGHT - 40

    # ---------- Asset loading helpers ----------
    def _safe_load_image(self, path: str) -> pygame.Surface | None:
        try:
            abs_path = os.path.abspath(path)
            img = pygame.image.load(abs_path).convert_alpha()
            return img
        except Exception as e:
            print("Failed to load:", path, "->", e)
            return None

    def _load_and_scale_background(self, path: str) -> pygame.Surface | None:
        bg = self._safe_load_image(path)
        if bg is None:
            return None
        return pygame.transform.smoothscale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

    def _load_symbol_images(self, paths: list[str]) -> list[pygame.Surface]:
        target_w = REEL_WIDTH - 5
        target_h = REEL_HEIGHT - 5

        loaded: list[pygame.Surface] = []
        for p in paths:
            img = self._safe_load_image(p)
            if img is None:
                placeholder = pygame.Surface((target_w, target_h), pygame.SRCALPHA)
                placeholder.fill((200, 50, 50))
                pygame.draw.line(placeholder, (255, 255, 255), (0, 0), (target_w, target_h), 4)
                pygame.draw.line(placeholder, (255, 255, 255), (target_w, 0), (0, target_h), 4)
                loaded.append(placeholder)
            else:
                loaded.append(pygame.transform.smoothscale(img, (target_w, target_h)))

        return loaded

    # ---------- Game logic ----------
    def decide_if_win(self) -> bool:
        win_chance = random.uniform(0.001, 0.005)
        return random.random() < win_chance

    def prepare_outcome(self):
        self.is_win_spin = self.decide_if_win()

        if self.is_win_spin:
            sym = random.randint(0, len(self.symbol_surfaces) - 1)
            self.target_indices = [sym, sym, sym]
        else:
            while True:
                a = random.randint(0, len(self.symbol_surfaces) - 1)
                b = random.randint(0, len(self.symbol_surfaces) - 1)
                c = random.randint(0, len(self.symbol_surfaces) - 1)
                if not (a == b == c):
                    self.target_indices = [a, b, c]
                    break

    def start_spin(self):
        if self.spinning:
            return

        if self.debt <= 0:
            self.message = "Debt fully paid."
            return

        self.debt += self.bet_amount
        self.prepare_outcome()

        self.last_win_total = 0
        self.last_debt_payment = 0
        self.last_personal_gain = 0
        self.message = f"Borrowed {self.bet_amount}"

        self.spinning = True
        self.reel_spinning = [True, True, True]
        self.spin_start_time = pygame.time.get_ticks()
        now = self.spin_start_time
        self.last_change_time = [now, now, now]

    def update(self):
        if not self.spinning:
            return

        now = pygame.time.get_ticks()

        for i in range(3):
            if self.reel_spinning[i]:
                if now - self.last_change_time[i] > self.change_interval:
                    self.reel_indices[i] = random.randint(0, len(self.symbol_surfaces) - 1)
                    self.last_change_time[i] = now
                if now - self.spin_start_time > self.stop_delays[i]:
                    self.reel_spinning[i] = False
                    self.reel_indices[i] = self.target_indices[i]

        if not any(self.reel_spinning):
            self.spinning = False
            self.check_win()

    def check_win(self):
        a, b, c = self.reel_indices
        if not (a == b == c):
            self.message = "No match."
            return

        total_win = JACKPOT_AMOUNT
        self.last_win_total = total_win

        debt_payment = int(total_win * 0.9)
        personal_gain = total_win - debt_payment

        actual_debt_pay = min(self.debt, debt_payment)
        self.debt -= actual_debt_pay
        self.balance += personal_gain

        self.last_debt_payment = actual_debt_pay
        self.last_personal_gain = personal_gain

        self.message = f"Jackpot. Debt paid: {actual_debt_pay}"

    # ---------- Drawing ----------
    def draw_reels(self):
        for i in range(3):
            x = START_X + i * (REEL_WIDTH + REEL_GAP)
            y = REEL_Y

            outer = pygame.Rect(x, y, REEL_WIDTH, REEL_HEIGHT)
            pygame.draw.rect(self.screen, (50, 50, 50), outer)
            pygame.draw.rect(self.screen, (200, 200, 200), outer, 3)

            inner = pygame.Rect(x + 5, y + 5, REEL_WIDTH - 10, REEL_HEIGHT - 10)

            symbol_img = self.symbol_surfaces[self.reel_indices[i]]
            img_rect = symbol_img.get_rect(center=inner.center)
            self.screen.blit(symbol_img, img_rect)

    def draw_ui(self):
        if self.background is not None:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill((20, 20, 30))

        title = self.font.render("Pihkviinimasin", True, (255, 255, 255))
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 20))

        debt_s = self.small_font.render(f"Debt: {self.debt}", True, (255, 80, 80))
        self.screen.blit(debt_s, (20, 20))

        bal_s = self.small_font.render(f"Your account: {self.balance}", True, (200, 255, 200))
        self.screen.blit(bal_s, (20, 55))

        bet_s = self.small_font.render(f"Bet: {self.bet_amount}", True, (200, 200, 200))
        self.screen.blit(bet_s, (20, 85))

        self.draw_reels()

        msg = self.small_font.render(self.message, True, (255, 255, 255))
        self.screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, REEL_Y + REEL_HEIGHT + 25))

        btn_color = (100, 100, 100) if self.spinning else (0, 150, 0)
        btn_text = "SPINNING" if self.spinning else "SPIN"
        btn_surf = self.font.render(btn_text, True, (255, 255, 255))

        padding_x = 20
        padding_y = 10
        self.spin_button_rect.size = (btn_surf.get_width() + padding_x * 2, btn_surf.get_height() + padding_y * 2)
        self.spin_button_rect.centerx = SCREEN_WIDTH // 2
        self.spin_button_rect.bottom = SCREEN_HEIGHT - 40

        pygame.draw.rect(self.screen, btn_color, self.spin_button_rect, border_radius=10)
        pygame.draw.rect(self.screen, (255, 255, 255), self.spin_button_rect, 2, border_radius=10)

        self.screen.blit(
            btn_surf,
            (self.spin_button_rect.centerx - btn_surf.get_width() // 2,
             self.spin_button_rect.centery - btn_surf.get_height() // 2)
        )

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.spin_button_rect.collidepoint(event.pos):
                self.start_spin()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.start_spin()

    def run(self):
        while True:
            for event in pygame.event.get():
                self.handle_event(event)

            self.update()
            self.draw_ui()
            pygame.display.flip()
            self.clock.tick(FPS)


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pihkviinimasin")
    SlotMachine(screen).run()


if __name__ == "__main__":
    main()
