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

    # Number of remembered public events, and chance of ignoring that memory.
    DIFFICULTIES = {"easy": (4, 0.45), "medium": (12, 0.20), "hard": (30, 0.08)}

    def __init__(self, name, difficulty="medium"):
        difficulty = difficulty.strip().lower()
        if difficulty not in self.DIFFICULTIES:
            raise ValueError("Difficulty must be easy, medium, or hard.")
        self.difficulty = difficulty
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
        if deckSize <= 0:
            raise ValueError("Cannot fish from an empty deck.")
        return random.choice([0, (deckSize - 1) // 2, deckSize - 1])


    def giveSet(self, cardRank):
        toGive = self.hand[cardRank]
        self.hand[cardRank] = []
        return toGive


    def collectSets(self):
        """Move books of four out of the hand and return their ranks."""
        completed = []
        for rank, cards in self.hand.items():
            if len(cards) == 4:
                self.sets[rank] = self.giveSet(rank)
                completed.append(rank)
        return completed

    def hasCards(self):
        return any(self.hand.values())

    def makeChoice(self, otherPlayers, gameLog=None):
        """Return [rank, opponent name], using only this hand and public events.

        Asking reveals a rank in the asker's hand. Transfers and books supersede
        older evidence. A private draw may invalidate a previous absence, but
        its rank is never available to this player.
        """
        ranks = [rank for rank, cards in self.hand.items() if cards]
        opponents = [name for name in otherPlayers if name != self.name]
        choices = [(rank, name) for rank in ranks for name in opponents]
        if not choices:
            raise ValueError("A choice requires cards and an eligible opponent.")

        memoryLength, mistakeChance = self.DIFFICULTIES[self.difficulty]
        knowledge = {}
        for event in (gameLog or [])[-memoryLength:]:
            asker = event["asker"]
            if event["type"] == "ask":
                rank, target = event["rank"], event["target"]
                knowledge[asker, rank] = True
                knowledge[target, rank] = False
                if event["drawnMatch"]:
                    knowledge[asker, rank] = True
            if event["drew"]:
                # Unknown draws can undo negative evidence, not reveal a rank.
                knowledge = {key: value for key, value in knowledge.items()
                             if key[0] != asker or value}
            for rank in event["books"]:
                for name in [self.name] + opponents:
                    knowledge[name, rank] = False

        if random.random() < mistakeChance:
            return list(random.choice(choices))

        def score(choice):
            rank, name = choice
            evidence = knowledge.get((name, rank))
            return (2 if evidence is True else 0 if evidence is False else 1,
                    len(self.hand[rank]))

        bestScore = max(map(score, choices))
        return list(random.choice([choice for choice in choices
                                   if score(choice) == bestScore]))


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
        if deckSize <= 0:
            raise ValueError("Cannot fish from an empty deck.")
        validChoice = False
        while not validChoice:
            mid = (deckSize - 1) // 2
            last = deckSize - 1

            print("")
            print("Would you like to draw from the top, center, or bottom of deck?\n")
            playerChoice = input(" --> ").strip().lower()

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
                print("You can't fish here! Cast a line somewhere else!\n")

        return choiceIdx


    def makeChoice(self, otherPlayers):
        validCardChoice = False
        while not validCardChoice:
            self.showHand()
            print("Choose a card to ask for:\n")
            cardChoice = input(" --> ").strip().capitalize()

            validCards = []
            for rank in self.hand.keys():
                if len(self.hand[rank]) > 0:
                    validCards.append(rank)

            if cardChoice in validCards:
                validCardChoice = True
            else:
                print("You don't have any of that card! Pick again!\n")


        validPlayerChoice = False
        while not validPlayerChoice:
            print(otherPlayers, end="\n\n")
            print("Choose a player to ask:\n")
            enteredName = input(" --> ").strip().casefold()
            playerChoice = next((name for name in otherPlayers
                                 if name.casefold() == enteredName), None)

            if playerChoice in otherPlayers:
                validPlayerChoice = True
            else:
                print("Choose one of the listed players! Pick again!\n")

        return [cardChoice, playerChoice]


    def showHand(self):
        print("")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("")
        print(f"             {self.name.upper()}'S HAND")
        print("")
        for rank in self.hand.keys():
            if len(self.hand[rank]) > 0:
                print(f"            {rank}: {len(self.hand[rank])}\n")
        print("")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("")
