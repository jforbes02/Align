# DB

This folder handles everything related to the database — connecting to it, defining what's stored in it, and migrating it when things change.

---

## database.py

This is where the connection to MySQL is set up. Think of it like dialing into the database before you can read or write anything.

- Reads your database credentials from the `.env` file (username, password, host, database name)
- Creates the **engine** — the thing that actually talks to MySQL
- `get_db()` — opens a database session for a request and closes it when done. Every route that needs the DB uses this
- `dbSession` — a shortcut type so routes can just say `db: dbSession` instead of writing the full dependency every time

---

## models.py

SQLAlchemy translates these Python classes into actual database tables.

### `User`
Stores user accounts.
- `id`, `username`, `password_hash`, `created_at`
- Linked to their sessions and uploaded videos

### `ExerciseSession`
One row per workout. Created every time a user finishes a squat session.
- `user_id` — who did it
- `exercise_type` — e.g. `"squat"`
- `final_score` — percentage of good reps (0–100)
- `rep_count` — how many reps were completed

### `SquatMetrics`
Extra detail attached to each session.
- `good_reps`, `bad_reps` — rep breakdown from the ML model
- `total_frames` — how many camera frames were analyzed

### `Video`
Tracks videos uploaded by users (saved to disk, URL stored here).

### `CorrectVideos`
Reference videos of correct form shown to users. Stored per exercise type.

---

## alembic/

Alembic is a tool for updating your database schema over time without deleting everything and starting over. When you add a new column or table, you write a migration file here and run `alembic upgrade head` to apply it.

Each file in `versions/` is a snapshot of one change — like a git commit, but for database schemas.
