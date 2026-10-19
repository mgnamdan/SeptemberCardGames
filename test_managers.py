import random
import unittest
from cards import Card, hand_value
from currency import Wallet
from decks import Deck
from managers import BlackjackManager, MemoryManager
from players import BlackjackHand


def cards(*ranks):
    return [Card(rank) for rank in ranks]


class BlackjackTests(unittest.TestCase):
    def table(self, player, dealer, pool=(), bet=50):
        game = BlackjackManager(Wallet(), bet)
        game.hands = [BlackjackHand(cards(*player), bet)]
        game.dealer = cards(*dealer)
        game.deck.drawPile = cards(*pool)
        game.phase = 'player'
        return game

    def test_aces_and_card_identity(self):
        self.assertEqual(hand_value(cards('Ace', 'Ace', 'Nine')), 21)
        self.assertEqual(hand_value(cards('Ace', 'Ace', 'King', 'King')), 22)
        self.assertNotEqual(Card('Ace', 'Spades'), Card('Ace', 'Hearts'))
        deck = Deck()
        self.assertEqual(len(set(deck.drawPile)), 52)

    def test_natural_push_win_and_loss_payouts(self):
        for player, dealer, expected in [
            (('Ace', 'King'), ('Ten', 'Nine'), 1075),
            (('Ace', 'King'), ('Ace', 'Queen'), 1000),
            (('Ten', 'Nine'), ('Ten', 'Eight'), 1050),
            (('Ten', 'Nine'), ('Ten', 'Nine'), 1000),
            (('Ten', 'Nine'), ('Ace', 'King'), 950),
        ]:
            with self.subTest(player=player, dealer=dealer):
                game = self.table(player, dealer)
                game.action('stand')
                game.step()
                self.assertTrue(game.finished)
                self.assertEqual(game.wallet.balance, expected)
                game.step()
                self.assertEqual(game.wallet.balance, expected)

    def test_bust_loses_even_when_dealer_busts(self):
        game = self.table(('King', 'Queen', 'Five'), ('King', 'Queen', 'Six'))
        game.action('stand')
        game.step()
        self.assertEqual(game.hand.result, 'BUST')
        self.assertEqual(game.wallet.balance, 950)

    def test_double_draws_once_and_adds_stake(self):
        game = self.table(('Five', 'Six'), ('Ten', 'Eight'), ('King',))
        game.action('double')
        self.assertEqual(game.phase, 'dealer')
        self.assertEqual(game.hand.bet, 100)
        self.assertEqual(game.wallet.balance, 900)
        game.step()
        self.assertEqual(game.wallet.balance, 1100)

    def test_split_hands_and_split_aces(self):
        game = self.table(('Eight', 'Eight'), ('Ten', 'Seven'), ('Three', 'King'))
        game.action('split')
        self.assertEqual(len(game.hands), 2)
        self.assertEqual(game.wallet.balance, 900)
        game.action('stand')
        self.assertEqual(game.active, 1)
        game.action('stand')
        game.step()
        self.assertEqual([h.result for h in game.hands], ['YOU WIN', 'DEALER WINS'])
        game = self.table(('Ace', 'Ace'), ('Ten', 'Seven'), ('King', 'Ten'))
        game.action('split')
        self.assertEqual(game.phase, 'dealer')
        self.assertFalse(any(h.natural for h in game.hands))
        game.step()
        self.assertEqual(game.wallet.balance, 1100)

    def test_dealer_stands_soft_17_and_hits_16(self):
        game = self.table(('Ten', 'Eight'), ('Ace', 'Six'), ('King',))
        game.action('stand')
        game.step()
        self.assertEqual(len(game.dealer), 2)
        game = self.table(('Ten', 'Eight'), ('Ten', 'Six'), ('King',))
        game.action('stand')
        game.step()
        self.assertEqual(len(game.dealer), 3)
        game.step()
        self.assertEqual(game.hand.result, 'YOU WIN')

    def test_disabled_actions_do_not_spend(self):
        game = self.table(('Ten', 'Nine'), ('Ten', 'Seven'))
        with self.assertRaises(ValueError):
            game.action('split')
        game.wallet.balance = 0
        with self.assertRaises(ValueError):
            game.action('double')
        self.assertEqual(game.wallet.balance, 0)
        with self.assertRaises(ValueError):
            BlackjackManager(Wallet(0))

    def test_300_rounds_finish_and_deal_unique_cards(self):
        state = random.getstate()
        try:
            for seed in range(300):
                random.seed(seed)
                game = BlackjackManager()
                for _ in range(100):
                    if game.finished:
                        break
                    if game.phase == 'dealer':
                        game.step()
                    elif game.can_split:
                        game.action('split')
                    elif game.hand.score < 17:
                        game.action('hit')
                    else:
                        game.action('stand')
                self.assertTrue(game.finished)
                dealt = game.dealer + [c for h in game.hands for c in h.cards]
                self.assertEqual(len(dealt), len(set(dealt)))
                self.assertGreaterEqual(game.wallet.balance, 0)
        finally:
            random.setstate(state)


class MemoryTests(unittest.TestCase):
    def test_mismatch_holds_until_step_and_cannot_click_third(self):
        game = MemoryManager()
        second = next(i for i, c in enumerate(game.cards) if c != game.cards[0])
        game.flip(0)
        with self.assertRaises(ValueError):
            game.flip(0)
        game.flip(second)
        self.assertEqual(game.phase, 'reveal')
        with self.assertRaises(ValueError):
            game.flip(23)
        game.step()
        self.assertEqual(game.flipped, [])
        self.assertEqual(game.moves, 1)

    def test_complete_perfect_board(self):
        game = MemoryManager()
        for card in set(game.cards):
            for index, candidate in enumerate(game.cards):
                if candidate == card:
                    game.flip(index)
        self.assertTrue(game.finished)
        self.assertEqual(game.moves, 12)
        self.assertEqual(len(game.matched), 24)


if __name__ == '__main__':
    unittest.main()
