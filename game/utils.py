from game.locations import LOCATIONS, get_location_index

PRESTIGE_BASE_XP = 3_500_000

def prestige_xp_required(prestige_level: int) -> int:
    return PRESTIGE_BASE_XP * (prestige_level + 1)

def fmt(number: int) -> str:
    number = int(number)

    def format_large(value: float, suffix: str) -> str:
        """
        Dynamisk decimal-logik:
        >= 100  → 1 decimal
        >= 10   → 2 decimaler
        annars  → 3 decimaler
        """
        abs_value = abs(value)

        if abs_value >= 100:
            formatted = f"{value:.1f}"
        elif abs_value >= 10:
            formatted = f"{value:.2f}"
        else:
            formatted = f"{value:.3f}"

        return formatted.rstrip("0").rstrip(".") + suffix

    # Billions
    if number >= 1_000_000_000:
        value = number / 1_000_000_000
        return format_large(value, "b")

    # Millions
    if number >= 1_000_000:
        value = number / 1_000_000
        return format_large(value, "m")

    # Under 100k → visa heltal
    if number < 100_000:
        return f"{number:,}".replace(",", " ")

    # 100k – 999k
    return f"{number // 1_000}k"

def format_time(seconds: int) -> str:
    seconds = max(0, int(seconds))

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    # Under 1 minute
    if hours == 0 and minutes == 0:
        return f"{secs}s"

    # Hours + minutes
    if hours > 0:
        if minutes > 0:
            return f"{hours}h {minutes}m"
        return f"{hours}h"

    # Minutes only
    return f"{minutes}m"

def is_prestige_eligible(player):
    from game.locations import LOCATIONS, get_location_index
    from game.utils import prestige_xp_required

    current_index = get_location_index(player["location"])
    if current_index != len(LOCATIONS) - 1:
        return False

    required = prestige_xp_required(player["prestige_level"])
    return player["total_xp"] >= required


def to_roman(n: int) -> str:
    if n <= 0:
        return "N/A"

    romans = [
        (10, "X"),
        (9, "IX"),
        (5, "V"),
        (4, "IV"),
        (1, "I"),
    ]

    result = ""
    for value, numeral in romans:
        while n >= value:
            result += numeral
            n -= value

    return result