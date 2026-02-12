from __future__ import annotations

import json
from pathlib import Path

from .schemas import (
    ArmorArcDef,
    ArmorDef,
    BodyPartDef,
    ContentBundle,
    EncounterEntry,
    EncounterTableDef,
    EntityTemplate,
    FactionDef,
    RumorTemplateDef,
    TerrainDef,
    WeaponDef,
    WoundSeverityDef,
    WoundTypeDef,
)


def _require(cond: bool, message: str) -> None:
    if not cond:
        raise ValueError(message)


class ContentIndex:
    def __init__(self, bundle: ContentBundle):
        self.bundle = bundle
        self.terrain = {t.id: t for t in bundle.terrains}
        self.factions = {f.id: f for f in bundle.factions}
        self.entities = {e.id: e for e in bundle.entities}
        self.weapons = {w.id: w for w in bundle.weapons}
        self.armors = {a.id: a for a in bundle.armors}
        self.wound_types = {w.id: w for w in bundle.wound_types}
        self.wound_severities = {s.id: s for s in bundle.wound_severities}
        self.encounter_tables = {e.id: e for e in bundle.encounter_tables}
        self.rumor_templates = {r.id: r for r in bundle.rumor_templates}
        self.rumor_by_event = {r.event_type: r for r in bundle.rumor_templates}


def load_content(path: str | Path) -> ContentIndex:
    data = json.loads(Path(path).read_text())

    terrains = [TerrainDef(**t) for t in data["terrains"]]
    factions = [FactionDef(**f) for f in data["factions"]]
    entities = [
        EntityTemplate(
            id=e["id"],
            faction_id=e["faction_id"],
            body_parts=[BodyPartDef(**bp) for bp in e["body_parts"]],
            mobility=e["mobility"],
            dexterity=e["dexterity"],
            armor_id=e.get("armor_id"),
            weapon_id=e.get("weapon_id"),
        )
        for e in data["entities"]
    ]
    weapons = [WeaponDef(**w) for w in data["weapons"]]
    armors = [ArmorDef(id=a["id"], thresholds={k: ArmorArcDef(**v) for k, v in a["thresholds"].items()}, fatigue_on_block=a["fatigue_on_block"], noise=a["noise"]) for a in data["armors"]]
    wound_types = [WoundTypeDef(**w) for w in data["wound_types"]]
    wound_severities = [WoundSeverityDef(**w) for w in data["wound_severities"]]
    encounter_tables = [EncounterTableDef(id=e["id"], entries=[EncounterEntry(**x) for x in e["entries"]]) for e in data["encounter_tables"]]
    rumor_templates = [RumorTemplateDef(**r) for r in data["rumor_templates"]]

    _require(all(0 < sum(bp.coverage for bp in e.body_parts) <= 1.01 for e in entities), "Entity body part coverage must sum to ~1")
    _require(all(1 <= r.max_hops <= 5 for r in rumor_templates), "Rumor max_hops must be 1..5")

    bundle = ContentBundle(
        terrains=terrains,
        factions=factions,
        entities=entities,
        weapons=weapons,
        armors=armors,
        wound_types=wound_types,
        wound_severities=wound_severities,
        encounter_tables=encounter_tables,
        rumor_templates=rumor_templates,
    )
    return ContentIndex(bundle)
