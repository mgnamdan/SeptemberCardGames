# The Velvet Table

A complete Pygame desktop rewrite of September Card Games: three playable
tables, original pixel art, green felt, brass trim and a quiet card-lounge mood.
The old terminal menus have been replaced by a resizable, mouse-driven interface.

## Play

Python 3.11 or newer is required. Install the pinned Pygame Community Edition
dependency, then launch from this directory:

```powershell
py -3.11 -m pip install -r requirements.txt
py -3.11 main.py
```

On Windows, you can also double-click **Play.bat** after installation. On other
platforms use `python3` in place of `py -3.11`. This version was tested on Windows
with Python 3.11 and pygame-ce 2.5.8. It uses no network connection during play.

Choose a table in the lobby, configure it, then select **Deal me in**. All art,
card backs, portraits and sound effects are generated locally; no asset downloads
or external fonts are required. A monospace system font is used when available.

## The tables

### Blackjack

Play against a dealer using play chips. Choose a stake of 10, 25, 50 or 100.
Hit, stand, double down or split matching ranks into up to four hands. Aces
count as 1 or 11; faces count as 10. There is no five-card automatic win.

The dealer stands on all 17s. A natural blackjack pays 3:2, ordinary wins pay
1:1, and a push returns the stake. Half-chip payouts round down. Split 21s
are ordinary hands; split aces receive one card each. Double is available
on a two-card hand if you can afford it. Insurance and surrender are not included.
The dealer's second card stays hidden until the dealer phase.

You start with 1,000 play chips. If your balance drops below 10, the setup
panel offers a free refill. Chips have no real-world value. Leaving a round
or closing the app forfeits chips already staked.

### Go Fish

Play against 1–4 computers. Two players receive seven cards each; larger tables
receive five. Click a rank in your hand, click an opponent with cards, then click
**Ask for cards**. They transfer every card of that rank. If they have none,
choose the top, center or bottom of the pool to draw from.

**Every request ends the turn after any fishing. There are no extra asks for
successful requests or matching draws.** An empty hand draws one card before
asking, or skips if the pool is empty. The last player with cards collects the
remaining pool, one draw at a time. Books of four leave the hand automatically.
Most books wins, with ties allowed.

| Difficulty | Recent public events remembered | Chance of ignoring memory |
| --- | ---: | ---: |
| Easy | 4 | 45% |
| Medium | 12 | 20% |
| Hard | 30 | 8% |

Computers receive only names and the permitted slice of `gameLog`, never opponents'
hands. Requests reveal possession; transfers, books and unknown draws update that
evidence. Remembered holders are preferred over unknown holders, then known
absences. Ties favor ranks already held in greater numbers. Random choices can
still be correct; the percentages are not guaranteed error rates.

The manager's full public log records asker, target, rank, transferred count,
whether fishing occurred, whether it matched, and completed books. Refill draws
also consume memory slots. Nonmatching private draw ranks never enter this log.
The on-screen notes can show your own private draw, but computer strategy receives
only the separate public log.

### Memory Match

A solo 24-card table with twelve pairs. Click two cards per move. Matching pairs
stay visible; mismatches flip back after a short pause. There is no timer. Finish
in as few moves as possible; your best move count is saved.

## Controls and conveniences

- Mouse: select cards, opponents and buttons.
- Blackjack shortcuts: **H** hit, **S** stand, **D** double, **P** split.
- **Tab / Shift+Tab**, then **Enter / Space**: navigate and activate controls.
- **Esc**: close a panel or open the leave-round confirmation.
- Scroll over **Table Notes** to read earlier actions.
- **Sound** toggles synthesized effects; **Pace** changes computer action speed.
- **How to play** opens the current table's rules and pauses automatic actions.
- Resize the window freely; the table scales and letterboxes without cropping.

Name, difficulty, opponent count, stake, sound, pace, chips, completed rounds and
the best Memory Match score are saved beside the app in `savegame.json`. Malformed
saves fall back to defaults. Delete that file to reset your profile. Active rounds
are not saved or resumed. Save files and generated previews are ignored by Git.

## Architecture

| File | Responsibility |
| --- | --- |
| `main.py` | Launch and command-line options |
| `gui.py` | Lobby, setup, tables, panels, controls, animation and local profile |
| `art.py` | Procedural pixel cards, portraits, chips, felt, fonts and colors |
| `managers.py` | Event-driven Blackjack, Go Fish and Memory Match managers |
| `players.py` | Blackjack hand state and Go Fish players / imperfect AI |
| `cards.py` | Immutable cards and ace-aware Blackjack scoring |
| `decks.py` | Shuffled 52-card deck and draw/discard operations |
| `currency.py` | Validated play-chip wallet |

Managers contain no Pygame imports, input prompts, sleeps or print loops. The GUI
invokes an action and returns to its event loop. Timed `step()` calls advance
computer decisions, dealer draws or mismatched memory cards. The UI validates
available actions, and managers independently reject illegal actions. Each table
has its own manager, making additional games straightforward to add.

The former placeholder currency converter was replaced with a play-chip wallet;
card equality now compares both rank and suit. Blackjack splitting explicitly
compares ranks instead. The old architecture PNG is a historical design artifact.

## Verification

```powershell
py -3.11 -m unittest -v
py -3.11 main.py --smoke-test
```

The test suite covers rules, payout accounting, split hands, imperfect memory,
private information, card conservation, local saves and GUI input/navigation.
It simulates 120 complete Go Fish games and 300 Blackjack rounds. GUI tests use
SDL's offscreen driver, including real Pygame mouse and keyboard events.

The smoke test renders lobby, setup, table, rules, crowded-hand and result screens
to `screenshots/`. Use `--screenshots PATH` to choose another output directory.
It uses a separate smoke-test save and does not modify your player profile.

Pygame API reference: [pygame-ce display documentation](https://pyga.me/docs/ref/display.html).
