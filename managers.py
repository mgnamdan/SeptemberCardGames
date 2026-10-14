import random
from players import (CompBlackjackPlayer, HumBlackjackPlayer,
                     CompGoFishPlayer, HumGoFishPlayer)
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
        self.players = []
        self.deck = Deck()
        self.gameLog = []


    def resetGame(self, playerName, numComps=None, difficulty=None):
        """Start a fresh round; optional settings also allow noninteractive setup."""
        if numComps is None:
            while True:
                try:
                    numComps = int(input("How many computers? (1-4)\n\n --> "))
                    if 1 <= numComps <= 4:
                        break
                except ValueError:
                    pass
                print("Enter a number from 1 to 4.\n")
        if not isinstance(numComps, int) or not 1 <= numComps <= 4:
            raise ValueError("Choose between 1 and 4 computers.")

        if difficulty is None:
            while True:
                difficulty = input("Computer difficulty (easy/medium/hard):\n\n --> ").strip().lower()
                if difficulty in CompGoFishPlayer.DIFFICULTIES:
                    break
                print("Choose easy, medium, or hard.\n")
        difficulty = difficulty.strip().lower()
        if difficulty not in CompGoFishPlayer.DIFFICULTIES:
            raise ValueError("Difficulty must be easy, medium, or hard.")

        playerName = playerName.strip() or "Player"
        names = [name for name in self.COMPNAMES
                 if name.casefold() != playerName.casefold()]
        self.players = [HumGoFishPlayer(playerName)]
        self.players.extend(CompGoFishPlayer(name, difficulty)
                            for name in random.sample(names, numComps))
        self.deck.reset()
        self.gameLog = []
        handSize = 7 if len(self.players) == 2 else 5
        for _ in range(handSize):
            for player in self.players:
                player.drawCard(self.deck.draw())
        for player in self.players:
            self._announceBooks(player, player.collectSets())


    def _announceBooks(self, player, books):
        for rank in books:
            print(f"{player.name} completed a book of {rank}s!\n")

    def isGameOver(self):
        return bool(self.players) and not self.deck.drawPile and not any(
            player.hasCards() for player in self.players)

    def manageTurn(self, player):
        """Resolve one request and any fishing, then end the turn."""
        if not self.isGameOver():
            if not player.hasCards():
                if not self.deck.drawPile:
                    return
                player.drawCard(self.deck.draw(player.goFish(len(self.deck.drawPile))))
                books = player.collectSets()
                self.gameLog.append({"type": "draw", "asker": player.name,
                                     "drew": True, "books": books})
                print(f"{player.name} drew a card to refill their empty hand.\n")
                self._announceBooks(player, books)

            opponents = {other.name: other for other in self.players
                         if other is not player and other.hasCards()}
            if not opponents:
                # Any remaining cards must complete this player's books.
                # Drain the pool without attempting an illegal request.
                while self.deck.drawPile:
                    player.drawCard(self.deck.draw(player.goFish(len(self.deck.drawPile))))
                    books = player.collectSets()
                    self.gameLog.append({"type": "draw", "asker": player.name,
                                         "drew": True, "books": books})
                    self._announceBooks(player, books)
                return

            if isinstance(player, HumGoFishPlayer):
                rank, targetName = player.makeChoice(list(opponents))
            else:
                memoryLength = player.DIFFICULTIES[player.difficulty][0]
                # Pass names, never opponent objects or private hands.
                rank, targetName = player.makeChoice(list(opponents),
                                                     self.gameLog[-memoryLength:])
            if rank not in player.hand or not player.hand[rank] or targetName not in opponents:
                raise ValueError("Players must ask an eligible opponent for a rank they hold.")
            print(f"{player.name} asks {targetName} for {rank}s.\n")
            received = opponents[targetName].giveSet(rank)
            drew = False
            drawnMatch = False
            if received:
                for card in received:
                    player.drawCard(card)
                print(f"{targetName} gives {player.name} {len(received)} card(s).\n")
            else:
                print("Go fish!\n")
                if self.deck.drawPile:
                    card = self.deck.draw(player.goFish(len(self.deck.drawPile)))
                    player.drawCard(card)
                    drew = True
                    drawnMatch = card.rank == rank
                    if isinstance(player, HumGoFishPlayer):
                        print(f"You drew {card}.\n")
                    elif drawnMatch:
                        print(f"{player.name} fished the requested rank!\n")
                else:
                    print("The pool is empty.\n")

            books = player.collectSets()
            self._announceBooks(player, books)
            # Deliberately omit the rank of a private, nonmatching draw.
            self.gameLog.append({"type": "ask", "asker": player.name,
                                 "target": targetName, "rank": rank,
                                 "received": len(received), "drew": drew,
                                 "drawnMatch": drawnMatch, "books": books})


    def determineWinner(self):
        if not self.players:
            return []
        highScore = max(len(player.sets) for player in self.players)
        winners = [player for player in self.players if len(player.sets) == highScore]
        for player in self.players:
            print(f"{player.name}: {len(player.sets)} book(s)\n")
        names = ", ".join(player.name for player in winners)
        print(f"{names} {'wins' if len(winners) == 1 else 'tie'} with {highScore} book(s)!\n")
        return winners


    def promptNextGame(self):
        while True:
            choice = input("Play another game of Go Fish? (y/n)\n\n --> ").strip().lower()
            if choice in ["y", "yes"]:
                return True
            if choice in ["n", "no", "quit", "exit", "return"]:
                return False
            print("Please answer yes or no.\n")


    def playGame(self):
        playerName = input("What is your name?\n\n --> ")
        self.resetGame(playerName)
        print("Collect books of four. Ask for a rank you hold. Most books wins!\n")
        print("Each turn ends after one request and any fishing, even if you get the requested rank.\n")
        while not self.isGameOver():
            for player in self.players:
                if self.isGameOver():
                    break
                self.manageTurn(player)
        self.determineWinner()
        return self.promptNextGame()
