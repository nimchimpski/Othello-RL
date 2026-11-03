# Othello Player. Reinforcement learning with q-Table #

*[CLICK TO PLAY!](https://nimchimpski.com/othello/)*

### In Train function: ### 
A model playes itself, (always as black using state inversion).
Epsilon Greedy with a decay function ensures sufficient exploration outside the previously learnt policy.
The reward is 0 for every move except the last: the winner's and loser's final moves are set to +1 and -1 (0 for a tie), and earlier moves learn from it through the Q-learning update. No heuristic is used in training.

### In Evaluate function: ### 
The model, using a specified q-table, playes against a random player.\
Win rate and win/loss ratio are recorded.

### Flask ###
A flask app presents a web page game where the user can play a model, using a predetermined Q-table.
The baord is updated with AJAX.

The AI picks the move with the highest Q-value. The Q-table only covers a small part of the 6x6 state space, so many positions are not in it. For those the web app falls back to a positional heuristic (`OthelloAI.choose_evaluated_action()`). Each legal move is scored as its own square value (`OthelloAI.evaluate_action()`, table below) plus `LOOKAHEAD_WEIGHT` times a one-ply lookahead: the move is played on a copy of the board and the resulting position is scored by `OthelloAI.evaluate_board()` (square values, frontier discs, mobility and, in the endgame, disc ratio, from the mover's perspective). Equally-scored moves are chosen randomly:

| Square | Score |
|---|---|
| Corner | +0.9 |
| Next to a corner you hold (C- and X-squares) | +0.6 |
| Edge, connected to a corner you hold | +0.5 |
| Other edge square | +0.3 |
| Centre, or next to a corner the opponent already holds | 0 |
| One square in from an edge that is still empty | -0.3 |
| Next to a corner that is still empty (C- and X-squares) | -0.9 |

The fallback is switched on with `aimoves(..., use_heuristic=True)`, which only `app.py` does. Training and `evaluate()` keep the original random fallback, so their behaviour and benchmark numbers are unchanged.

In ad-hoc test games (not part of the repo), with colours alternating:
- The Q-table alone found the position in its table for only ~13% of its moves; the rest were random.
- The heuristic on its own beat the Q-table AI 95-4 and a random player 96-4 (100 games each).
- A small 3-ply search using corner, X-square and mobility terms beat the heuristic 55-4 (60 games), so the heuristic is a static weighting rather than a strong player.

### Training Performance ###
Profiling (cProfile, 50 games) reveals the following hotspots:

| Function | % of time | Calls (50 games) | Notes |
|---|---|---|---|
| `calcnextcell` | ~36% | ~1M | Per-step direction arithmetic |
| `direction_checker` | ~23% | ~820k | Walks each direction for valid moves/flips |
| `available_actions` | ~9% | ~6.4k | Calls the above two repeatedly |
| `deepcopy` | ~5% | ~170k | Full board copy per move |

**Potential optimisations:**
- Inline `calcnextcell` into `direction_checker` to eliminate function-call overhead (~60% of time is in these two)
- Replace `deepcopy` with shallow list copy or immutable board representation
- Fine-tune existing Q-tables by re-running `train()` with the same filename — it auto-loads and continues training
- Note: restarting training resets alpha to 0.5 (high), so short top-ups (<20k games) may temporarily degrade performance before improving it

**Development Idea:**
- Refactor training and evaluation code to use NumPy vectorized operations instead of Python loops where possible. This can significantly speed up array and matrix manipulations, especially in Q-table updates and board evaluations.

### Planned Development ###

**Heuristic-guided play mode (user toggle)**

The heuristic fallback described above is now always on in the web app. Still to do is a UI switch so the player can compare:
- **Pure Q-table mode**: action selected solely from Q-table lookup; falls back to random for unseen states
- **Heuristic-assisted mode** (current behaviour): unseen states use `evaluate_action()` instead of random selection

Implementation sketch:
- Pass a `use_heuristic=True/False` flag from the frontend toggle to the `/play` route (the page sets the URL via `PLAY_URL`, which is `/othello/play` behind nginx)
- Hand that flag to `game.aimoves(..., use_heuristic=...)` in `app.py`
- No retraining required — purely a change to inference-time action selection

Other ideas:
- Add a one-move lookahead: reject a move if it lets the opponent take a corner on their reply
- Replace the static weights with a shallow search (see the 3-ply result above)
- Also use the heuristic to break ties between equal Q-values (currently only used when the position is unknown)
- `OthelloAI.generate_2_tuples()` is a partially developed, unused start on an n-tuple network: it lists every pair of neighbouring squares (horizontal, vertical, both diagonals). The missing parts are a weight table per tuple, a position evaluator that sums the lookups, and the learning update. Unlike the Q-table it would generalise across positions that share local patterns, so it is an interesting direction.

