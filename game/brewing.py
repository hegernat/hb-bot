import time
from game.locations import LOCATIONS, get_location_index

from db.queries import (
    get_player,
    get_active_batch,
    update_player_resources,
    delete_batch,
)


def resolve_batch_if_needed(user_id: int):

    player = get_player(user_id)
    batch = get_active_batch(user_id)
    if not batch:
        return None

    now = int(time.time())

    # --- Mold failure ---
    if batch["will_fail"] and batch["fail_time"] and now >= batch["fail_time"]:
        total_duration = batch["end_time"] - batch["start_time"]
        remaining = max(0, batch["end_time"] - now)

        base_ratio = remaining / total_duration if total_duration > 0 else 0

        mold_tier = player["mold_protection"] or 0
        min_ratio = 0.15 + (0.05 * mold_tier)

        refund_ratio = max(base_ratio, min_ratio)
        refund_ratio = min(refund_ratio, 0.95)

        refund_liters = int(batch["liters"] * refund_ratio)

        refund_sugar = refund_liters
        refund_yeast = refund_liters // 5

        if refund_sugar > 0 or refund_yeast > 0:
            update_player_resources(
                user_id,
                sugar_delta=refund_sugar,
                yeast_delta=refund_yeast
            )

        delete_batch(user_id)

        return {
            "type": "mold",
            "refund_sugar": refund_sugar,
            "refund_yeast": refund_yeast
        }

    # --- Successful completion ---
    if now >= batch["end_time"]:

        current_moonshine = player["moonshine"] or 0
        location_index = get_location_index(player["location"])
        location = LOCATIONS[location_index]
        max_storage = location["max_storage"]
        liters = batch["liters"]

        space_left = max_storage - current_moonshine
        moonshine_to_add = max(0, min(liters, space_left))

        update_player_resources(
            user_id,
            moonshine_delta=moonshine_to_add
        )

        overflow = liters - moonshine_to_add

        delete_batch(user_id)

        return {
            "type": "complete",
            "liters": moonshine_to_add,
            "overflow": overflow
        }

    return None