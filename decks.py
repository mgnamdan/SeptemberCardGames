from cards import Card
from random import shuffle

class Deck:

    RANKS = ["Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Jack", "Queen", "King", "Ace"]
    SUITS = ["Clubs", "Hearts", "Spades", "Diamonds"]


    def __init__(self):
        self.reset()


    def __str__(self):
        return "\n".join(str(card) for card in self.drawPile)


    def reset(self):
        self.drawPile = []
        self.discardPile = []
        self.outPile = []

        for suit in self.SUITS:
            for rank in self.RANKS:
                newCard = Card(rank, suit)
                self.drawPile.append(newCard)


    def draw(self):
        toGive = self.drawPile.pop(0)
        self.outPile.append(toGive)
        return toGive


    def discard(self, toDiscard):
        if toDiscard in self.outPile:
            self.outPile.remove(toDiscard)
            self.discardPile.append(toDiscard)


    def shuffle(self):
        shuffle(self.drawPile)