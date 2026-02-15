# HB-bot

HB-bot is a Discord-based economy game where players produce moonshine, manage operational risk, scale locations, and prestige for long-term progression.

The game emphasizes:
- Risk vs reward
- Heat management
- Scaling production
- Competitive XP progression

---

## Core Systems

### Brewing

- 5 sugar + 1 yeast = 1 liter
- Brew time = 1 second per liter
- Prestige reduces brew time by 5% per level
- `/brew all` fills remaining storage automatically
- Storage caps are enforced per location

---

### Mold

- Each batch has a base mold risk
- Mold protection reduces failure chance
- If mold occurs:
  - Partial refund based on remaining time
  - Minimum refund 15%
  - +5% minimum refund per mold tier

---

### Market & Heat

- Market refreshes every hour
- 3 buyers per location
- Buyers vary in:
  - Volume range
  - Price per liter
  - Base raid risk (varies hourly)

- Selling increases Heat
- Higher Heat increases raid probability
- Heat resets every hour and on prestige

---

### Raids

- Raid chance scales with:
  - Buyer base risk
  - Current heat level
  - Player XP scaling

- Raid protection reduces money lost (not raid chance)
- XP gained is based on actual money received after raid

---

### Prestige

- Requires final location + required XP
- Resets:
  - Inventory
  - Cash (to €500)
  - Protection
  - Heat
- Grants +5% permanent brewing speed per level
- XP requirement increases 5% per prestige level

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
```

Run the bot:

```bash
python hb.py
```

---

## Architecture

```
commands/   Slash commands
db/         Database & queries
game/       Core game logic
hb.py       Entry point
requirements.txt  
```

---

## Notes

- Database file (`*.sqlite`) is auto-generated on first run.  
- `.env`, `.venv`, and database files are excluded from version control.  
- Global slash commands may take up to 1 hour to propagate after first deploy.  
- The economy is global across all servers by default (shared player progression).
- Heat resets every hour and on prestige.  
- Protection reduces financial loss, not raid probability.  

---

## Future Improvements

- Dynamic price-risk correlation  
- Event-based modifiers  
- Server-scoped economy mode (optional multi-guild isolation)  
- UI polish for market and sell feedback  
- Anti-spam safeguards on high-frequency commands  
- Expanded buyer identities and visual assets  
- Seasonal prestige ladder or leaderboard reset mode  
