LOCATIONS = [
    {
        "name": "Shed",
        "max_batch": 600,
        "max_storage": 1200,
        "max_sugar": 600,
        "max_yeast": 120,
        "upgrade_cost": 0,
        "upgrade_xp": 0,
    },
    {
        "name": "Garage",
        "max_batch": 1500,
        "max_storage": 3000,
        "max_sugar": 1500,
        "max_yeast": 300,
        "upgrade_cost": 35_000,
        "upgrade_xp": 60_000,
    },
    {
        "name": "Warehouse",
        "max_batch": 4000,
        "max_storage": 8000,
        "max_sugar": 4000,
        "max_yeast": 800,
        "upgrade_cost": 250_000,
        "upgrade_xp": 180_000,
    },
    {
        "name": "Harbour",
        "max_batch": 10_000,
        "max_storage": 20_000,
        "max_sugar": 10_000,
        "max_yeast": 2000,
        "upgrade_cost": 400_000,
        "upgrade_xp": 600_000,
    },
    {
        "name": "Distillery",
        "max_batch": 30_000,
        "max_storage": 60_000,
        "max_sugar": 30_000,
        "max_yeast": 6000,
        "upgrade_cost": 900_000,
        "upgrade_xp": 1_500_000,
    },
]

def get_location_index(name: str) -> int:
    for i, loc in enumerate(LOCATIONS):
        if loc["name"] == name:
            return i
    raise ValueError(f"Unknown location: {name}")
