# scores

This folder handles rep counting, ML-based form scoring, and saving a completed workout to the database.

---

## scoring.py

Takes the stream of per-frame joint data from `vision/` and turns it into a final workout result.

---

### RepCounter

Tracks where you are in a squat rep using a state machine. Think of it like a checklist that the squat has to pass through in order.

```
STANDING → DESCENDING → AT_BOTTOM → ASCENDING → STANDING (rep counted)
```

States:
- **STANDING** — knee angle above 170°, you're upright
- **DESCENDING** — you've started bending your knees
- **AT_BOTTOM** — knee angle dropped below 100° (actual squat depth reached)
- **ASCENDING** — you're coming back up

To avoid counting noise (like a slight wobble) as a state change, it requires **4 frames in a row** before confirming a transition. If you start going down but come back up before hitting depth, that rep is thrown out.

Each completed rep stores all its frame data for scoring later.

**`on_frame(features)`** — call this every frame with the extracted features dict. The counter handles everything internally.

**`rep_count`** — property that returns how many valid reps have been completed.

---

### ML Scoring

**`load_model()`**
Reads the trained neural network weights from `ml/trained_angles_weights.json` at startup. Only runs once.

**`ml_predict(features)`**
Runs one set of 8 joint angles through the neural network and returns:
- `1` = good form
- `-1` = bad form

The angles are normalized by dividing by 360 before being fed in (same as during training).

**`score_session(rep_counter)`**
Called when the workout ends. For each completed rep, it averages the 8 ML angles across all frames in that rep and calls `ml_predict`. Returns a summary dict:
```python
{
    "rep_count": 5,
    "good_reps": 4,
    "bad_reps": 1,
    "reps": [
        {"rep": 1, "form": "good"},
        {"rep": 2, "form": "bad"},
        ...
    ]
}
```

---

### Saving to the database

**`save_session(scores, user_id, total_frames)`**
Takes the output of `score_session` and writes two rows to the database:
1. An `ExerciseSession` with the final score (% good reps) and rep count
2. A `SquatMetrics` row with the good/bad rep breakdown and total frames analyzed

Returns the new session ID, which gets sent back to the Android app so it can show the results screen.
