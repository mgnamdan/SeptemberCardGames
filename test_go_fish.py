"""Rules and memory regressions for the event-driven Go Fish table."""
import random
import unittest
from unittest.mock import patch
from cards import Card
from managers import GoFishManager
from players import CompGoFishPlayer


def event(asker, target, rank, books=()):
    return dict(type='ask', asker=asker, target=target, rank=rank,
                received=0, drew=False, drawnMatch=False, books=list(books))


class GoFishTests(unittest.TestCase):
    def setUp(self):
        self.state = random.getstate()
        random.seed(23)

    def tearDown(self):
        random.setstate(self.state)

    def player(self, name, ranks=(), difficulty='hard'):
        player = CompGoFishPlayer(name, difficulty)
        for rank in ranks:
            player.drawCard(Card(rank))
        return player

    def table(self, a, b, pool=()):
        manager = GoFishManager(num_comps=1)
        manager.players = [a, b]
        manager.deck.drawPile = list(pool)
        manager.gameLog = []
        manager.current = 0
        manager._prepare()
        return manager

    def test_transfer_ends_turn_and_collects_book(self):
        a, b = self.player('A', ['Ace']), self.player('B', ['Ace'] * 3 + ['King'])
        game = self.table(a, b)
        game.ask('Ace', 'B')
        self.assertEqual(game.current, 1)
        self.assertEqual(game.gameLog[-1]['received'], 3)
        self.assertEqual(len(a.sets['Ace']), 4)
        self.assertFalse(a.hasCards())

    def test_matching_and_nonmatching_fish_both_end_turn(self):
        for rank in ('Ace', 'Two'):
            with self.subTest(rank=rank):
                game = self.table(self.player('A', ['Ace']), self.player('B', ['King']), [Card(rank), Card('Three')])
                game.ask('Ace', 'B')
                self.assertEqual(game.phase, 'fish')
                self.assertEqual(game.current, 0)
                game.fish(0)
                self.assertEqual(game.current, 1)
                self.assertEqual(len(game.deck), 1)
                self.assertEqual(game.gameLog[-1]['drawnMatch'], rank == 'Ace')
                self.assertNotIn('Two', str(game.gameLog))

    def test_refill_then_ask_and_empty_deck_skip(self):
        game = self.table(self.player('A'), self.player('B', ['King']), [Card('Ace')])
        self.assertEqual(game.phase, 'refill')
        game.fish()
        self.assertEqual((game.current, game.phase), (0, 'ask'))
        game.player.giveSet('Ace')
        game._prepare()
        self.assertEqual(game.phase, 'skip')
        game.step()
        self.assertEqual(game.current, 1)

    def test_illegal_actions_are_rejected_without_mutation(self):
        game = self.table(self.player('A', ['Ace']), self.player('B', ['King']))
        for rank, target in [('King', 'B'), ('Ace', 'A'), ('Ace', 'Nobody')]:
            with self.assertRaises(ValueError):
                game.ask(rank, target)
        with self.assertRaises(ValueError):
            game.fish()
        self.assertEqual(game.gameLog, [])
        self.assertEqual(game.current, 0)

    @patch('players.random.random', return_value=1)
    def test_memory_tracks_transfers_books_and_private_draws(self, _):
        player = self.player('A', ['Ace', 'King'])
        log = [event('B', 'C', 'Ace'), event('C', 'B', 'Ace')]
        self.assertEqual(player.makeChoice(['B', 'C'], log), ['Ace', 'C'])
        log.append(event('C', 'B', 'Ace', books=['Ace']))
        self.assertEqual(player.makeChoice(['B', 'C'], log)[0], 'King')
        player.drawCard(Card('Ace'))
        log = [event('C', 'B', 'Ace'), dict(type='draw', asker='B', drew=True, books=[])]
        self.assertEqual(player.makeChoice(['B'], log), ['Ace', 'B'])

    @patch('players.random.random', return_value=1)
    def test_easy_forgets_hard_remembers(self, _):
        log = [event('B', 'C', 'Ace')] + [event('C', 'B', 'Two')] * 4
        for difficulty, expected in [('easy', 'King'), ('hard', 'Ace')]:
            player = self.player('A', ['Ace', 'King', 'King'], difficulty)
            self.assertEqual(player.makeChoice(['B'], log)[0], expected)

    @patch('players.random.random', return_value=0)
    @patch('players.random.choice', side_effect=lambda options: options[-1])
    def test_even_hard_can_choose_wrong_opponent(self, *_):
        player = self.player('A', ['Ace'])
        self.assertEqual(player.makeChoice(['B', 'C'], [event('B', 'C', 'Ace')]), ['Ace', 'C'])

    def test_manager_only_shares_limited_log_and_names(self):
        game = self.table(self.player('A', ['King']), self.player('B', ['Ace'], 'easy'))
        game.current = 1
        game.gameLog = [event('A', 'B', 'King')] * 20
        with patch.object(game.player, 'makeChoice', return_value=['Ace', 'A']) as choose:
            game.step()
        self.assertEqual(choose.call_args.args[0], ['A'])
        self.assertEqual(len(choose.call_args.args[1]), 4)

    def test_computer_draw_rank_stays_private(self):
        game = self.table(self.player('A', ['King']), self.player('B', ['Ace']), [Card('Two')])
        game.current = 1
        game.ask('Ace', 'A')
        game.fish()
        self.assertNotIn('Two', str(game.gameLog))
        self.assertNotIn('Two', str(game.messages))

    def test_fishing_indices(self):
        player = self.player('A')
        for size in range(1, 53):
            self.assertIn(player.goFish(size), range(size))
        with self.assertRaises(ValueError):
            player.goFish(0)

    def test_complete_games_conserve_52_cards(self):
        for seed in range(120):
            random.seed(seed)
            game = GoFishManager(num_comps=1 + seed % 4, difficulty=['easy', 'medium', 'hard'][seed % 3])
            for _ in range(4000):
                if game.finished:
                    break
                if game.current == 0 and game.phase == 'ask':
                    rank, name = game.player.makeChoice([p.name for p in game.opponents], game.gameLog)
                    game.ask(rank, name)
                elif game.current == 0 and game.phase in ('fish', 'refill'):
                    game.fish()
                else:
                    game.step()
                cards = list(game.deck.drawPile)
                for player in game.players:
                    cards += [card for group in player.hand.values() for card in group]
                    cards += [card for group in player.sets.values() for card in group]
                self.assertEqual(len(cards), 52)
                self.assertEqual(len(set(cards)), 52)
            self.assertTrue(game.finished, f'Seed {seed} did not finish')
            self.assertEqual(sum(len(p.sets) for p in game.players), 13)


if __name__ == '__main__':
    unittest.main()
