import random
from players import CompBlackjackPlayer, HumBlackjackPlayer
from decks import Deck



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#
#                       BLACKJACK MANAGER
#
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


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
        # Look through all of our scores and find the highest score not over 21
        # Log all players with that score
        # If there's only one player with score, they win
        # If multiple have highscore:
        #      If one of those players is the dealer, the dealer wins
        #      Otherwise all players with the highscore win
        #
        #      One winner, two winners, 3+ winners
        highScore = 0
        for player in self.players:
            for handNum in player.scores.keys():
                if player.scores[handNum] > highScore and player.scores[handNum] < 22:
                    highScore = player.scores[handNum]

        winners = []

        for player in self.players:
            for handNum in player.scores.keys():
                if player.scores[handNum] == highScore:
                    if player not in winners:
                        winners.append(player)

        if len(winners) == 0:
            # Nobody won
            print("")
            print("Everyone busted - nobody wins!")
        elif len(winners) == 1:
            # Only one winner
            print("")
            print(f"{winners[0]} won with a score of {highScore}!")
        else:
            if self.dealer in winners:
                # Dealer wins
                print("")
                print(f"The dealer wins with a score of {highScore} - better luck next time!")
            else:
                if len(winners) == 2:
                    # Two winners
                    print("")
                    print(f"{winners[0]} and {winners[1]} win with a high score of {highScore}!")
                else:
                    # More than two winners
                    message = ""
                    for idx in range(len(winners)):
                        if idx == 0:
                            message += f"{winners[idx]}"
                        elif idx == len(winners) - 1:
                            message += f", and {winners[idx]} win with a high score of {highScore}!"
                        else:
                            message += f", {winners[idx]}"
                    print("")
                    print(message)               


    def promptNextGame(self):
        validChoice = False
        while not validChoice:
            print("")
            print("Would you like to play another game of blackjack? (y/n)")
            playerChoice = input(" --> ").lower()

            if playerChoice in ["y", "yes"]:
                nextGame = True
                validChoice = True
            elif playerChoice in ["n", "no", "quit", "exit", "return"]:
                nextGame = False
                validChoice = True
            else:
                print("Invalid choice - please try again!")
        return nextGame


    def manageTurn(self, player):
        handNum = 1
        while handNum <= len(player.hand.keys()):

            player.showHand(handNum)
            validSplit = (len(player.hand[handNum]) == 2) and (player.hand[handNum][0] == player.hand[handNum][1])
            choice = player.makeChoice(handNum)

            if choice == "split" and validSplit:
                # Implement the split
                splitCard = player.hand[handNum].pop()
                newHand = [splitCard]
                player.hand[handNum+1] = newHand
                player.drawCard(self.deck.draw(), handNum)
                player.drawCard(self.deck.draw(), handNum+1)
            elif choice == "split" and not validSplit:
                print("You shall NOT split!")
            elif choice == "hit":
                player.drawCard(self.deck.draw(), handNum)
            else:
                handNum += 1


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
            for hand in player.hand.keys():
                player.calcScore(hand)

        self.determineWinner()

        return self.promptNextGame()



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#
#                       GO FISH MANAGER
#
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class GoFishManager:

    COMPNAMES = ["Alex", "Ben", "Claire", "Danny", "Emily", "Felix", "Grace", "Henry", "Isabella", "Jack", "Kayla", "Liam", "Morgan",
                 "Nathan", "Olivia", "Pat", "Quinn", "Ryan", "Sophie", "Taylor", "Uma", "Victor", "Willow", "Xavier", "Yasmine", "Zach"]


    def __init__(self):
        pass


    def resetGame(self):
        pass


    def manageTurn(self):
        pass


    def determineWinner(self):
        pass


    def promptNextGame(self):
        pass


    def playGame(self):
        pass
