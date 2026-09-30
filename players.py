import random

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#
#                       BLACKJACK PLAYER CLASSES
#
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


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
        if self.hand[handNum][0] == self.hand[handNum][1]:
            return "split"
        self.calcScore(handNum)
        if self.scores[handNum] >= 17 or len(self.hand[handNum]) == 5:
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


    def makeChoice(self, handNum=1):
        self.calcScore(handNum)
        if self.scores[handNum] >= 21 or len(self.hand[handNum]) == 5:
            return "stay"
        else:
            return input(" --> ").lower()



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#
#                       GO FISH PLAYER CLASSES
#
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class CompGoFishPlayer:

    def __init__(self, name):
        self.name = name
        self.hand = {"Two": [],
                     "Three": [],
                     "Four": [],
                     "Five": [],
                     "Six": [],
                     "Seven": [],
                     "Eight": [],
                     "Nine": [],
                     "Ten": [],
                     "Jack": [],
                     "Queen": [],
                     "King": [],
                     "Ace": []}
        self.sets = {}


    def __repr__(self):
        return self.name


    def drawCard(self, goCard):
        cardRank = goCard.rank
        self.hand[cardRank].append(goCard)


    def goFish(self, deckSize):
        choice = random.randint(1, 3)
        if choice == 1:
            return 0
        elif choice == 2:
            return (deckSize // 2) - 1
        else:
            return deckSize - 1


    def giveSet(self, cardRank):
        toGive = self.hand[cardRank]
        self.hand[cardRank] = []
        return toGive


    def makeChoice(self):
        pass


    def showMatches(self):
        print("")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("")
        print(f"           {self.name.upper()}'S MATCHES")
        print("")
        if len(self.sets.keys()) == 0:
            print("           No matching sets!")
        else:
            for rank in self.sets.keys():
                print(f"             {rank}s: {self.sets[rank]}")
        print("")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("")







class HumGoFishPlayer(CompGoFishPlayer):

    def goFish(self, deckSize):
        validChoice = False
        while not validChoice:
            mid = (deckSize // 2) - 1
            last = deckSize - 1

            print("")
            print(f"Would you like to draw from the top, center, or bottom of deck?")
            playerChoice = input(" --> ").lower()

            if playerChoice in ["top", "1", "beginning", "default"]:
                choiceIdx = 0
                validChoice = True
            elif playerChoice in ["center", "mid", "middle"]:
                choiceIdx = mid
                validChoice = True
            elif playerChoice in ["bottom", "last", "deep sea"]:
                choiceIdx = last
                validChoice = True
            else:
                print("You can't fish here! Cast a line somewhere else!")

        return choiceIdx


    def makeChoice(self, otherPlayers):
        validChoice = False
        while not validChoice:
            self.showHand()
            print("")
            print("")

    def showHand(self):
        pass
