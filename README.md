# Hexcrawler MVP Vertical Slice

Deterministic, headless-testable hexcrawler simulation with an integrated in-game editor/play loop.

## What works
- Fixed-tick deterministic simulation (`tick_ms=100`) with seeded RNG and stable replay.
- Data-driven content loader for terrains, entities, factions, weapons, armor, wound tables, encounter tables, rumor templates.
- World event -> tracks + rumor pipeline, hop-capped propagation (3-5), TTL decay, regional unrest downgrade signal.
- Wound model with body part targeting, severity recovery, and treatment acceleration.
- Armor thresholds by arc with secondary effects when non-penetrating.
- Editor flow: paint terrain, place dungeon/town/ruin, place spawner, define patrol route, edit encounter/rumor/weapons/armor/wounds/factions, simulate days, then play.

## Run demo
```bash
PYTHONPATH=src python -m hexcrawler.web.server
```
Open `http://localhost:8000`.

## Run tests
```bash
PYTHONPATH=src pytest -q
```
