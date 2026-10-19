"""Shared, immutable playing cards, independent of the GUI."""
from dataclasses import dataclass

RANKS = ("Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
         "Ten", "Jack", "Queen", "King", "Ace")
SUITS = ("Clubs", "Hearts", "Spades", "Diamonds")
LABELS = dict(zip(RANKS, ("2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A")))


@dataclass(frozen=True)
class Card:
    rank: str = "Two"
    suit: str = "Clubs"

    def __post_init__(self):
        if self.rank not in RANKS or self.suit not in SUITS:
            raise ValueError("Unknown card rank or suit")

    @property
    def label(self):
        return LABELS[self.rank]

    @property
    def value(self):
        return min(RANKS.index(self.rank) + 2, 10) if self.rank != "Ace" else 11

    def __str__(self):
        return f"{self.rank} of {self.suit}"


def hand_value(cards):
    total = sum(card.value for card in cards)
    aces = sum(card.rank == "Ace" for card in cards)
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total
