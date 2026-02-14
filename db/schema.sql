PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS players (
    user_id             INTEGER PRIMARY KEY,
    cash                INTEGER NOT NULL,
    sugar               INTEGER NOT NULL,
    yeast               INTEGER NOT NULL,
    moonshine           INTEGER NOT NULL,

    location            TEXT NOT NULL,

    current_xp          INTEGER NOT NULL,
    total_xp            INTEGER NOT NULL,

    prestige_level      INTEGER NOT NULL,

    notified_location   INTEGER NOT NULL DEFAULT 0,
    notified_prestige   INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS active_batches (
    user_id         INTEGER PRIMARY KEY,
    liters          INTEGER NOT NULL,
    start_time      INTEGER NOT NULL,
    end_time        INTEGER NOT NULL,

    will_fail       INTEGER NOT NULL,
    fail_time       INTEGER,

    FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS protections (
    user_id             INTEGER PRIMARY KEY,

    mold_tier           INTEGER NOT NULL DEFAULT 0,
    raid_bribes         INTEGER NOT NULL DEFAULT 0,
    raid_storage        INTEGER NOT NULL DEFAULT 0,
    raid_network        INTEGER NOT NULL DEFAULT 0,

    FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS exposure (
    player_id INTEGER,
    hour INTEGER,
    exposure INTEGER,
    PRIMARY KEY (player_id, hour)
);
