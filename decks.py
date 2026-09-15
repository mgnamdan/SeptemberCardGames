from cards import Card

class Deck:

    RANKS = ["Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Jack", "Queen", "King", "Ace"]
    SUITS = ["Clubs", "Hearts", "Spades", "Diamonds"]

    def __init__(self):
        pass

    def __str__(self):
        return "\n".join(card for card in self.drawPile)

    def reset(self):
        pass

    def draw(self):
        pass

    def discard(self):
        pass

    def shuffle(self):
        pass