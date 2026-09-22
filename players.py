class CompBlackjackPlayer:

    CARDVALUES = {"Two": 2, "Three": 3, "Four": 4, "Five": 5, "Six": 6, "Seven": 7, "Eight": 8,
                  "Nine": 9, "Ten": 10, "Jack": 10, "Queen": 10, "King": 10, "Ace": 11}


    def __init__(self, name):
        self.name = name
        self.hand = {1: []}
        self.scores = {1: 0}


    def __repr__(self):
        return self.name


    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        if self.name != other.name:
            return False
        if len(self.hand.keys()) != len(other.hand.keys()):
            return False
        else:
            for key in self.hand.keys():
                if len(self.hand[key]) != len(other.hand.key[key]):
                    return False
                else:
                    for idx in range(len(self.hand[key])):
                        if self.hand[key][idx] != self.hand[key][idx]:
                            return False
            return True



    def drawCard(self, toGet, handNum=1):
        self.hand[handNum].append(toGet)


    def discardCard(self, idx=0, handNum=1):
        return self.hand[handNum].pop(idx)


    def showHand(self, handNum=1):
        print("")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("")
        print(f"             {self.name.upper()}'S HAND")
        print("")
        if len(self.hand[handNum]) == 0:
            print("           No cards in hand!")
        else:
            print("             1. ??? of ???")
            for idx in range(1, len(self.hand[handNum])):
                print(f"             {idx + 1}. {str(self.hand[handNum][idx])}")
        print("")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("")


    def calcScore(self, handNum=1):
        rawScore = 0
        aces = 0
        for card in self.hand[handNum]:
            rawScore += self.CARDVALUES[card.rank]
            if card.rank == "Ace":
                aces += 1

        while rawScore > 21 and aces > 0:
            rawScore -= 10
            aces -= 1

        self.scores[handNum] = rawScore


    def giveScore(self, handNum=1):
        return self.scores[handNum]


    def makeChoice(self, handNum=1):
        self.calcScore(handNum)
        if self.scores[handNum] >= 17:
            return "stay"
        else:
            return "hit"



class HumBlackjackPlayer(CompBlackjackPlayer):

    def showHand(self, handNum=1):
        print("")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("")
        print(f"             {self.name.upper()}'S HAND")
        print("")
        if len(self.hand[handNum]) == 0:
            print("           No cards in hand!")
        else:
            for idx in range(len(self.hand[handNum])):
                print(f"             {idx + 1}. {str(self.hand[handNum][idx])}")
        print("")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("")


    def makeChoice(self):
        return input(" --> ")
