class CompBlackjackPlayer:

    CARDVALUES = {"Two": 2, "Three": 3, "Four": 4, "Five": 5, "Six": 6, "Seven": 7, "Eight": 8,
                  "Nine": 9, "Ten": 10, "Jack": 10, "Queen": 10, "King": 10, "Ace": 11}


    def __init__(self, name):
        self.name = name
        self.hand = []
        self.score = 0


    def __repr__(self):
        return self.name


    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        if self.name != other.name:
            return False
        if len(self.hand) != len(other.hand):
            return False
        else:
            for idx in range(len(self.hand)):
                if self.hand[idx] != other.hand[idx]:
                    return False
            return True


    def drawCard(self):
        pass


    def discardCard(self):
        pass


    def showHand(self):
        print("")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("")
        print(f"             {self.name.upper()}'S HAND")
        print("")
        if len(self.hand) == 0:
            print("           No cards in hand!")
        else:
            print("             1. ??? of ???")
            for idx in range(1, len(self.hand)):
                print(f"             {idx + 1} {str(self.hand[idx])}")
        print("")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("")


    def calcScore(self):
        pass


    def giveScore(self):
        return self.score


    def makeChoice(self):
        pass
