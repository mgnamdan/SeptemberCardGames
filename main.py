# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# HELPER FUNCTIONS AND IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from managers import BlackjackManager, GoFishManager

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN FUNCTION DEFINITION
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def main():
    appOn = True
    blackjack = BlackjackManager()
    goFish = GoFishManager()

    while appOn:
        print("")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("")
        print("              GAMES MENU")
        print("")
        print("             1. Blackjack")
        print("             2. Go Fish")
        print("")
        print("              Q -> QUIT")
        print("")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("")
        playerChoice = input(" --> ").strip().upper()

        if playerChoice == "1":
            playingBlackjack = True
            while playingBlackjack:
                playingBlackjack = blackjack.playGame()
        elif playerChoice == "2":
            playingGoFish = True
            while playingGoFish:
                playingGoFish = goFish.playGame()
        elif playerChoice == "Q":
            appOn = False
        else:
            print("Invalid option!")        



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN FUNCTION CALL
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if __name__ == "__main__":
    main()
