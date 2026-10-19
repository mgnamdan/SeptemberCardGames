"""Original procedural pixel art: cards, portraits, chips, felt and lettering."""
import random
import pygame as pg
from cards import RANKS

INK = (19, 24, 29)
PANEL = (29, 38, 42)
CREAM = (244, 231, 197)
MUTED = (151, 168, 155)
GOLD = (218, 178, 104)
GREEN = (29, 79, 65)
MINT = (146, 201, 163)
RED = (187, 76, 73)

GLYPHS = {
    'A': ['01110','11011','11011','11111','11011','11011','11011'],
    'B': ['11110','11011','11011','11110','11011','11011','11110'],
    'C': ['01111','11000','11000','11000','11000','11000','01111'],
    'D': ['11110','11011','11011','11011','11011','11011','11110'],
    'E': ['11111','11000','11000','11110','11000','11000','11111'],
    'F': ['11111','11000','11000','11110','11000','11000','11000'],
    'G': ['01111','11000','11000','11011','11011','11011','01111'],
    'H': ['11011','11011','11011','11111','11011','11011','11011'],
    'I': ['11111','00100','00100','00100','00100','00100','11111'],
    'J': ['00111','00011','00011','00011','11011','11011','01110'],
    'K': ['11011','11011','11110','11100','11110','11011','11011'],
    'L': ['11000','11000','11000','11000','11000','11000','11111'],
    'M': ['10001','11011','11111','10101','10001','10001','10001'],
    'N': ['11001','11101','11101','11011','11011','11011','11001'],
    'O': ['01110','11011','11011','11011','11011','11011','01110'],
    'P': ['11110','11011','11011','11110','11000','11000','11000'],
    'Q': ['01110','11011','11011','11011','11111','01110','00011'],
    'R': ['11110','11011','11011','11110','11100','11010','11011'],
    'S': ['01111','11000','11000','01110','00011','00011','11110'],
    'T': ['11111','00100','00100','00100','00100','00100','00100'],
    'U': ['11011','11011','11011','11011','11011','11011','01110'],
    'V': ['11011','11011','11011','11011','11011','01110','00100'],
    'W': ['10001','10001','10001','10101','11111','11011','10001'],
    'X': ['11011','11011','01110','00100','01110','11011','11011'],
    'Y': ['11011','11011','01110','00100','00100','00100','00100'],
    'Z': ['11111','00011','00110','00100','01100','11000','11111'],
    '0': ['01110','11011','11011','11011','11011','11011','01110'],
    '1': ['00100','01100','00100','00100','00100','00100','01110'],
    '2': ['01110','11011','00011','00110','01100','11000','11111'],
    '3': ['11110','00011','00011','01110','00011','00011','11110'],
    '4': ['11011','11011','11011','11111','00011','00011','00011'],
    '5': ['11111','11000','11000','11110','00011','00011','11110'],
    '6': ['01110','11000','11000','11110','11011','11011','01110'],
    '7': ['11111','00011','00011','00110','01100','01100','01100'],
    '8': ['01110','11011','11011','01110','11011','11011','01110'],
    '9': ['01110','11011','11011','01111','00011','00011','01110'],
}
SUIT_PIXELS = {
    'Hearts': ['0110110','1111111','1111111','0111110','0011100','0001000'],
    'Diamonds': ['0001000','0011100','0111110','1111111','0111110','0011100','0001000'],
    'Spades': ['0001000','0011100','0111110','1111111','1111111','0101010','0001000','0011100'],
    'Clubs': ['0011100','0011100','0001000','0111110','1111111','0111110','0001000','0011100'],
}


class Art:
    def __init__(self):
        self.fonts = {}
        self.cards = {}
        self.background = pg.Surface((1280, 800))
        self.background.fill(INK)
        rng = random.Random(101)
        for y in range(0, 800, 4):
            pg.draw.line(self.background, (21 + y // 180, 27, 30), (0, y), (1280, y))
        for _ in range(3300):
            x, y = rng.randrange(1280), rng.randrange(800)
            pg.draw.rect(self.background, (31, 36, 37), (x, y, 2, 2))
        self.table = self.make_table()

    def font(self, size):
        if size not in self.fonts:
            self.fonts[size] = pg.font.SysFont('consolas,dejavusansmono,monospace', size)
        return self.fonts[size]

    def text(self, surface, text, pos, size=18, color=CREAM, center=False):
        image = self.font(size).render(str(text), False, color)
        rect = image.get_rect(midtop=pos) if center else image.get_rect(topleft=pos)
        surface.blit(image, rect)
        return rect

    def wrap(self, surface, text, rect, size=16, color=MUTED, spacing=5):
        x, y, width, height = rect
        for paragraph in text.split('\n'):
            line = ''
            for word in paragraph.split():
                candidate = (line + ' ' + word).strip()
                if self.font(size).size(candidate)[0] > width and line:
                    if y + size > rect[1] + height:
                        return y
                    self.text(surface, line, (x, y), size, color)
                    y += size + spacing
                    line = word
                else:
                    line = candidate
            if y + size <= rect[1] + height:
                self.text(surface, line, (x, y), size, color)
            y += size + spacing
        return y

    def pixel_text(self, surface, text, pos, scale=4, color=GOLD):
        x, y = pos
        for letter in text.upper():
            for row, pixels in enumerate(GLYPHS.get(letter, [])):
                for col, pixel in enumerate(pixels):
                    if pixel == '1':
                        pg.draw.rect(surface, color, (x + col * scale, y + row * scale, scale, scale))
            x += 6 * scale

    def suit(self, surface, suit, pos, scale=3, color=None):
        color = color or (RED if suit in ('Hearts', 'Diamonds') else INK)
        for row, pixels in enumerate(SUIT_PIXELS[suit]):
            for col, pixel in enumerate(pixels):
                if pixel == '1':
                    pg.draw.rect(surface, color, (pos[0] + col * scale, pos[1] + row * scale, scale, scale))

    def card(self, surface, card, rect, back=False, selected=False, dim=False):
        rect = pg.Rect(rect)
        key = (card, rect.size, back, dim)
        if key not in self.cards:
            small = pg.Surface((48, 68), pg.SRCALPHA)
            pg.draw.rect(small, (177, 159, 123), (0, 0, 48, 68))
            pg.draw.rect(small, CREAM, (1, 1, 46, 65))
            if back:
                pg.draw.rect(small, (46, 67, 80), (3, 3, 42, 60))
                for y in range(5, 62, 5):
                    for x in range(5, 44, 5):
                        pg.draw.rect(small, (72, 99, 109), (x, y, 2, 2))
                pg.draw.rect(small, GOLD, (7, 8, 34, 50), 1)
                self.suit(small, 'Spades', (14, 23), 3, GOLD)
            elif card:
                color = RED if card.suit in ('Hearts', 'Diamonds') else INK
                label = pg.font.Font(None, 15).render(card.label, False, color)
                small.blit(label, (4, 3))
                small.blit(pg.transform.rotate(label, 180), (43 - label.get_width(), 52))
                self.suit(small, card.suit, (4, 14), 1, color)
                self.suit(small, card.suit, (37, 43), 1, color)
                if card.rank in ('Jack', 'Queen', 'King'):
                    pg.draw.rect(small, (224, 207, 165), (13, 20, 23, 28))
                    self.suit(small, card.suit, (17, 26), 2, color)
                    pg.draw.rect(small, GOLD, (17, 21, 14, 3))
                    for x in (17, 23, 29):
                        pg.draw.rect(small, GOLD, (x, 18, 2, 5))
                elif card.rank == 'Ace':
                    self.suit(small, card.suit, (13, 24), 3, color)
                else:
                    count = RANKS.index(card.rank) + 2
                    positions = [(15, 23), (29, 23), (15, 34), (29, 34), (15, 45), (29, 45),
                                 (22, 18), (22, 29), (22, 40), (22, 50)]
                    for x, y in positions[:count]:
                        self.suit(small, card.suit, (x - 3, y - 3), 1, color)
            if dim:
                shade = pg.Surface((48, 68), pg.SRCALPHA)
                shade.fill((20, 50, 39, 125))
                small.blit(shade, (0, 0))
            self.cards[key] = pg.transform.scale(small, rect.size)
        pg.draw.rect(surface, (12, 24, 25), rect.move(4, 6))
        if selected:
            pg.draw.rect(surface, GOLD, rect.inflate(8, 8), 3)
        surface.blit(self.cards[key], rect)

    def portrait(self, surface, rect, seed=0, active=False):
        colors = [(174, 101, 74), (114, 141, 145), (164, 120, 154), (179, 156, 91), (90, 148, 118)]
        s = pg.Surface((20, 20))
        s.fill((35, 48, 48))
        pg.draw.rect(s, colors[seed % len(colors)], (3, 14, 14, 6))
        pg.draw.rect(s, (111, 70, 48), (6, 4, 9, 10))
        pg.draw.rect(s, (226, 175, 122), (7, 6, 7, 8))
        pg.draw.rect(s, (240, 196, 143), (7, 7, 5, 4))
        pg.draw.rect(s, INK, (8, 9, 1, 1))
        pg.draw.rect(s, INK, (12, 9, 1, 1))
        pg.draw.rect(s, (135, 76, 61), (10, 12, 2, 1))
        if seed % 2:
            pg.draw.rect(s, colors[seed % len(colors)], (5, 3, 10, 3))
            pg.draw.rect(s, GOLD, (4, 6, 12, 1))
        else:
            pg.draw.rect(s, (62, 40, 36), (6, 4, 9, 3))
            pg.draw.rect(s, (62, 40, 36), (5, 7, 2, 7))
        pg.draw.rect(s, CREAM, (9, 15, 3, 2))
        surface.blit(pg.transform.scale(s, pg.Rect(rect).size), rect)
        pg.draw.rect(surface, GOLD if active else (72, 89, 80), rect, 2)

    def chip(self, surface, pos, color=RED, radius=18):
        x, y = pos
        pg.draw.circle(surface, (14, 24, 26), (x + 3, y + 5), radius)
        pg.draw.circle(surface, color, (x, y), radius)
        pg.draw.circle(surface, CREAM, (x, y), radius - 4, 2)
        for dx, dy in ((0, -radius), (0, radius - 5), (-radius, 0), (radius - 5, 0)):
            pg.draw.rect(surface, CREAM, (x + dx - 2, y + dy - 2, 5, 5))

    def make_table(self):
        small = pg.Surface((476, 282), pg.SRCALPHA)
        pg.draw.ellipse(small, (8, 18, 21), (0, 10, 476, 272))
        pg.draw.ellipse(small, (80, 51, 39), (0, 0, 476, 266))
        pg.draw.ellipse(small, (143, 102, 62), (4, 3, 468, 258), 2)
        pg.draw.ellipse(small, (41, 33, 29), (11, 9, 454, 248))
        pg.draw.ellipse(small, (42, 91, 70), (17, 15, 442, 236))
        pg.draw.ellipse(small, GREEN, (20, 18, 436, 230))
        rng = random.Random(7)
        for _ in range(6000):
            x, y = rng.randrange(24, 451), rng.randrange(22, 243)
            if ((x - 238) / 210) ** 2 + ((y - 133) / 108) ** 2 < 1:
                small.set_at((x, y), (32, 83, 67) if x % 2 else (27, 75, 62))
        pg.draw.ellipse(small, (76, 115, 83), (30, 29, 416, 208), 1)
        return pg.transform.scale(small, (952, 564))
