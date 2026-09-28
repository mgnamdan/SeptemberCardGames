# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# HELPER FUNCTIONS AND IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from managers import BlackjackManager

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN FUNCTION DEFINITION
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def main():
    appOn = True
    blackjack = BlackjackManager()

    while appOn:
        print("")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("")
        print("              GAMES MENU")
        print("")
        print("             1. Blackjack")
        print("")
        print("              Q -> QUIT")
        print("")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("")
        playerChoice = input(" --> ")

        if playerChoice == "1":
            playingBlackjack = True
            while playingBlackjack:
                playingBlackjack = blackjack.playGame()
        elif playerChoice == "Q":
            appOn = False
        else:
            print("Invalid option!")        



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN FUNCTION CALL
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
main()
