class CompBlackjackPlayer:

    def __init__(self, name):
        self.name = name
        self.hand = []
        self.score = 0


    def __repr__(self):
        pass


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
        print(f"             {self.name}'S HAND")
        print("")
        print("             1. ??? of ???")
        for idx in range(1, len(self.hand)):
            print(f"             {idx + 1} {self.hand[idx].rank} of {self.hand[idx].suit}")
        print("")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")


    def calcScore(self):
        pass


    def giveScore(self):
        return self.score


    def makeChoice(self):
        pass
