# Hexcrawler MVP Architecture Note

## Module boundaries
- `hexcrawler.sim`: deterministic simulation core (tick loop, RNG, events, rumors, tracks, wounds, armor, persistence).
- `hexcrawler.content`: typed schema/dataclasses and JSON loader with validation.
- `hexcrawler.web`: minimal in-game editor/play UI and command APIs.
- `data/content.json`: content data for rules and world templates.

## Multiplayer-safe implications
- Simulation state changes only through `Simulation` commands; UI is a thin command client.
- Tick progression is explicit and deterministic; no render-frame coupling.
- RNG is isolated in simulation core and seeded, enabling deterministic replays and future server authority.
- APIs are command-style and map cleanly to future remote transport without changing simulation logic.
