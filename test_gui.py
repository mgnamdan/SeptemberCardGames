"""Offscreen input and navigation tests through Pygame's real event handlers."""
import json
import os
import tempfile
import unittest
from pathlib import Path

os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame as pg
from gui import CardGameApp


class GuiTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / 'save.json'
        self.app = CardGameApp(self.path)
        self.app.render()

    def tearDown(self):
        pg.quit()
        self.temp.cleanup()

    def click(self, x, y):
        self.app.handle_event(pg.event.Event(pg.MOUSEBUTTONDOWN, pos=(x, y), button=1))
        self.app.render()

    def key(self, key, unicode=''):
        self.app.handle_event(pg.event.Event(pg.KEYDOWN, key=key, unicode=unicode, mod=0))
        self.app.render()

    def start(self, game):
        self.app.choose_game(game)
        self.app.render()
        self.click(730, 612)
        self.app.game_started = -10000
        self.app.render()

    def test_lobby_setup_and_gofish_request_by_mouse(self):
        self.click(640, 684)
        self.assertEqual(self.app.modal, 'setup')
        self.click(730, 612)
        self.app.game_started = -10000
        self.app.render()
        self.assertEqual(self.app.scene, 'table')
        # Eligible portrait and first card hit targets are exposed by rendering.
        portrait = next(rect for rect, _, enabled in self.app.buttons if enabled and rect.y == 175)
        card = next(rect for rect, _, enabled in self.app.buttons if enabled and rect.y == 572)
        self.click(*portrait.center)
        self.click(*card.center)
        self.assertIsNotNone(self.app.selected_rank)
        self.assertIsNotNone(self.app.selected_target)
        self.click(498, 706)
        self.assertEqual(len(self.app.game.gameLog), 1)
        if self.app.game.phase == 'fish':
            self.click(345, 706)
        self.assertEqual(self.app.game.current, 1)

    def test_rules_pause_opponents_and_escape_returns(self):
        self.start('gofish')
        self.app.game.current = 1
        self.click(910, 118)
        self.assertEqual(self.app.modal, 'rules')
        self.app.next_action = 0
        self.app.update()
        self.assertEqual(self.app.game.gameLog, [])
        self.key(pg.K_ESCAPE)
        self.app.update()
        self.assertTrue(self.app.game.gameLog)

    def test_blackjack_keyboard_settlement_and_replay(self):
        self.start('blackjack')
        if self.app.game.phase == 'player':
            self.key(pg.K_s, 's')
        for _ in range(20):
            self.app.next_action = 0
            self.app.update()
        self.assertTrue(self.app.game.finished)
        self.assertEqual(self.app.settings['rounds'], 1)
        self.app.render()
        self.click(385, 478)
        self.assertEqual(self.app.modal, 'setup')
        old = self.app.game
        self.click(730, 612)
        self.assertIsNot(old, self.app.game)

    def test_memory_clicks_flip_and_resolve_pair(self):
        self.start('memory')
        game = self.app.game
        match = next(i for i in range(1, 24) if game.cards[i] == game.cards[0])
        self.click(210, 250)
        self.click(210 + match % 6 * 112, 250 + match // 6 * 116)
        self.assertEqual(len(game.matched), 2)
        self.assertEqual(game.moves, 1)

    def test_leave_confirmation_and_stakes_are_not_refunded(self):
        self.start('blackjack')
        self.click(1160, 40)
        self.assertEqual(self.app.modal, 'leave')
        self.click(770, 612)
        self.assertEqual(self.app.scene, 'lobby')
        self.assertEqual(self.app.wallet.balance, 950)

    def test_resize_letterbox_click_mapping(self):
        self.app.window = pg.display.set_mode((960, 700), pg.RESIZABLE)
        self.app.render()
        # Native 1280x800 canvas scaled to 960x600, with a 50px top margin.
        self.click(480, 50 + int(684 * .75))
        self.assertEqual(self.app.modal, 'setup')
        self.assertEqual(self.app.game_id, 'gofish')

    def test_local_save_and_corrupt_save_recovery(self):
        self.app.set_option('name', 'Danny')
        self.app.wallet.balance = 789
        self.app.save()
        self.assertEqual(json.loads(self.path.read_text())['chips'], 789)
        self.assertEqual(self.app.load()['name'], 'Danny')
        self.path.write_text('{not-json', encoding='utf-8')
        self.assertEqual(self.app.load()['chips'], 1000)
        self.path.write_text('[]', encoding='utf-8')
        self.assertEqual(self.app.load()['name'], 'You')


if __name__ == '__main__':
    unittest.main()
