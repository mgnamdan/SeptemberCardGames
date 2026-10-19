"""Event-driven game managers. Each action returns immediately to the GUI."""
import random
from cards import Card, RANKS, hand_value
from decks import Deck
from currency import Wallet
from players import BlackjackHand, CompGoFishPlayer, HumGoFishPlayer


class TableManager:
    def __init__(self):
        self.messages = []
        self.result = ""
        self.phase = ""
        self.revision = 0

    def say(self, message):
        self.messages.append(message)
        self.messages = self.messages[-100:]
        self.revision += 1

    @property
    def finished(self):
        return self.phase == "finished"


class GoFishManager(TableManager):
    COMPNAMES = ["Mabel", "Jasper", "Cleo", "Otis", "Ruby", "Felix"]

    def __init__(self, name="You", num_comps=2, difficulty="medium"):
        super().__init__()
        if num_comps not in range(1, 5):
            raise ValueError("Choose 1 to 4 opponents")
        self.deck = Deck()
        names = [n for n in self.COMPNAMES if n.casefold() != name.casefold()]
        self.players = [HumGoFishPlayer(name, difficulty)] + [
            CompGoFishPlayer(n, difficulty) for n in random.sample(names, num_comps)]
        self.gameLog = []
        self.current = 0
        self.pending = None
        for _ in range(7 if num_comps == 1 else 5):
            for player in self.players:
                player.drawCard(self.deck.draw())
        self.say("Cards dealt. One request per turn. Make it count.")
        for player in self.players:
            self._books(player)
        self._prepare()

    @property
    def player(self):
        return self.players[self.current]

    @property
    def opponents(self):
        return [p for p in self.players if p is not self.player and p.hasCards()]

    def _books(self, player):
        books = player.collectSets()
        for rank in books:
            self.say(f"{player.name} completed a book of {rank}s!")
        return books

    def _prepare(self):
        if not len(self.deck) and not any(p.hasCards() for p in self.players):
            self.phase = "finished"
            winners = self.determineWinner()
            self.result = " & ".join(p.name for p in winners) + (" wins!" if len(winners) == 1 else " tie!")
            self.say(self.result)
        elif not self.player.hasCards():
            self.phase = "refill" if len(self.deck) else "skip"
        elif not self.opponents:
            self.phase = "collect"
        else:
            self.phase = "ask"

    def _end_turn(self):
        self.current = (self.current + 1) % len(self.players)
        self._prepare()

    def ask(self, rank, target_name):
        if self.phase != "ask":
            raise ValueError("Not ready to ask")
        targets = {p.name: p for p in self.opponents}
        if rank not in self.player.hand or not self.player.hand[rank] or target_name not in targets:
            raise ValueError("Choose a rank in your hand and an opponent with cards")
        player = self.player
        self.say(f"{player.name} asks {target_name} for {rank}s.")
        cards = targets[target_name].giveSet(rank)
        for card in cards:
            player.drawCard(card)
        entry = {"type": "ask", "asker": player.name, "target": target_name,
                 "rank": rank, "received": len(cards), "drew": False,
                 "drawnMatch": False, "books": self._books(player)}
        self.gameLog.append(entry)
        if cards:
            self.say(f"{target_name} hands over {len(cards)}. Turn complete.")
            self._end_turn()
        elif len(self.deck):
            self.say(f"Go fish, {player.name}!")
            self.pending = entry
            self.phase = "fish"
        else:
            self.say("No cards to give. The pool is empty.")
            self._end_turn()

    def fish(self, index=0):
        if self.phase not in ("fish", "refill", "collect") or not len(self.deck):
            raise ValueError("Cannot draw now")
        if not 0 <= index < len(self.deck):
            raise ValueError("Invalid draw position")
        player, phase = self.player, self.phase
        card = self.deck.draw(index)
        player.drawCard(card)
        books = self._books(player)
        if phase == "fish":
            self.pending.update(drew=True, drawnMatch=card.rank == self.pending["rank"], books=books)
            public_match = self.pending["drawnMatch"]
            self.pending = None
            if self.current == 0:
                self.say(f"You drew {card}. Turn complete.")
            else:
                self.say(f"{player.name} drew {'the requested rank' if public_match else 'a card'}. Turn complete.")
            self._end_turn()
        else:
            self.gameLog.append({"type": "draw", "asker": player.name, "drew": True, "books": books})
            self.say(f"{player.name} draws {'a card' if self.current else str(card)}.")
            self._prepare()

    def step(self):
        """One computer action or forced skip. Never waits or reads input."""
        if self.finished:
            return
        if self.phase == "skip":
            self.say(f"{self.player.name} has no cards and skips.")
            self._end_turn()
        elif self.phase == "collect" or (self.current != 0 and self.phase in ("refill", "fish")):
            self.fish(self.player.goFish(len(self.deck)))
        elif self.current != 0 and self.phase == "ask":
            memory = self.player.DIFFICULTIES[self.player.difficulty][0]
            rank, name = self.player.makeChoice([p.name for p in self.opponents], self.gameLog[-memory:])
            self.ask(rank, name)

    def determineWinner(self):
        high = max(len(p.sets) for p in self.players)
        return [p for p in self.players if len(p.sets) == high]


class BlackjackManager(TableManager):
    def __init__(self, wallet=None, bet=50):
        super().__init__()
        self.wallet = wallet if wallet is not None else Wallet()
        if bet not in (10, 25, 50, 100):
            raise ValueError("Choose a supported bet")
        self.wallet.spend(bet)
        self.deck = Deck()
        self.hands = [BlackjackHand([self.deck.draw(), self.deck.draw()], bet)]
        self.dealer = [self.deck.draw(), self.deck.draw()]
        self.active = 0
        self.phase = "player"
        self.say(f"{bet} chips on the felt. Good luck.")
        if self.hands[0].natural or hand_value(self.dealer) == 21:
            self.phase = "dealer"
            self.say("Checking for blackjack.")

    @property
    def hand(self):
        return self.hands[self.active]

    @property
    def can_split(self):
        return (self.phase == "player" and len(self.hands) < 4 and len(self.hand.cards) == 2
                and self.hand.cards[0].rank == self.hand.cards[1].rank
                and self.wallet.balance >= self.hand.bet)

    @property
    def can_double(self):
        return self.phase == "player" and len(self.hand.cards) == 2 and self.wallet.balance >= self.hand.bet

    def _next_hand(self):
        self.hand.done = True
        if self.active + 1 < len(self.hands):
            self.active += 1
        else:
            self.phase = "dealer"

    def action(self, choice):
        if self.phase != "player":
            raise ValueError("It is not your turn")
        if choice == "hit":
            card = self.deck.draw()
            self.hand.cards.append(card)
            self.say(f"You draw {card}. Total: {self.hand.score}.")
            if self.hand.score >= 21:
                self._next_hand()
        elif choice == "stand":
            self.say(f"You stand on {self.hand.score}.")
            self._next_hand()
        elif choice == "double" and self.can_double:
            self.wallet.spend(self.hand.bet)
            self.hand.bet *= 2
            self.hand.cards.append(self.deck.draw())
            self.say(f"Double down. Your total is {self.hand.score}.")
            self._next_hand()
        elif choice == "split" and self.can_split:
            self.wallet.spend(self.hand.bet)
            card = self.hand.cards.pop()
            self.hand.split = True
            new_hand = BlackjackHand([card, self.deck.draw()], self.hand.bet, split=True)
            self.hand.cards.append(self.deck.draw())
            self.hands.insert(self.active + 1, new_hand)
            self.say("Pair split. Play each hand in order.")
            if card.rank == "Ace":
                self._next_hand()
                self._next_hand()
        else:
            raise ValueError("That action is not available")

    def step(self):
        if self.phase != "dealer":
            return
        score = hand_value(self.dealer)
        if score < 17 and any(h.score <= 21 and not h.natural for h in self.hands):
            card = self.deck.draw()
            self.dealer.append(card)
            self.say(f"Dealer draws {card}. Total: {hand_value(self.dealer)}.")
            return
        dealer_natural = len(self.dealer) == 2 and score == 21
        net = 0
        for hand in self.hands:
            payout = 0
            if hand.score > 21:
                hand.result = "BUST"
            elif hand.natural and not dealer_natural:
                # Integer chips: the half chip on an odd stake rounds down.
                hand.result, payout = "BLACKJACK", hand.bet + hand.bet * 3 // 2
            elif dealer_natural and not hand.natural:
                hand.result = "DEALER WINS"
            elif score > 21 or hand.score > score:
                hand.result, payout = "YOU WIN", hand.bet * 2
            elif hand.score == score:
                hand.result, payout = "PUSH", hand.bet
            else:
                hand.result = "DEALER WINS"
            self.wallet.credit(payout)
            net += payout - hand.bet
        self.phase = "finished"
        self.result = f"{'+' if net >= 0 else ''}{net} chips" if len(self.hands) > 1 else self.hands[0].result.title()
        self.say(f"Round complete. {'+' if net >= 0 else ''}{net} chips.")


class MemoryManager(TableManager):
    """Solo 12-pair matching. Mismatches stay visible until the next step."""
    def __init__(self):
        super().__init__()
        pairs = [Card(rank, "Hearts" if i % 2 else "Spades") for i, rank in enumerate(RANKS[:12])]
        self.cards = pairs * 2
        random.shuffle(self.cards)
        self.matched = set()
        self.flipped = []
        self.moves = 0
        self.phase = "choose"
        self.say("Find all 12 pairs. Take your time; every move counts.")

    def flip(self, index):
        if self.phase != "choose" or index in self.matched or index in self.flipped or not 0 <= index < 24:
            raise ValueError("Choose a face-down card")
        self.flipped.append(index)
        self.revision += 1
        if len(self.flipped) == 2:
            self.moves += 1
            a, b = self.flipped
            if self.cards[a] == self.cards[b]:
                self.matched.update(self.flipped)
                self.flipped = []
                self.say(f"A pair of {self.cards[a].rank}s. Nicely spotted.")
                if len(self.matched) == len(self.cards):
                    self.phase = "finished"
                    self.result = f"All pairs in {self.moves} moves!"
                    self.say(self.result)
            else:
                self.phase = "reveal"
                self.say("Not a pair. Remember those places.")

    def step(self):
        if self.phase == "reveal":
            self.flipped = []
            self.phase = "choose"
