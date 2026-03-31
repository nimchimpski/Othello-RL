# Othello Player. Reinforcement learning with q-Table #

*[CLICK TO PLAY!](http://217.174.244.37:5003/)*

### In Train function: ### 
A model playes itself, (always as black using state inversion).
Epsilon Greedy with a decay function ensures sufficient exploration outside the previously learnt policy.
A Heuristic evaluation function is used after every move to update the q-table.

### In Evaluate function: ### 
The model, using a specified q-table, playes against a random player.\
Win rate and win/loss ratio are recorded.

### Flask ###
A flask app presents a web page game where the user can play a model, using a predetermined Q-table.
The baord is updated with AJAX.

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

Add a UI switch so the player can choose between:
- **Pure Q-table mode** (current): action selected solely from Q-table lookup; falls back to random for unseen states
- **Heuristic-assisted mode**: for unseen/tied states, rank available moves using the existing `evalweights()` positional weight matrix (corners > edges > centre) instead of random selection

Implementation sketch:
- Pass a `use_heuristic=True/False` flag from the frontend toggle to the `/othello/play` route
- In `OthelloAI.choose_action()`, when no Q-value is available (or values are tied), fall back to `evalweights()` to pick the best-weighted available move rather than choosing randomly
- No retraining required — purely a change to inference-time action selection

This would immediately improve play quality in the opening and mid-game where state-space coverage is sparse, while keeping the pure RL mode available for comparison.

