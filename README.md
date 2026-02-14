# HB

HB is a Discord economy game where players produce moonshine, manage risk, upgrade locations, and prestige for long-term scaling bonuses.

The game focuses on progression, risk management, and competitive global rankings.

---

## Features

- Location-based production scaling  
- Storage limits per location  
- Mold mechanic (early-game pressure)  
- Raid mechanic (late-game pressure)  
- Protection system (max tier 3)  
- Prestige system with scaling XP requirements  
- Global leaderboard  
- Background batch resolution  
- Automatic number formatting (k / m / b)  

---

## Game Mechanics

### Brewing

- 1 yeast : 5 sugar ratio  
- Brew time = liters (seconds)  
- Prestige reduces brew time by 5% per level  
- Hard storage cap enforced  
- Overflow is lost and reported  

### Mold

- Can destroy a batch  
- Minimum 15% refund  
- Mold protection reduces chance and increases refund  

### Raids

- Triggered on sell  
- Risk scales with prestige  
- Raid protection reduces risk  

### Prestige

- Resets progression to Shed  
- Resets cash to €500  
- Increases brewing speed  
- Increases XP requirement by 5% per level  
- Total XP is preserved  

---

## Setup

Create virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
DISCORD_TOKEN=your_token_here
GUILD_ID=your_server_id_here
```

Run the bot:

```bash
python hb.py
```

---

## Project Structure

```
commands/       Slash commands  
db/             Database + queries  
game/           Core mechanics  
hb.py           Entry point  
requirements.txt  
```

---

## Notes

- Database file (`*.sqlite`) is auto-generated on first run.  
- `.env`, `.venv`, and database files are excluded from version control.  
- Guild commands are registered at startup.  

---

## Future Improvements

- Paginated leaderboard  
- Multi-guild support  
- Economy balancing tuning  
- Web dashboard  
- Seasonal resets  

