import random
import time
import hashlib

from game.locations import LOCATIONS

BUYERS = [
    {
        "slot": 1,
        "name": "Jari Jinxu",
        "volume_range": (0.05, 0.25),  # % of storage
        "price_range": (12.5, 15.5),
        "raid_range": (0.25, 0.35),   # High risk buyer
    },
    {
        "slot": 2,
        "name": "Sergei Bogdanov",
        "volume_range": (0.35, 0.65),
        "price_range": (10.5, 13.5),
        "raid_range": (0.15, 0.22),   # Medium risk
    },
    {
        "slot": 3,
        "name": "Ezra Goldstein",
        "volume_range": (0.70, 1.00),
        "price_range": (8.0, 11.5),
        "raid_range": (0.07, 0.13),   # Low base risk
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
        base_raid = random.uniform(*buyer["raid_range"])
        price = round(random.uniform(*buyer["price_range"]), 2)

        offers.append({
            "slot": buyer["slot"],
            "name": buyer["name"],
            "volume_min": vol_min,
            "volume_max": vol_max,
            "price_per_liter": price,
            "base_raid": base_raid,
        })

    return offers