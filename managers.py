import random
from players import CompBlackjackPlayer, HumBlackjackPlayer
from decks import Deck


class BlackjackManager:

    COMPNAMES = ["Alex", "Ben", "Claire", "Danny", "Emily", "Felix", "Grace", "Henry", "Isabella", "Jack", "Kayla", "Liam", "Morgan",
                 "Nathan", "Olivia", "Pat", "Quinn", "Ryan", "Sophie", "Taylor", "Uma", "Victor", "Willow", "Xavier", "Yasmine", "Zach"]


    def __init__(self):
        self.usedNames = []
        dealerName = random.choice(self.COMPNAMES)
        self.usedNames.append(dealerName)
        self.dealer = CompBlackjackPlayer(dealerName)
        self.deck = Deck()


    def resetGame(self, playerName):
        self.players = []
        # Create the human player and add to players list
        human = HumBlackjackPlayer(playerName)
        self.players.append(human)

        # Prompt the number of computer players
        validNumPlayers = False
        while not validNumPlayers:
            print("")
            print("How many computers would you like to play against? (1-4)")
            numComps = input(" --> ")

            try:
                numComps = int(numComps) - 1
                if numComps >= 0 and numComps < 5:
                    validNumPlayers = True
                else:
                    print("Invalid number - please try again!")
            except ValueError:
                print("Invalid number - please try again!")

        # Create other computers and add them to players list
        if numComps == 0:
            self.players.append(self.dealer)
        else:
            for _ in range(numComps):
                validName = False
                while not validName:
                    compName = random.choice(self.COMPNAMES)
                    if compName not in self.usedNames:
                        validName = True
                computer = CompBlackjackPlayer(compName)
                self.players.append(computer)
                self.usedNames.append(compName)
            self.players.append(self.dealer)


    def determineWinner(self):
        pass


    def promptNextGame(self):
        pass


    def manageTurn(self, player):
        takingTurn = True
        handNum = 1
        while takingTurn:

            player.showHand(handNum)
            choice = player.makeChoice(handNum)
            if choice == "split":
                # Implement the split
                pass
            elif choice == "hit":
                player.drawCard(self.deck.draw(), handNum)
            else:
                takingTurn = False


    def playGame(self):
        # Prompt player name and set up game
        print("")
        print("What is your name?")
        playerName = input(" --> ")
        self.resetGame(playerName)

        # Play the game
        for _ in range(2):
            for player in self.players:
                player.drawCard(self.deck.draw())

        for player in self.players:
            self.manageTurn(player)
