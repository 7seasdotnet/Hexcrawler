from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Hex = tuple[int, int]


@dataclass
class WoundInstance:
    body_part: str
    wound_type: str
    severity: str
    mobility_delta: int
    dexterity_delta: int
    recover_at_tick: int
    treated: bool = False


@dataclass
class EntityState:
    id: str
    template_id: str
    faction_id: str
    hex: Hex
    mobility: int
    dexterity: int
    armor_id: str | None
    weapon_id: str | None
    wounds: list[WoundInstance] = field(default_factory=list)
    fatigue: int = 0
    stagger: int = 0


@dataclass
class TrackObject:
    id: str
    event_id: str
    hex: Hex
    evidence_type: str
    created_tick: int
    discovered_by: set[str] = field(default_factory=set)
    validated_by: set[str] = field(default_factory=set)


@dataclass
class RumorInstance:
    id: str
    template_id: str
    event_id: str
    text: str
    confidence: float
    ttl_ticks: int
    evidence_types: list[str]
    hops: int = 0
    source_hex: Hex = (0, 0)
    known_by: set[str] = field(default_factory=set)


@dataclass
class WorldEvent:
    id: str
    event_type: str
    source_hex: Hex
    actor_entity_id: str
    target_hex: Hex
    evidence_types: list[str]
    tick: int


@dataclass
class Site:
    id: str
    kind: Literal["dungeon", "town", "ruin"]
    hex: Hex


@dataclass
class PatrolRoute:
    id: str
    points: list[Hex]


@dataclass
class Spawner:
    id: str
    hex: Hex
    encounter_table_id: str
    interval_ticks: int
    next_spawn_tick: int


@dataclass
class WorldState:
    tick: int = 0
    width: int = 12
    height: int = 12
    terrain: dict[Hex, str] = field(default_factory=dict)
    entities: dict[str, EntityState] = field(default_factory=dict)
    tracks: dict[str, TrackObject] = field(default_factory=dict)
    rumors: dict[str, RumorInstance] = field(default_factory=dict)
    events: dict[str, WorldEvent] = field(default_factory=dict)
    sites: dict[str, Site] = field(default_factory=dict)
    patrol_routes: dict[str, PatrolRoute] = field(default_factory=dict)
    spawners: dict[str, Spawner] = field(default_factory=dict)
    regional_unrest: dict[str, int] = field(default_factory=dict)

    def snapshot(self) -> dict:
        def e_repr(ent: EntityState) -> tuple:
            wounds = tuple(
                sorted(
                    (w.body_part, w.wound_type, w.severity, w.mobility_delta, w.dexterity_delta, w.recover_at_tick, w.treated)
                    for w in ent.wounds
                )
            )
            return (ent.id, ent.template_id, ent.hex, ent.mobility, ent.dexterity, ent.fatigue, ent.stagger, wounds)

        return {
            "tick": self.tick,
            "terrain": tuple(sorted(self.terrain.items())),
            "entities": tuple(sorted(e_repr(e) for e in self.entities.values())),
            "tracks": tuple(
                sorted((t.id, t.event_id, t.hex, t.evidence_type, tuple(sorted(t.discovered_by)), tuple(sorted(t.validated_by))) for t in self.tracks.values())
            ),
            "rumors": tuple(
                sorted(
                    (r.id, r.template_id, r.event_id, r.confidence, r.ttl_ticks, r.hops, tuple(r.evidence_types), tuple(sorted(r.known_by)))
                    for r in self.rumors.values()
                )
            ),
            "events": tuple(sorted((e.id, e.event_type, e.source_hex, e.tick) for e in self.events.values())),
            "sites": tuple(sorted((s.id, s.kind, s.hex) for s in self.sites.values())),
            "patrol_routes": tuple(sorted((p.id, tuple(p.points)) for p in self.patrol_routes.values())),
            "regional_unrest": tuple(sorted(self.regional_unrest.items())),
        }
