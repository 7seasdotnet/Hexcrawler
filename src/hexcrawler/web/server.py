from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

from hexcrawler.content import load_content
from hexcrawler.sim import Simulation

ROOT = Path(__file__).resolve().parent
CONTENT = load_content(Path(__file__).resolve().parents[3] / "data" / "content.json")
SIM = Simulation(seed=42, content=CONTENT)
SIM.init_world()
PLAYER_ID = SIM.spawn_entity("scout", (0, 0))


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, payload: bytes, ctype: str = "text/html") -> None:
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _json(self, obj: dict) -> None:
        self._send(200, json.dumps(obj).encode(), "application/json")

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/":
            return self._send(200, (ROOT / "templates" / "editor.html").read_bytes())
        if path == "/play":
            return self._send(200, (ROOT / "templates" / "play.html").read_bytes())
        if path == "/static/editor.js":
            return self._send(200, (ROOT / "static" / "editor.js").read_bytes(), "application/javascript")
        if path == "/api/world":
            return self._json(
                {
                    "tick": SIM.world.tick,
                    "terrain": [{"q": q, "r": r, "t": t} for (q, r), t in SIM.world.terrain.items()],
                    "sites": [{"id": s.id, "kind": s.kind, "q": s.hex[0], "r": s.hex[1]} for s in SIM.world.sites.values()],
                    "spawners": [{"id": s.id, "q": s.hex[0], "r": s.hex[1], "table": s.encounter_table_id} for s in SIM.world.spawners.values()],
                    "routes": [{"id": p.id, "points": p.points} for p in SIM.world.patrol_routes.values()],
                    "rumors": [r.text for r in SIM.world.rumors.values()],
                    "tracks": [{"id": t.id, "q": t.hex[0], "r": t.hex[1], "e": t.evidence_type} for t in SIM.world.tracks.values()],
                    "regional_unrest": SIM.world.regional_unrest,
                }
            )
        self._send(404, b"not found", "text/plain")

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length", "0"))
        data = json.loads(self.rfile.read(length) or b"{}")

        if path == "/api/paint":
            SIM.paint_terrain((data["q"], data["r"]), data["terrain"])
            return self._json({"ok": True})
        if path == "/api/site":
            sid = SIM.place_site(data.get("kind", "dungeon"), (data["q"], data["r"]))
            return self._json({"ok": True, "id": sid})
        if path == "/api/spawner":
            sid = SIM.place_spawner((data["q"], data["r"]), data.get("table", "wilds_basic"), 20)
            return self._json({"ok": True, "id": sid})
        if path == "/api/route":
            rid = SIM.add_patrol_route([(data["q1"], data["r1"]), (data["q2"], data["r2"])])
            return self._json({"ok": True, "id": rid})
        if path == "/api/encounter":
            CONTENT.encounter_tables[data["id"]].entries[0].weight = int(data["first_weight"])
            return self._json({"ok": True})
        if path == "/api/rumor-template":
            SIM.update_rumor_template(data["id"], int(data["ttl_ticks"]), int(data["max_hops"]))
            return self._json({"ok": True})
        if path == "/api/weapon":
            SIM.update_weapon(data["id"], int(data["penetration"]))
            return self._json({"ok": True})
        if path == "/api/armor":
            SIM.update_armor_threshold(data["armor_id"], data["damage_type"], data["arc"], int(data["value"]))
            return self._json({"ok": True})
        if path == "/api/wound":
            SIM.update_wound_type(data["id"], int(data["mobility_delta"]), int(data["dexterity_delta"]))
            return self._json({"ok": True})
        if path == "/api/faction":
            SIM.update_faction_settlement(data["id"], data["settlement"])
            return self._json({"ok": True})
        if path == "/api/simulate":
            SIM.simulate_days(int(data.get("days", 1)))
            return self._json({"ok": True, "tick": SIM.world.tick})
        if path == "/api/play":
            SIM.tick(6)
            event_id = SIM.create_world_event("raid", (1, 1), PLAYER_ID, (2, 2), ["tracks", "bodies"])
            first_track_id = next(iter(SIM.world.tracks))
            SIM.discover_track(PLAYER_ID, first_track_id)
            SIM.validate_track(PLAYER_ID, first_track_id)
            return self._json({"ok": True, "event_id": event_id})

        self._send(404, b"not found", "text/plain")


def main() -> None:
    HTTPServer(("0.0.0.0", 8000), Handler).serve_forever()


if __name__ == "__main__":
    main()
