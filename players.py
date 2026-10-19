"""Player state and imperfect Go Fish strategy, independent of the GUI."""
import random
from dataclasses import dataclass, field
from cards import RANKS, hand_value


@dataclass
class BlackjackHand:
    cards: list = field(default_factory=list)
    bet: int = 50
    done: bool = False
    split: bool = False
    result: str = ""

    @property
    def score(self):
        return hand_value(self.cards)

    @property
    def natural(self):
        return not self.split and len(self.cards) == 2 and self.score == 21


class CompGoFishPlayer:
    DIFFICULTIES = {"easy": (4, .45), "medium": (12, .20), "hard": (30, .08)}

    def __init__(self, name, difficulty="medium"):
        if difficulty not in self.DIFFICULTIES:
            raise ValueError("Choose easy, medium, or hard")
        self.name, self.difficulty = name, difficulty
        self.hand = {rank: [] for rank in RANKS}
        self.sets = {}

    def drawCard(self, card):
        self.hand[card.rank].append(card)

    def giveSet(self, rank):
        cards, self.hand[rank] = self.hand[rank], []
        return cards

    def collectSets(self):
        completed = []
        for rank, cards in self.hand.items():
            if len(cards) == 4:
                self.sets[rank] = self.giveSet(rank)
                completed.append(rank)
        return completed

    def hasCards(self):
        return any(self.hand.values())

    @property
    def count(self):
        return sum(map(len, self.hand.values()))

    def goFish(self, size):
        if size <= 0:
            raise ValueError("Cannot fish from an empty deck")
        return random.choice([0, (size - 1) // 2, size - 1])

    def makeChoice(self, otherPlayers, gameLog=None):
        ranks = [rank for rank, cards in self.hand.items() if cards]
        opponents = [name for name in otherPlayers if name != self.name]
        choices = [(rank, name) for rank in ranks for name in opponents]
        if not choices:
            raise ValueError("A choice needs cards and an opponent")
        memory, mistake = self.DIFFICULTIES[self.difficulty]
        knowledge = {}
        for event in (gameLog or [])[-memory:]:
            asker = event["asker"]
            if event["type"] == "ask":
                knowledge[asker, event["rank"]] = True
                knowledge[event["target"], event["rank"]] = False
            if event["drew"]:
                knowledge = {key: value for key, value in knowledge.items()
                             if key[0] != asker or value}
            for rank in event["books"]:
                for name in [self.name] + opponents:
                    knowledge[name, rank] = False
        if random.random() < mistake:
            return list(random.choice(choices))

        def score(choice):
            rank, name = choice
            evidence = knowledge.get((name, rank))
            return (2 if evidence is True else 0 if evidence is False else 1,
                    len(self.hand[rank]))

        best = max(map(score, choices))
        return list(random.choice([choice for choice in choices if score(choice) == best]))


class HumGoFishPlayer(CompGoFishPlayer):
    """The GUI supplies choices; the human shares the same card operations."""
