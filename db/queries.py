from db.db import get_db

def get_player(user_id: int):
    db = get_db()
    return db.execute(
        "SELECT * FROM players WHERE user_id = ?",
        (user_id,)
    ).fetchone()

def set_prestige_notified(user_id):
    db = get_db()
    db.execute(
        "UPDATE players SET prestige_notified = 1 WHERE user_id = ?",
        (user_id,)
    )
    db.commit()

def create_player(user_id: int):
    db = get_db()
    db.execute(
        """
        INSERT INTO players (
            user_id, cash, sugar, yeast, moonshine,
            location, current_xp, total_xp, prestige_level
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            500,      # start cash
            0,        # sugar
            0,        # yeast
            0,        # moonshine
            "Shed",
            0,        # current XP
            0,        # total XP
            0         # prestige
        )
    )
    db.execute(
        "INSERT INTO protections (user_id) VALUES (?)",
        (user_id,)
    )
    db.commit()

from game.locations import get_location_index, LOCATIONS

SUGAR_PRICE = 1
YEAST_PRICE = 2


def update_player_resources(
    user_id: int,
    cash_delta: int = 0,
    sugar_delta: int = 0,
    yeast_delta: int = 0,
    moonshine_delta: int = 0
):
    db = get_db()

    player = db.execute(
        "SELECT * FROM players WHERE user_id = ?",
        (user_id,)
    ).fetchone()

    if not player:
        return

    location_index = get_location_index(player["location"])
    location = LOCATIONS[location_index]

    max_sugar = location["max_sugar"]
    max_yeast = location["max_yeast"]

    # Current values
    new_sugar = player["sugar"] + sugar_delta
    new_yeast = player["yeast"] + yeast_delta
    new_cash = player["cash"] + cash_delta
    new_moonshine = player["moonshine"] + moonshine_delta

    overflow_cash = 0

    # --- Sugar cap ---
    if new_sugar > max_sugar:
        overflow = new_sugar - max_sugar
        overflow_cash += overflow * SUGAR_PRICE
        new_sugar = max_sugar

    if new_sugar < 0:
        new_sugar = 0

    # --- Yeast cap ---
    if new_yeast > max_yeast:
        overflow = new_yeast - max_yeast
        overflow_cash += overflow * YEAST_PRICE
        new_yeast = max_yeast

    if new_yeast < 0:
        new_yeast = 0

    new_cash += overflow_cash

    if new_cash < 0:
        new_cash = 0

    if new_moonshine < 0:
        new_moonshine = 0

    db.execute(
        """
        UPDATE players
        SET cash = ?,
            sugar = ?,
            yeast = ?,
            moonshine = ?
        WHERE user_id = ?
        """,
        (new_cash, new_sugar, new_yeast, new_moonshine, user_id)
    )

    db.commit()

def get_active_batch(user_id: int):
    db = get_db()
    return db.execute(
        "SELECT * FROM batches WHERE user_id = ?",
        (user_id,)
    ).fetchone()

def create_batch(user_id, liters, start_time, end_time, will_fail, fail_time, channel_id):
    db = get_db()
    db.execute(
        """
        INSERT INTO batches (user_id, liters, start_time, end_time, will_fail, fail_time, channel_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (user_id, liters, start_time, end_time, will_fail, fail_time, channel_id)
    )
    db.commit()

def delete_batch(user_id: int):
    db = get_db()
    db.execute(
        "DELETE FROM batches WHERE user_id = ?",
        (user_id,)
    )
    db.commit()

def add_xp(user_id: int, amount: int):
    db = get_db()
    db.execute(
        """
        UPDATE players
        SET current_xp = current_xp + ?,
            total_xp = total_xp + ?
        WHERE user_id = ?
        """,
        (amount, amount, user_id)
    )
    db.commit()

def get_top_players(limit: int = 10):
    db = get_db()
    cursor = db.execute(
        """
        SELECT user_id, total_xp, prestige_level
        FROM players
        ORDER BY total_xp DESC
        LIMIT ?
        """,
        (limit,)
    )
    return cursor.fetchall()

def get_global_rank(user_id: int):
    db = get_db()

    cursor = db.execute(
        """
        SELECT COUNT(*) + 1 AS rank
        FROM players
        WHERE total_xp > (
            SELECT total_xp FROM players WHERE user_id = ?
        )
        """,
        (user_id,)
    )
    row = cursor.fetchone()
    return row["rank"] if row else None

def get_all_active_batches():
    db = get_db()
    return db.execute("SELECT * FROM batches").fetchall()

def get_exposure(player_id: int, hour: int):
    db = get_db()
    row = db.execute(
        "SELECT exposure FROM exposure WHERE player_id = ? AND hour = ?",
        (player_id, hour)
    ).fetchone()

    return row["exposure"] if row else 0


def set_exposure(player_id: int, hour: int, exposure: int):
    db = get_db()
    db.execute(
        """
        INSERT INTO exposure (player_id, hour, exposure)
        VALUES (?, ?, ?)
        ON CONFLICT(player_id, hour)
        DO UPDATE SET exposure = excluded.exposure
        """,
        (player_id, hour, exposure)
    )
    db.commit()