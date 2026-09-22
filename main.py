# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# HELPER FUNCTIONS AND IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from decks import Deck
from cards import Card
from players import CompBlackjackPlayer



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN FUNCTION DEFINITION
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def main():
    testDeck = Deck()
    aceOne = Card("Ace", "Clubs")
    aceTwo = Card("Ace", "Spades")
    aceThree = Card("Ace", "Hearts")
    player = CompBlackjackPlayer("Danny")

    player.drawCard(testDeck.draw())
    player.drawCard(testDeck.draw())

    print("")
    print(f"{player.hand}")
    print("")

    player.showHand()

    player.drawCard(aceOne)
    player.drawCard(aceTwo)
    player.drawCard(aceThree)

    player.showHand()

    player.calcScore()
    print(player.giveScore())
    print(player.makeChoice())



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN FUNCTION CALL
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
main()
