"""Pygame presentation, input, animation and local preferences for the lounge."""
import array
import json
import math
from pathlib import Path
import random

import pygame as pg
from art import Art, INK, PANEL, CREAM, MUTED, GOLD, GREEN, MINT, RED
from cards import Card, LABELS, hand_value
from currency import Wallet
from managers import BlackjackManager, GoFishManager, MemoryManager

ROOT = Path(__file__).resolve().parent
SAVE = ROOT / 'savegame.json'
GAMES = {
    'blackjack': ('BLACKJACK', 'A little nerve. A little luck.', 'Beat the dealer without going over 21.', 'Spades'),
    'gofish': ('GO FISH', 'Good cards. Better company.', 'Read the table. Collect books of four.', 'Hearts'),
    'memory': ('MEMORY MATCH', 'For a sharp eye & a quiet mind.', 'Turn the cards. Find all twelve pairs.', 'Diamonds'),
}
RULES = {
    'blackjack': 'Get closer to 21 than the dealer without going over. Aces count as 1 or 11. Face cards count as 10.\n\nHit draws a card. Stand ends your hand. Double adds an equal stake, draws once, then stands. Split equal ranks into separate hands (up to four). Split aces get one card each.\n\nDealer stands on all 17s. A natural blackjack pays 3:2; half chips round down. Other wins pay 1:1. Ties return your stake. Split 21 is not a natural. Chips are just for fun.',
    'gofish': 'Collect four cards of a rank to make a book. The most books wins; ties are allowed.\n\nSelect a rank from your hand, select an opponent, then ASK. They give you every card of that rank. If they have none, choose where to fish. Every request ends the turn after any fishing, even if successful.\n\nEmpty hands draw one card, then ask; with an empty pool they skip. Computers remember 4 / 12 / 30 public events on Easy / Medium / Hard. Even Hard sometimes ignores its memory. Private draws stay private.',
    'memory': 'Find twelve matching pairs in as few moves as you can.\n\nClick two face-down cards. Matching pairs stay visible. A mismatch stays visible briefly, then turns back over. A move is two flips.\n\nThere is no timer or penalty for taking your time. Your best move count is saved locally. Aim for a perfect twelve!',
}


class CardGameApp:
    WIDTH, HEIGHT = 1280, 800

    def __init__(self, save_path=SAVE):
        pg.mixer.pre_init(22050, -16, 1, 512)
        pg.init()
        desktop_w, desktop_h = pg.display.get_desktop_sizes()[0]
        scale = min(1, (desktop_w - 80) / 1280, (desktop_h - 100) / 800)
        initial_size = (1280, 800) if pg.display.get_driver() == 'dummy' else (int(1280 * scale), int(800 * scale))
        self.window = pg.display.set_mode(initial_size, pg.RESIZABLE)
        pg.display.set_caption('The Velvet Table | Pixel Card Lounge')
        self.surface = pg.Surface((1280, 800))
        self.art = Art()
        icon = pg.Surface((32, 32))
        icon.fill(INK)
        self.art.suit(icon, 'Spades', (6, 4), 3, GOLD)
        pg.display.set_icon(icon)
        self.clock = pg.time.Clock()
        self.save_path = Path(save_path)
        self.settings = self.load()
        self.wallet = Wallet(self.settings['chips'])
        self.running = True
        self.scene = 'lobby'
        self.game_id = 'gofish'
        self.game = None
        self.modal = None
        self.buttons = []
        self.mouse = (-1, -1)
        self.focus = -1
        self.name_focus = False
        self.name_selected = False
        self.selected_rank = None
        self.selected_target = None
        self.next_action = 0
        self.game_started = 0
        self.log_offset = 0
        self.result_recorded = False
        self.toast = ''
        self.toast_until = 0
        self.sounds = self.make_sounds()

    def load(self):
        defaults = {'name': 'You', 'difficulty': 'medium', 'opponents': 2,
                    'chips': 1000, 'bet': 50, 'sound': True, 'fast': False,
                    'rounds': 0, 'best_memory': None}
        try:
            data = json.loads(self.save_path.read_text(encoding='utf-8'))
            if not isinstance(data, dict):
                return defaults
            for key in defaults:
                value = data.get(key)
                if key == 'name' and isinstance(value, str) and value.strip():
                    defaults[key] = value.strip()[:12]
                elif key == 'difficulty' and value in ('easy', 'medium', 'hard'):
                    defaults[key] = value
                elif key in ('chips', 'rounds') and type(value) is int and 0 <= value <= 10000000:
                    defaults[key] = value
                elif key == 'opponents' and type(value) is int and value in range(1, 5):
                    defaults[key] = value
                elif key == 'bet' and value in (10, 25, 50, 100):
                    defaults[key] = value
                elif key in ('sound', 'fast') and type(value) is bool:
                    defaults[key] = value
                elif key == 'best_memory' and type(value) is int and value >= 12:
                    defaults[key] = value
        except (OSError, ValueError):
            pass
        return defaults

    def save(self):
        self.settings['chips'] = self.wallet.balance
        try:
            temporary = self.save_path.with_suffix('.tmp')
            temporary.write_text(json.dumps(self.settings, indent=2), encoding='utf-8')
            temporary.replace(self.save_path)
        except OSError:
            self.toast = 'Could not save locally. You can keep playing.'
            self.toast_until = pg.time.get_ticks() + 4000

    def make_sounds(self):
        if not pg.mixer.get_init():
            return {}
        sounds = {}
        for name, frequency, duration in [('click', 440, .035), ('card', 660, .055), ('win', 880, .16)]:
            samples = array.array('h', (int(1600 * (1 - i / (22050 * duration)) *
                math.sin(2 * math.pi * frequency * i / 22050)) for i in range(int(22050 * duration))))
            sounds[name] = pg.mixer.Sound(buffer=samples)
        return sounds

    def sound(self, name='click'):
        if self.settings['sound'] and name in self.sounds:
            self.sounds[name].play()

    def panel(self, rect, color=PANEL, border=(66, 78, 72)):
        pg.draw.rect(self.surface, (10, 17, 20), pg.Rect(rect).move(0, 5))
        pg.draw.rect(self.surface, color, rect)
        pg.draw.rect(self.surface, border, rect, 2)

    def text(self, *args, **kwargs):
        return self.art.text(self.surface, *args, **kwargs)

    def button(self, rect, label, action, enabled=True, primary=False, selected=False):
        rect = pg.Rect(rect)
        hovered = rect.collidepoint(self.mouse) or len(self.buttons) == self.focus
        fill = GOLD if primary else (51, 72, 65) if selected else (37, 49, 48)
        if hovered and enabled:
            fill = (236, 202, 140) if primary else (62, 86, 73)
        if not enabled:
            fill = (32, 39, 40)
        pg.draw.rect(self.surface, (10, 18, 19), rect.move(0, 4))
        pg.draw.rect(self.surface, fill, rect)
        pg.draw.rect(self.surface, GOLD if selected or (hovered and enabled) else (76, 89, 77), rect, 2)
        self.text(label, (rect.centerx, rect.y + (rect.height - 18) // 2), 18,
                  INK if primary and enabled else CREAM if enabled else (89, 102, 96), center=True)
        self.buttons.append((rect, action, enabled))

    def hit_area(self, rect, action, enabled=True):
        if enabled and (pg.Rect(rect).collidepoint(self.mouse) or len(self.buttons) == self.focus):
            pg.draw.rect(self.surface, MINT, pg.Rect(rect).inflate(4, 4), 2)
        self.buttons.append((pg.Rect(rect), action, enabled))

    def choose_game(self, game_id):
        self.game_id = game_id
        self.modal = 'setup'
        self.name_focus = False
        self.focus = -1

    def start_game(self):
        self.settings['name'] = self.settings['name'].strip() or 'You'
        if self.game_id == 'blackjack':
            if self.wallet.balance < self.settings['bet']:
                return
            self.game = BlackjackManager(self.wallet, self.settings['bet'])
        elif self.game_id == 'gofish':
            self.game = GoFishManager(self.settings['name'], self.settings['opponents'], self.settings['difficulty'])
        else:
            self.game = MemoryManager()
        self.scene, self.modal = 'table', None
        self.selected_rank = self.selected_target = None
        self.game_started = pg.time.get_ticks()
        self.next_action = self.game_started + 1200
        self.log_offset = 0
        self.result_recorded = False
        self.focus = -1
        self.save()
        self.sound('card')

    def act(self, callback):
        callback()
        self.next_action = pg.time.get_ticks() + (550 if self.settings['fast'] else 1150)
        self.selected_rank = self.selected_target = None
        self.log_offset = 0
        self.save()
        self.sound('card')

    def set_option(self, key, value):
        self.settings[key] = value
        self.save()

    def edit_name(self):
        self.name_focus = True
        self.name_selected = True

    def leave(self):
        if self.game and not self.game.finished:
            self.modal = 'leave'
        else:
            self.to_lobby()

    def to_lobby(self):
        self.scene, self.modal = 'lobby', None
        self.game = None
        self.focus = -1
        self.save()

    def refill_chips(self):
        self.wallet.balance = 1000
        self.save()

    def header(self):
        pg.draw.rect(self.surface, (17, 23, 27), (0, 0, 1280, 79))
        pg.draw.line(self.surface, (66, 71, 61), (32, 78), (1248, 78), 2)
        self.art.suit(self.surface, 'Spades', (34, 23), 4, GOLD)
        self.text('THE VELVET TABLE', (82, 21), 22, CREAM)
        self.text('A PIXEL CARD LOUNGE', (83, 48), 12, MUTED)
        self.text(f'{self.wallet.balance:,} CHIPS', (685, 30), 18, GOLD)
        self.button((852, 21, 120, 37), 'SOUND ' + ('ON' if self.settings['sound'] else 'OFF'),
                    lambda: self.set_option('sound', not self.settings['sound']))
        self.button((984, 21, 108, 37), 'PACE ' + ('2X' if self.settings['fast'] else '1X'),
                    lambda: self.set_option('fast', not self.settings['fast']))
        self.button((1104, 21, 144, 37), 'LOBBY' if self.scene == 'table' else 'QUIT',
                    self.leave if self.scene == 'table' else self.quit)

    def lobby(self):
        self.panel((32, 104, 1216, 326), (27, 43, 40), (75, 91, 72))
        self.text('EST. 2026   /   PULL UP A CHAIR', (62, 128), 14, MINT)
        self.art.pixel_text(self.surface, 'GOOD CARDS.', (62, 175), 5, CREAM)
        self.art.pixel_text(self.surface, 'GREAT COMPANY.', (62, 228), 5, GOLD)
        self.text('The lights are low. The table is ready.', (62, 295), 19)
        self.text('Pick a game and stay a while.', (62, 325), 19, MUTED)
        self.text('3 TABLES OPEN', (62, 388), 14, MINT)
        pg.draw.circle(self.surface, MINT, (211, 396), 4)
        # A little still life, drawn at pixel resolution rather than downloaded.
        hero_table = pg.transform.scale(self.art.table, (520, 304))
        self.surface.blit(hero_table, (712, 119))
        for card, x, y, angle in [(Card('Jack', 'Clubs'), 850, 182, 13),
                                 (Card('Queen', 'Hearts'), 919, 164, 0),
                                 (Card('Ace', 'Spades'), 987, 186, -13)]:
            canvas = pg.Surface((112, 152), pg.SRCALPHA)
            self.art.card(canvas, card, (4, 4, 96, 136))
            self.surface.blit(pg.transform.rotate(canvas, angle), (x, y))
        for x, y, color in [(839, 334, RED), (863, 352, RED), (1105, 316, GOLD), (1124, 335, GOLD)]:
            self.art.chip(self.surface, (x, y), color)
        self.text('CHOOSE YOUR TABLE', (32, 455), 16, GOLD)
        for i, (game_id, (title, subtitle, description, suit)) in enumerate(GAMES.items()):
            x = 32 + i * 412
            self.panel((x, 489, 392, 240))
            self.text(f'0{i + 1}', (x + 22, 509), 14, MUTED)
            self.art.suit(self.surface, suit, (x + 329, 509), 4, GOLD if i != 1 else RED)
            self.art.pixel_text(self.surface, title, (x + 22, 548), 3, CREAM)
            self.text(subtitle, (x + 22, 585), 15, GOLD)
            self.text(description, (x + 22, 613), 14, MUTED)
            self.button((x + 22, 663, 348, 43), 'TAKE A SEAT  >', lambda g=game_id: self.choose_game(g), primary=i == 1)
        self.text('HANDCRAFTED PIXELS  /  CLASSIC CARD GAMES', (32, 762), 13, MUTED)
        self.text(f'{self.settings["rounds"]} ROUNDS PLAYED   /   MAKE YOURSELF AT HOME', (777, 762), 13, MUTED)

    def table_base(self):
        title = GAMES[self.game_id][0]
        self.art.pixel_text(self.surface, title, (32, 104), 3, CREAM)
        self.text('TABLE ' + {'blackjack': '01', 'gofish': '02', 'memory': '03'}[self.game_id], (32, 139), 13, MUTED)
        self.button((840, 100, 144, 39), 'HOW TO PLAY', lambda: setattr(self, 'modal', 'rules'))
        self.surface.blit(self.art.table, (32, 165))
        self.sidebar()

    def sidebar(self):
        self.panel((1012, 100, 236, 629), (24, 33, 36))
        self.text('TABLE NOTES', (1032, 122), 18, GOLD)
        self.text('THE STORY SO FAR', (1032, 149), 12, MUTED)
        pg.draw.line(self.surface, (64, 81, 70), (1032, 177), (1228, 177))
        messages = self.game.messages
        end = max(0, len(messages) - self.log_offset)
        # Fit the newest messages into the available height, including wrapping.
        shown = []
        used = 0
        for message in reversed(messages[:end]):
            lines, line = 1, ''
            for word in message.split():
                candidate = (line + ' ' + word).strip()
                if self.art.font(14).size(candidate)[0] > 196 and line:
                    lines += 1
                    line = word
                else:
                    line = candidate
            height = lines * 18 + 17
            if used + height > 430:
                break
            shown.insert(0, (message, height))
            used += height
        y = 195
        for i, (message, height) in enumerate(shown):
            color = CREAM if i == len(shown) - 1 and not self.log_offset else MUTED
            self.art.wrap(self.surface, message, (1032, y, 196, height), 14, color, 4)
            y += height
        self.text('SCROLL HERE FOR HISTORY', (1032, 649), 11, MUTED)
        self.text('PRIVATE CARDS STAY HIDDEN', (1032, 680), 11, GOLD)

    def status_bar(self, title, hint):
        self.panel((32, 740, 1216, 43), (25, 36, 37))
        self.text(title, (48, 751), 17, GOLD)
        self.text(hint, (440, 753), 14, MUTED)

    def deal_offset(self, index=0):
        elapsed = pg.time.get_ticks() - self.game_started - index * 65
        return int(max(0, 1 - max(0, elapsed) / 450) ** 2 * 100)

    def blackjack(self):
        g = self.game
        self.art.portrait(self.surface, (465, 162, 64, 64), 1, g.phase == 'dealer')
        self.text('THE DEALER', (497, 233), 17, CREAM, center=True)
        hidden = g.phase == 'player'
        score = f'{g.dealer[0].value} + ?' if hidden else str(hand_value(g.dealer))
        self.text('TOTAL ' + score, (497, 257), 14, GOLD, center=True)
        spacing = min(100, 480 // max(1, len(g.dealer)))
        start = 497 - (spacing * (len(g.dealer) - 1) + 88) // 2
        for i, card in enumerate(g.dealer):
            self.art.card(self.surface, card, (start + i * spacing, 290 - self.deal_offset(i), 88, 124), back=hidden and i == 1)
        self.text('BLACKJACK PAYS 3 : 2', (500, 441), 16, (110, 148, 112), center=True)
        self.text('DEALER STANDS ON 17', (500, 464), 12, (110, 148, 112), center=True)
        for i, hand in enumerate(g.hands):
            count = len(g.hands)
            region = 850 // count
            center = 80 + region * i + region // 2
            width = 80 if count <= 2 else 62
            height = int(width * 1.42)
            spacing = min(width + 8, (region - width - 20) // max(1, len(hand.cards) - 1))
            left = center - (spacing * (len(hand.cards) - 1) + width) // 2
            for j, card in enumerate(hand.cards):
                self.art.card(self.surface, card, (left + j * spacing, 512 + self.deal_offset(j), width, height),
                              selected=i == g.active and g.phase == 'player' and j == 0)
            label = hand.result if g.finished else f'{hand.score} POINTS'
            self.text(label, (center, 642), 16, GOLD if i == g.active else CREAM, center=True)
            self.text(f'{hand.bet} CHIPS', (center, 664), 12, MUTED, center=True)
        if not g.finished:
            for i, (label, action, enabled) in enumerate([
                ('HIT [H]', 'hit', g.phase == 'player'), ('STAND [S]', 'stand', g.phase == 'player'),
                ('DOUBLE [D]', 'double', g.can_double), ('SPLIT [P]', 'split', g.can_split)]):
                self.button((160 + i * 174, 689, 160, 38), label,
                            lambda a=action: self.act(lambda: g.action(a)), enabled, primary=i == 0)
        self.status_bar('YOUR MOVE' if g.phase == 'player' else 'DEALER AT WORK' if not g.finished else 'HAND COMPLETE',
                        'Choose an action above. Play chips only.' if g.phase == 'player' else g.messages[-1])

    def gofish(self):
        g = self.game
        human = g.players[0]
        can_ask = g.current == 0 and g.phase == 'ask'
        for i, player in enumerate(g.players[1:]):
            width = 850 // (len(g.players) - 1)
            cx = 80 + width * i + width // 2
            active = g.current == i + 1 and not g.finished
            selected = self.selected_target == player.name
            rect = pg.Rect(cx - 75, 175, 150, 176)
            if selected or active:
                pg.draw.rect(self.surface, GOLD if selected else MINT, rect, 2)
            self.art.portrait(self.surface, (cx - 27, 187, 54, 54), i, active)
            self.text(player.name.upper(), (cx, 250), 16, GOLD if selected else CREAM, center=True)
            self.text(f'{player.count} CARDS / {len(player.sets)} BOOKS', (cx, 274), 12, MUTED, center=True)
            for j in range(min(player.count, 5)):
                self.art.card(self.surface, None, (cx - 36 + j * 12, 299, 32, 45), back=True)
            self.hit_area(rect, lambda name=player.name: setattr(self, 'selected_target', name), can_ask and player.hasCards())
        self.art.pixel_text(self.surface, 'GO FISH', (397, 372), 4, (78, 126, 94))
        if len(g.deck):
            for i in range(3):
                self.art.card(self.surface, None, (465 + i * 2, 417 - i * 3, 60, 84), back=True)
        self.text(f'{len(g.deck)} IN THE POOL', (498, 510), 13, MINT, center=True)
        self.text(f'{self.settings["name"].upper()}  /  {len(human.sets)} BOOKS', (76, 546), 16, GOLD)
        book_labels = ' '.join(LABELS[rank] for rank in human.sets) or 'Collect four of a rank'
        self.text(book_labels, (610, 546), 13, MUTED)
        ranks = [(rank, cards) for rank, cards in human.hand.items() if cards]
        card_w = min(72, 810 // max(len(ranks), 1) - 5)
        step = card_w + 8
        left = 498 - (len(ranks) * step - 8) // 2
        for i, (rank, cards) in enumerate(ranks):
            selected = rank == self.selected_rank
            rect = pg.Rect(left + i * step, 572 - (9 if selected else 0) + self.deal_offset(i), card_w, 94)
            self.art.card(self.surface, cards[0], rect, selected=selected)
            self.text(f'x{len(cards)}', (rect.centerx, rect.bottom + 5), 13, GOLD, center=True)
            self.hit_area(rect, lambda r=rank: setattr(self, 'selected_rank', r), can_ask)
        if not ranks:
            self.text('Your hand is empty.', (498, 605), 18, MUTED, center=True)
        if g.current == 0 and g.phase in ('fish', 'refill'):
            for i, (label, index) in enumerate([('TOP', 0), ('CENTER', (len(g.deck) - 1) // 2), ('BOTTOM', len(g.deck) - 1)]):
                self.button((280 + i * 151, 689, 140, 38), label,
                            lambda idx=index: self.act(lambda: g.fish(idx)), primary=i == 0)
            self.status_bar('CAST YOUR LINE', 'Choose where to draw. A refill lets you ask; fishing ends the turn.')
        elif can_ask:
            self.button((380, 689, 236, 38), 'ASK FOR CARDS',
                        lambda: self.act(lambda: g.ask(self.selected_rank, self.selected_target)),
                        bool(self.selected_rank and self.selected_target), primary=True)
            self.status_bar('YOUR TURN', 'Select a card rank, select an opponent, then ask.')
        elif not g.finished:
            self.text(g.player.name.upper() + ' IS THINKING' + '.' * (1 + pg.time.get_ticks() // 450 % 3),
                      (498, 698), 17, CREAM, center=True)
            self.status_bar('AROUND THE TABLE', 'One request per turn. Watch the table notes for clues.')
        else:
            self.status_bar('ALL BOOKS COLLECTED', g.result)

    def memory(self):
        g = self.game
        self.text(f'{len(g.matched) // 2} / 12 PAIRS', (172, 170), 17, GOLD)
        self.text(f'{g.moves} MOVES', (655, 170), 17, MINT)
        for index, card in enumerate(g.cards):
            col, row = index % 6, index // 6
            rect = pg.Rect(172 + col * 112, 210 + row * 116, 76, 100)
            visible = index in g.matched or index in g.flipped
            self.art.card(self.surface, card, rect, back=not visible, dim=index in g.matched)
            if index in g.matched:
                self.text('+', (rect.right - 14, rect.y + 5), 18, GOLD)
            self.hit_area(rect, lambda idx=index: self.act(lambda: g.flip(idx)),
                          g.phase == 'choose' and not visible)
        best = self.settings['best_memory']
        self.text(f'PERSONAL BEST: {best if best else "--"} MOVES', (498, 688), 14, GOLD, center=True)
        self.status_bar('FIND YOUR PAIR' if g.phase == 'choose' else 'TAKE A LOOK' if not g.finished else 'BEAUTIFULLY MATCHED',
                        'Click two cards. No timer. Just a little concentration.')

    def result_banner(self):
        self.panel((260, 350, 480, 169), (22, 35, 35), GOLD)
        self.text('ROUND COMPLETE', (500, 369), 14, GOLD, center=True)
        size = 24
        while self.art.font(size).size(self.game.result)[0] > 432 and size > 14:
            size -= 1
        self.text(self.game.result, (500, 398), size, CREAM, center=True)
        self.button((282, 459, 210, 40), 'PLAY AGAIN', lambda: self.choose_game(self.game_id), primary=True)
        self.button((508, 459, 210, 40), 'BACK TO LOBBY', self.to_lobby)

    def draw_modal(self):
        veil = pg.Surface((1280, 800), pg.SRCALPHA)
        veil.fill((6, 12, 17, 205))
        self.surface.blit(veil, (0, 0))
        self.buttons = []
        self.panel((300, 127, 680, 546), (27, 39, 40), GOLD)
        self.text('THE VELVET TABLE', (332, 152), 13, GOLD)
        if self.modal == 'setup':
            self.art.pixel_text(self.surface, GAMES[self.game_id][0], (332, 188), 4, CREAM)
            self.text('Make yourself comfortable.', (332, 233), 17, MUTED)
            self.text('YOUR NAME', (332, 282), 14, GOLD)
            self.button((490, 273, 250, 40), self.settings['name'] + ('_' if self.name_focus else ''),
                        self.edit_name, selected=self.name_focus)
            if self.game_id == 'gofish':
                self.text('OPPONENTS', (332, 347), 14, GOLD)
                for i in range(1, 5):
                    self.button((490 + (i - 1) * 76, 335, 62, 40), str(i),
                                lambda n=i: self.set_option('opponents', n), selected=self.settings['opponents'] == i)
                self.text('DIFFICULTY', (332, 407), 14, GOLD)
                for i, level in enumerate(('easy', 'medium', 'hard')):
                    self.button((490 + i * 144, 395, 132, 40), level.upper(),
                                lambda v=level: self.set_option('difficulty', v), selected=self.settings['difficulty'] == level)
                memory, mistake = self.game_memory()
                self.art.wrap(self.surface, f'Remembers {memory} public events. Ignores memory {int(mistake * 100)}% of the time. One request per turn, always.',
                              (332, 475, 588, 65), 16, MUTED)
            elif self.game_id == 'blackjack':
                self.text('YOUR STAKE', (332, 347), 14, GOLD)
                for i, bet in enumerate((10, 25, 50, 100)):
                    self.button((490 + i * 100, 335, 88, 40), str(bet),
                                lambda b=bet: self.set_option('bet', b), selected=self.settings['bet'] == bet)
                self.text(f'Available: {self.wallet.balance:,} play chips', (332, 411), 18, CREAM)
                self.art.wrap(self.surface, 'You versus the dealer. Hit, stand, split or double. Blackjack pays 3:2. Chips have no cash value.',
                              (332, 455, 590, 80), 16, MUTED)
                if self.wallet.balance < 10:
                    self.button((650, 402, 290, 40), 'REFILL TO 1,000 CHIPS', self.refill_chips, primary=True)
            else:
                self.art.wrap(self.surface, 'A quiet table for one. Twenty-four cards, twelve pairs. Find them all in as few moves as you can. No clock to race.',
                              (332, 345, 580, 120), 20, CREAM, 10)
                self.text(f'YOUR BEST: {self.settings["best_memory"] or "--"} MOVES', (332, 487), 16, GOLD)
            self.button((332, 587, 176, 48), 'CANCEL', lambda: setattr(self, 'modal', None))
            affordable = self.game_id != 'blackjack' or self.wallet.balance >= self.settings['bet']
            self.button((528, 587, 420, 48), 'DEAL ME IN  >' if affordable else 'CHOOSE A SMALLER STAKE', self.start_game, affordable, primary=True)
        elif self.modal == 'rules':
            self.art.pixel_text(self.surface, 'HOUSE RULES', (332, 192), 4, CREAM)
            self.art.wrap(self.surface, RULES[self.game_id], (332, 248, 604, 325), 18, CREAM, 7)
            self.button((332, 587, 616, 48), 'BACK TO THE TABLE', lambda: setattr(self, 'modal', None), primary=True)
        elif self.modal == 'leave':
            self.art.pixel_text(self.surface, 'LEAVE THE TABLE', (332, 192), 4, CREAM)
            message = 'This round is still in play. Leaving ends it.'
            if self.game_id == 'blackjack':
                message += ' Chips already staked will not be returned.'
            self.art.wrap(self.surface, message, (332, 285, 590, 150), 21, CREAM, 10)
            self.button((332, 587, 290, 48), 'KEEP PLAYING', lambda: setattr(self, 'modal', None), primary=True)
            self.button((642, 587, 306, 48), 'LEAVE ROUND', self.to_lobby)

    def game_memory(self):
        from players import CompGoFishPlayer
        return CompGoFishPlayer.DIFFICULTIES[self.settings['difficulty']]

    def render(self):
        self.buttons = []
        self.surface.blit(self.art.background, (0, 0))
        self.header()
        if self.scene == 'lobby':
            self.lobby()
        else:
            self.table_base()
            {'blackjack': self.blackjack, 'gofish': self.gofish, 'memory': self.memory}[self.game_id]()
            if self.game.finished:
                self.result_banner()
        if self.modal:
            self.draw_modal()
        if self.toast and pg.time.get_ticks() < self.toast_until:
            self.panel((280, 91, 720, 42), INK, GOLD)
            self.text(self.toast, (640, 102), 16, GOLD, center=True)
        width, height = self.window.get_size()
        ratio = min(width / 1280, height / 800)
        size = (max(1, int(1280 * ratio)), max(1, int(800 * ratio)))
        self.viewport = pg.Rect((width - size[0]) // 2, (height - size[1]) // 2, *size)
        self.window.fill((9, 14, 18))
        self.window.blit(pg.transform.scale(self.surface, size), self.viewport)
        pg.display.flip()

    def virtual_pos(self, pos):
        width, height = self.window.get_size()
        ratio = min(width / 1280, height / 800)
        return ((pos[0] - (width - 1280 * ratio) / 2) / ratio,
                (pos[1] - (height - 800 * ratio) / 2) / ratio)

    def handle_event(self, event):
        if event.type == pg.QUIT:
            self.quit()
        elif event.type == pg.MOUSEMOTION:
            self.mouse = self.virtual_pos(event.pos)
            self.focus = -1
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            self.mouse = self.virtual_pos(event.pos)
            if not pg.Rect(490, 273, 250, 40).collidepoint(self.mouse):
                self.name_focus = False
            for rect, callback, enabled in reversed(self.buttons):
                if enabled and rect.collidepoint(self.mouse):
                    self.sound()
                    callback()
                    break
        elif event.type == pg.MOUSEWHEEL and self.scene == 'table' and not self.modal and self.mouse[0] > 1012:
            self.log_offset = max(0, min(max(0, len(self.game.messages) - 1), self.log_offset + event.y))
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                if self.modal:
                    self.modal = None
                elif self.scene == 'table':
                    self.leave()
            elif self.modal == 'setup' and self.name_focus:
                if event.key == pg.K_BACKSPACE:
                    self.settings['name'] = '' if self.name_selected else self.settings['name'][:-1]
                    self.name_selected = False
                elif event.key == pg.K_a and event.mod & pg.KMOD_CTRL:
                    self.name_selected = True
                elif event.key in (pg.K_RETURN, pg.K_TAB):
                    self.name_focus = False
                elif event.unicode and event.unicode.isprintable():
                    if self.name_selected:
                        self.settings['name'] = ''
                        self.name_selected = False
                    if len(self.settings['name']) < 12:
                        self.settings['name'] += event.unicode
            elif event.key == pg.K_TAB:
                available = [i for i, (_, _, enabled) in enumerate(self.buttons) if enabled]
                if available:
                    direction = -1 if event.mod & pg.KMOD_SHIFT else 1
                    offset = available.index(self.focus) if self.focus in available else (-1 if direction == 1 else 0)
                    self.focus = available[(offset + direction) % len(available)]
            elif event.key in (pg.K_RETURN, pg.K_SPACE) and 0 <= self.focus < len(self.buttons):
                _, callback, enabled = self.buttons[self.focus]
                if enabled:
                    callback()
            elif not self.modal and self.scene == 'table' and self.game_id == 'blackjack' and self.game.phase == 'player':
                action = {pg.K_h: 'hit', pg.K_s: 'stand', pg.K_d: 'double', pg.K_p: 'split'}.get(event.key)
                if action and (action != 'split' or self.game.can_split) and (action != 'double' or self.game.can_double):
                    self.act(lambda: self.game.action(action))

    def update(self):
        if self.scene != 'table' or self.modal:
            return
        now = pg.time.get_ticks()
        if self.game.finished:
            if not self.result_recorded:
                self.result_recorded = True
                self.settings['rounds'] += 1
                if self.game_id == 'memory':
                    old = self.settings['best_memory']
                    self.settings['best_memory'] = min(old, self.game.moves) if old else self.game.moves
                self.save()
                self.sound('win')
            return
        if now >= self.next_action:
            revision = self.game.revision
            self.game.step()
            delay = 1000 if self.game_id == 'memory' else 500 if self.settings['fast'] else 1100
            self.next_action = now + delay
            if revision != self.game.revision:
                self.sound('card')
                self.log_offset = 0
                self.save()

    def quit(self):
        self.save()
        self.running = False

    def run(self):
        self.render()
        try:
            while self.running:
                for event in pg.event.get():
                    self.handle_event(event)
                    # Rebuild hit targets after each action to avoid stale double clicks.
                    self.render()
                self.update()
                self.render()
                self.clock.tick(60)
        finally:
            self.save()
            pg.quit()

    def smoke_test(self, directory):
        """Render real screens without a display; do not touch the user's save."""
        output = Path(directory)
        output.mkdir(parents=True, exist_ok=True)
        self.save_path = output / 'smoke-save.json'
        self.wallet.balance = 1000
        self.settings['bet'] = 50
        random.seed(19)
        self.render()
        pg.image.save(self.surface, output / 'lobby.png')
        for game_id in GAMES:
            self.to_lobby()
            self.choose_game(game_id)
            self.render()
            pg.image.save(self.surface, output / f'{game_id}-setup.png')
            self.start_game()
            self.game_started = -10000
            self.render()
            pg.image.save(self.surface, output / f'{game_id}.png')
            self.modal = 'rules'
            self.render()
            pg.image.save(self.surface, output / f'{game_id}-rules.png')
            self.modal = None
        # Exercise dense layouts and settled states as well as fresh deals.
        self.to_lobby()
        self.game_id = 'gofish'
        self.settings['opponents'] = 4
        self.start_game()
        self.game_started = -10000
        for rank in LABELS:
            if not self.game.players[0].hand[rank]:
                self.game.players[0].drawCard(Card(rank))
        self.selected_rank = 'Ace'
        self.selected_target = self.game.players[1].name
        for _ in range(7):
            self.game.say('Mabel asks Jasper for Queens. Jasper hands over three cards.')
        self.render()
        pg.image.save(self.surface, output / 'gofish-dense.png')
        self.to_lobby()
        self.game_id = 'blackjack'
        self.start_game()
        self.game_started = -10000
        from players import BlackjackHand
        self.game.phase = 'player'
        self.game.hands = [BlackjackHand([Card('Eight'), Card('Two'), Card('Five')], 50, split=True) for _ in range(4)]
        self.render()
        pg.image.save(self.surface, output / 'blackjack-split.png')
        self.game.phase = 'finished'
        self.game.result = '+100 chips'
        self.render()
        pg.image.save(self.surface, output / 'result.png')
        pg.quit()
        print(f'Rendered lobby, setup, table and rules screens to {output.resolve()}')
