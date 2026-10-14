import contextlib
import io
import random
import unittest
from unittest.mock import patch

from cards import Card
from managers import GoFishManager
from players import CompGoFishPlayer, HumGoFishPlayer


def event(asker, target, rank, received=0, drew=False, drawnMatch=False, books=()):
    return {"type": "ask", "asker": asker, "target": target, "rank": rank,
            "received": received, "drew": drew, "drawnMatch": drawnMatch,
            "books": list(books)}


class GoFishTests(unittest.TestCase):
    def setUp(self):
        self.randomState = random.getstate()
        random.seed(23)
        self.output = contextlib.redirect_stdout(io.StringIO())
        self.output.__enter__()

    def tearDown(self):
        self.output.__exit__(None, None, None)
        random.setstate(self.randomState)

    def player(self, name, ranks=(), difficulty="hard"):
        player = CompGoFishPlayer(name, difficulty)
        for rank in ranks:
            player.drawCard(Card(rank))
        return player

    def manager(self, players, pool=()):
        manager = GoFishManager()
        manager.players = players
        manager.deck.drawPile = list(pool)
        return manager

    def test_books_need_four_and_leave_hand(self):
        player = self.player("A", ["Ace"] * 3)
        self.assertEqual(player.collectSets(), [])
        player.drawCard(Card("Ace", "Hearts"))
        self.assertEqual(player.collectSets(), ["Ace"])
        self.assertFalse(player.hasCards())
        self.assertEqual(len(player.sets["Ace"]), 4)
        self.assertEqual(player.collectSets(), [])

    @patch("players.random.random", return_value=1)
    def test_memory_tracks_transfer_and_book(self, _):
        player = self.player("A", ["Ace", "King"])
        log = [event("B", "C", "Ace"), event("C", "B", "Ace", received=1)]
        self.assertEqual(player.makeChoice(["B", "C"], log), ["Ace", "C"])
        log.append(event("C", "B", "Ace", received=1, books=["Ace"]))
        self.assertEqual(player.makeChoice(["B", "C"], log)[0], "King")

    @patch("players.random.random", return_value=1)
    def test_draw_invalidates_old_negative_evidence(self, _):
        player = self.player("A", ["Ace", "Ace", "King"])
        log = [event("C", "B", "Ace"),
               {"type": "draw", "asker": "B", "drew": True, "books": []}]
        self.assertEqual(player.makeChoice(["B"], log), ["Ace", "B"])

    @patch("players.random.random", return_value=1)
    def test_easy_forgets_evidence_hard_remembers(self, _):
        log = [event("B", "C", "Ace")]
        log.extend(event("C", "B", "Two") for _ in range(4))
        easy = self.player("A", ["Ace", "King", "King"], "easy")
        hard = self.player("A", ["Ace", "King", "King"], "hard")
        self.assertEqual(easy.makeChoice(["B"], log)[0], "King")
        self.assertEqual(hard.makeChoice(["B"], log)[0], "Ace")

    @patch("players.random.random", return_value=0)
    @patch("players.random.choice", side_effect=lambda choices: choices[-1])
    def test_hard_can_ignore_known_good_request(self, *_):
        player = self.player("A", ["Ace"])
        self.assertEqual(player.makeChoice(["B", "C"], [event("B", "C", "Ace")]),
                         ["Ace", "C"])

    def test_successful_request_transfers_all_cards_and_ends_turn(self):
        a = self.player("A", ["Ace", "King"])
        b = self.player("B", ["Ace", "Ace", "Two"])
        manager = self.manager([a, b])
        with patch.object(a, "makeChoice", return_value=["Ace", "B"]) as choose:
            manager.manageTurn(a)
        choose.assert_called_once()
        self.assertEqual(len(a.hand["Ace"]), 3)
        self.assertEqual(b.hand["Ace"], [])
        self.assertEqual([entry["received"] for entry in manager.gameLog], [2])

    def test_fishing_always_ends_turn_and_private_draw_stays_private(self):
        for drawnRank in ["Ace", "Two"]:
            with self.subTest(drawnRank=drawnRank):
                a, b = self.player("A", ["Ace"]), self.player("B", ["King"])
                manager = self.manager([a, b], [Card(drawnRank), Card("Three")])
                with patch.object(a, "makeChoice", return_value=["Ace", "B"]) as choose, \
                        patch.object(a, "goFish", return_value=0) as fish:
                    manager.manageTurn(a)
                choose.assert_called_once()
                fish.assert_called_once()
                self.assertEqual(len(manager.deck.drawPile), 1)
                self.assertEqual(len(a.hand[drawnRank]), 2 if drawnRank == "Ace" else 1)
                self.assertEqual([entry["drawnMatch"] for entry in manager.gameLog],
                                 [drawnRank == "Ace"])
                self.assertNotIn("Two", str(manager.gameLog))

    def test_refill_and_empty_pool_skip(self):
        a, b = self.player("A"), self.player("B", ["King"])
        manager = self.manager([a, b], [Card("Ace")])
        manager.manageTurn(a)
        self.assertEqual(manager.gameLog[0]["type"], "draw")
        a.giveSet("Ace")
        with patch.object(a, "makeChoice") as choose:
            manager.manageTurn(a)
        choose.assert_not_called()

    def test_single_remaining_player_finishes_books(self):
        a, b = self.player("A", ["Ace"] * 3), self.player("B")
        manager = self.manager([a, b], [Card("Ace")])
        manager.manageTurn(a)
        self.assertTrue(manager.isGameOver())
        self.assertEqual(manager.determineWinner(), [a])
        b.sets["King"] = [Card("King")] * 4
        self.assertEqual(manager.determineWinner(), [a, b])

    def test_fishing_indices_and_human_name_matching(self):
        player = self.player("A")
        for size in range(1, 53):
            for _ in range(10):
                self.assertIn(player.goFish(size), range(size))
        with self.assertRaises(ValueError):
            player.goFish(0)
        human = HumGoFishPlayer("Human")
        human.drawCard(Card("Ace"))
        with patch("builtins.input", side_effect=["two", " ace ", "bad", " mCDoNALD "]):
            self.assertEqual(human.makeChoice(["McDonald"]), ["Ace", "McDonald"])
        with patch("builtins.input", return_value="center"):
            self.assertEqual(human.goFish(1), 0)

    def test_reset_deal_validation_and_replay(self):
        manager = GoFishManager()
        with patch("builtins.input", side_effect=["bad", "0", "5", "1", "bad", "HARD"]):
            manager.resetGame("alex")
        self.assertEqual(len(manager.deck.drawPile), 38)
        self.assertNotEqual(manager.players[1].name.casefold(), "alex")
        manager.gameLog.append({"old": True})
        manager.players[0].sets["Ace"] = []
        manager.resetGame("Player", 4, "easy")
        self.assertEqual(len(manager.deck.drawPile), 27)
        self.assertEqual(manager.gameLog, [])
        self.assertEqual(sum(len(p.sets) for p in manager.players), 0)
        with patch("builtins.input", side_effect=["bad", "YES", "no"]):
            self.assertTrue(manager.promptNextGame())
            self.assertFalse(manager.promptNextGame())

    def test_manager_limits_memory_given_to_computer(self):
        a, b = self.player("A", ["Ace"], "easy"), self.player("B", ["King"])
        manager = self.manager([a, b])
        manager.gameLog = [event("B", "A", "King") for _ in range(20)]
        with patch.object(a, "makeChoice", return_value=["Ace", "B"]) as choose:
            manager.manageTurn(a)
        self.assertEqual(choose.call_args.args[0], ["B"])
        self.assertEqual(len(choose.call_args.args[1]), 4)

    def test_complete_games_conserve_all_cards(self):
        for seed in range(60):
            random.seed(seed)
            manager = GoFishManager()
            manager.resetGame("Human", 1 + seed % 4, ["easy", "medium", "hard"][seed % 3])
            human = manager.players[0]
            replacement = self.player(human.name, difficulty=manager.players[1].difficulty)
            replacement.hand, replacement.sets = human.hand, human.sets
            manager.players[0] = replacement
            for turn in range(3000):
                if manager.isGameOver():
                    break
                manager.manageTurn(manager.players[turn % len(manager.players)])
                cards = list(manager.deck.drawPile)
                for player in manager.players:
                    cards.extend(card for hand in player.hand.values() for card in hand)
                    cards.extend(card for book in player.sets.values() for card in book)
                self.assertEqual(len(cards), 52)
                self.assertEqual(len({(card.rank, card.suit) for card in cards}), 52)
            self.assertTrue(manager.isGameOver(), f"Seed {seed} did not finish")
            self.assertEqual(sum(len(p.sets) for p in manager.players), 13)

    def test_menu_dispatches_go_fish_and_replay(self):
        import main
        with patch("builtins.input", side_effect=["2", "q"]), \
                patch.object(main.GoFishManager, "playGame", side_effect=[True, False]) as play:
            main.main()
        self.assertEqual(play.call_count, 2)


if __name__ == "__main__":
    unittest.main()
