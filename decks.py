"""A shuffled deck shared by the table managers."""
import random
from cards import Card, RANKS, SUITS


class Deck:
    RANKS = RANKS
    SUITS = SUITS

    def __init__(self):
        self.reset()

    def reset(self):
        self.drawPile = [Card(rank, suit) for suit in SUITS for rank in RANKS]
        self.discardPile = []
        self.outPile = []
        self.shuffle()

    def draw(self, drawIdx=0):
        if not self.drawPile:
            raise ValueError("The deck is empty")
        card = self.drawPile.pop(drawIdx)
        self.outPile.append(card)
        return card

    def shuffle(self):
        random.shuffle(self.drawPile)

    def discard(self, card):
        self.outPile.remove(card)
        self.discardPile.append(card)

    def __len__(self):
        return len(self.drawPile)
