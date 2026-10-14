# September Card Games

Run `python main.py` (or `py -3.11 main.py` on Windows), then choose
`1` for Blackjack, `2` for Go Fish, or `Q` to quit. No third-party packages
are needed.

## Go Fish

Play against 1–4 computers and choose their difficulty for the round.
Two players receive seven cards each; larger groups receive five each.
Ask an opponent with cards for a rank in your own hand, entering the rank
as a word (for example, `Ace` or `Ten`) and the opponent's name.
Names and ranks are case-insensitive.

The opponent gives you every card of that rank. If they have none, draw
from the top, center, or bottom of the pool. Each turn ends after one request
and any fishing, even if you receive or draw the requested rank. Four cards of a rank become
a book and leave your hand. An empty-handed player draws one card before
asking, or skips their turn if the pool is empty. If only one player has
cards, they finish drawing the pool and collect the remaining books.
Play ends when the pool and all hands are empty. Most books wins; ties
are allowed. Replaying starts with a fresh deck, players, and log.

### Computer memory

| Difficulty | Recent public events remembered | Chance to choose randomly |
| --- | ---: | ---: |
| Easy | 4 | 45% |
| Medium | 12 | 20% |
| Hard | 30 | 8% |

`GoFishManager.gameLog` stores chronological dictionaries. Request events
include `asker`, `target`, `rank`, number `received`, whether the asker `drew`,
whether that draw matched (`drawnMatch`), and completed `books`. Refill draws
are separate `type: "draw"` events and also count toward the memory limit.
The log never records a private draw's rank unless it matches the request.

Computers receive only opponent names and their allowed slice of the log.
They infer possession from requests, update that evidence after transfers
and books, and reconsider previous absences after unknown draws. They prefer
remembered holders, then unknown holders, then remembered absences. Within
those groups they prefer ranks they already have more of, breaking ties
randomly. A random decision can still happen to be correct; the percentages
above are chances of ignoring memory, not guaranteed error rates.

Difficulty settings live in `CompGoFishPlayer.DIFFICULTIES` in `players.py`.
For programmatic setup, use
`manager.resetGame("Player", numComps=2, difficulty="hard")`.

## Tests

Run `python -m unittest -v` (or `py -3.11 -m unittest -v`). Tests cover
memory, imperfect choices, transfers, fishing, books, ties, replay setup,
input handling, menu dispatch, and 60 seeded full-game simulations that
check card conservation and completion.
