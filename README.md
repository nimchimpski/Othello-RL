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

