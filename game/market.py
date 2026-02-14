import random
import time
import hashlib

from game.locations import LOCATIONS

BUYERS = [
    {
        "slot": 1,
        "name": "HIV infected Rico",
        "volume_range": (0.10, 0.20),  # % of storage
        "price_range": (12.5, 14.0),
        "base_raid": 0.28,
    },
    {
        "slot": 2,
        "name": "Drunk Daren",
        "volume_range": (0.35, 0.55),
        "price_range": (11.2, 12.3),
        "base_raid": 0.18,
    },
    {
        "slot": 3,
        "name": "Syndicate Sam",
        "volume_range": (0.70, 1.00),
        "price_range": (10.5, 11.5),
        "base_raid": 0.10,
    },
]


def get_market_seed(location_index: int):
    current_hour = int(time.time() // 3600)
    raw = f"{location_index}-{current_hour}"
    hashed = hashlib.sha256(raw.encode()).hexdigest()
    return int(hashed[:16], 16)


def generate_market(location_index: int):
    seed = get_market_seed(location_index)
    random.seed(seed)

    location = LOCATIONS[location_index]
    max_storage = location["max_storage"]

    offers = []

    for buyer in BUYERS:
        min_pct, max_pct = buyer["volume_range"]
        vol_min = int(max_storage * min_pct)
        vol_max = int(max_storage * max_pct)

        price = round(random.uniform(*buyer["price_range"]), 2)

        offers.append({
            "slot": buyer["slot"],
            "name": buyer["name"],
            "volume_min": vol_min,
            "volume_max": vol_max,
            "price_per_liter": price,
            "base_raid": buyer["base_raid"],
        })

    return offers