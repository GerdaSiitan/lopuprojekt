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

REEL_WIDTH = 72
REEL_HEIGHT = 72
REEL_GAP = 12

SCREEN_WIDTH = config.win_width
SCREEN_HEIGHT = config.win_height
CENTER_X = SCREEN_WIDTH // 2

TOTAL_WIDTH = 3 * REEL_WIDTH + 2 * REEL_GAP

# HOIA 60 PEAL
SLOT_BLOCK_OFFSET_Y = 60

TITLE_Y = 24
REEL_Y = 170 + SLOT_BLOCK_OFFSET_Y

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "img")
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

        # assets
        self.symbol_surfaces = self._load_symbol_images(SYMBOL_IMAGE_PATHS)

        # reel state
        self.reel_indices = [random.randrange(len(self.symbol_surfaces)) for _ in range(3)]
        self.target_indices = self.reel_indices[:]
        self.is_win_spin = False

        # spin timing
        self.spinning = False
        self.reel_spinning = [False, False, False]
        self.spin_start_time = 0
        self.stop_delays = [700, 1100, 1500]
        self.last_change_time = [0, 0, 0]
        self.change_interval = 80

        # economy
        self.debt = START_DEBT
        self.balance = START_BALANCE
        self.last_win_total = 0
        self.last_debt_payment = 0
        self.last_personal_gain = 0
        self.message = ""

        # fonts
        self.font = pygame.font.SysFont("arial", 26)
        self.small_font = pygame.font.SysFont("arial", 20)

        # button
        self.spin_button_rect = pygame.Rect(0, 0, 140, 50)
        self.spin_button_rect.center = (CENTER_X, SCREEN_HEIGHT - 36)

        # bg
        self.bg_surface = self._make_glass_background(SCREEN_WIDTH, SCREEN_HEIGHT)

    # ---------- VISUAL ----------
    def _make_glass_background(self, w, h):
        surf = pygame.Surface((w, h))
        top, bottom = (10, 12, 20), (6, 8, 14)
        for y in range(h):
            t = y / max(1, h - 1)
            col = (
                int(top[0] * (1 - t) + bottom[0] * t),
                int(top[1] * (1 - t) + bottom[1] * t),
                int(top[2] * (1 - t) + bottom[2] * t),
            )
            pygame.draw.line(surf, col, (0, y), (w, y))

        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        rng = random.Random(12345)
        for _ in range(16):
            pygame.draw.circle(
                overlay,
                (255, 255, 255, rng.randint(20, 40)),
                (rng.randint(0, w), rng.randint(0, h)),
                rng.randint(40, 120),
            )
        surf.blit(overlay, (0, 0))
        return surf

    def _draw_glass_rect(self, rect, alpha=60, radius=14):
        glass = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(glass, (255, 255, 255, alpha), glass.get_rect(), border_radius=radius)
        pygame.draw.rect(glass, (255, 255, 255, 90), glass.get_rect(), 2, border_radius=radius)

        hi = pygame.Surface((rect.width, max(1, rect.height // 3)), pygame.SRCALPHA)
        hi.fill((255, 255, 255, 30))
        glass.blit(hi, (0, 0))

        self.screen.blit(glass, rect.topleft)

    # ---------- ASSETS ----------
    def _safe_load_image(self, path):
        try:
            return pygame.image.load(os.path.abspath(path)).convert_alpha()
        except Exception as e:
            print("Failed to load:", path, "->", e)
            return None

    def _fit_image(self, img, w, h, padding=0):
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        if img is None:
            surf.fill((200, 50, 50, 255))
            pygame.draw.line(surf, (255, 255, 255), (0, 0), (w, h), 3)
            pygame.draw.line(surf, (255, 255, 255), (w, 0), (0, h), 3)
            return surf

        max_w = w - padding * 2
        max_h = h - padding * 2
        scale = min(max_w / img.get_width(), max_h / img.get_height())
        new_w = max(1, int(img.get_width() * scale))
        new_h = max(1, int(img.get_height() * scale))
        scaled = pygame.transform.smoothscale(img, (new_w, new_h))
        surf.blit(scaled, scaled.get_rect(center=(w // 2, h // 2)))
        return surf

    def _load_symbol_images(self, paths):
        target_w = REEL_WIDTH - 10
        target_h = REEL_HEIGHT - 10
        out = []
        for p in paths:
            out.append(self._fit_image(self._safe_load_image(p), target_w, target_h, padding=0))
        return out

    # ---------- JACKPOT LOGIC ----------
    def decide_if_win(self) -> bool:
        win_chance = random.uniform(0.00001, 0.00005)
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

    # ---------- GAME ----------
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
                    self.reel_indices[i] = random.randrange(len(self.symbol_surfaces))
                    self.last_change_time[i] = now

                if now - self.spin_start_time > self.stop_delays[i]:
                    self.reel_spinning[i] = False
                    self.reel_indices[i] = self.target_indices[i]

        if not any(self.reel_spinning):
            self.spinning = False
            self.check_win()

    # ---------- DRAW ----------
    def draw(self):
        self.screen.blit(self.bg_surface, (0, 0))

        # TITLE
        title_rect = pygame.Rect(0, TITLE_Y, 360, 46)
        title_rect.centerx = CENTER_X
        self._draw_glass_rect(title_rect, alpha=55, radius=16)

        title = self.font.render("Pihkviinimasin", True, (255, 255, 255))
        self.screen.blit(title, title.get_rect(center=title_rect.center))

        # HUD (centered)
        hud_rect = pygame.Rect(0, TITLE_Y + 62, 300, 118)
        hud_rect.centerx = CENTER_X
        self._draw_glass_rect(hud_rect, alpha=40, radius=16)

        self.screen.blit(self.small_font.render(f"Debt: {self.debt}", True, (255, 120, 120)),
                         (hud_rect.x + 14, hud_rect.y + 12))
        self.screen.blit(self.small_font.render(f"Your account: {self.balance}", True, (170, 255, 170)),
                         (hud_rect.x + 14, hud_rect.y + 44))
        self.screen.blit(self.small_font.render(f"Bet: {self.bet_amount}", True, (220, 220, 220)),
                         (hud_rect.x + 14, hud_rect.y + 76))

        # REELS PANEL
        panel_rect = pygame.Rect(0, REEL_Y - 18, TOTAL_WIDTH + 36, REEL_HEIGHT + 36)
        panel_rect.centerx = CENTER_X
        self._draw_glass_rect(panel_rect, alpha=55, radius=16)

        for i in range(3):
            x = panel_rect.x + 18 + i * (REEL_WIDTH + REEL_GAP)
            y = REEL_Y
            reel_rect = pygame.Rect(x, y, REEL_WIDTH, REEL_HEIGHT)
            self._draw_glass_rect(reel_rect, alpha=85, radius=12)

            inner_rect = pygame.Rect(x + 5, y + 5, REEL_WIDTH - 10, REEL_HEIGHT - 10)
            img = self.symbol_surfaces[self.reel_indices[i]]
            self.screen.blit(img, img.get_rect(center=inner_rect.center))

        # ✅ MESSAGE BAR = AINUS INFOALA (ei teki uut kasti)
        if self.last_win_total > 0:
            lines = [
                f"Jackpot: {self.last_win_total}",
                f"Debt paid: {self.last_debt_payment}",
                f"You got: {self.last_personal_gain}",
            ]
            bar_height = 36 + 22 * len(lines)
        else:
            lines = [self.message]
            bar_height = 36

        msg_rect = pygame.Rect(0, REEL_Y + REEL_HEIGHT + 22, TOTAL_WIDTH + 36, bar_height)
        msg_rect.centerx = CENTER_X
        self._draw_glass_rect(msg_rect, alpha=45, radius=14)

        for i, text in enumerate(lines):
            surf = self.small_font.render(text, True, (255, 255, 255))
            self.screen.blit(
                surf,
                surf.get_rect(center=(msg_rect.centerx, msg_rect.y + 18 + i * 22))
            )

        # BUTTON
        btn_color = (100, 100, 100) if self.spinning else (0, 150, 0)
        btn_text = "SPINNING" if self.spinning else "SPIN"
        btn_surf = self.font.render(btn_text, True, (255, 255, 255))

        padding_x, padding_y = 20, 10
        self.spin_button_rect.size = (btn_surf.get_width() + padding_x * 2, btn_surf.get_height() + padding_y * 2)
        self.spin_button_rect.centerx = CENTER_X
        self.spin_button_rect.bottom = SCREEN_HEIGHT - 28

        self._draw_glass_rect(self.spin_button_rect.inflate(10, 10), alpha=40, radius=18)
        pygame.draw.rect(self.screen, btn_color, self.spin_button_rect, border_radius=12)
        pygame.draw.rect(self.screen, (255, 255, 255), self.spin_button_rect, 2, border_radius=12)
        self.screen.blit(btn_surf, btn_surf.get_rect(center=self.spin_button_rect.center))

    # ---------- LOOP ----------
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
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pihkviinimasin")
    SlotMachine(screen).run()


if __name__ == "__main__":
    main()
