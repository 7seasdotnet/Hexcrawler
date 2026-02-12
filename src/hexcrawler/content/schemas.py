from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TerrainDef:
    id: str
    move_cost: int
    track_visibility_mod: float


@dataclass
class BodyPartDef:
    id: str
    coverage: float


@dataclass
class WoundTypeDef:
    id: str
    mobility_delta: int
    dexterity_delta: int
    bleed: int


@dataclass
class WoundSeverityDef:
    id: str
    recovery_ticks: int


@dataclass
class ArmorArcDef:
    front: int
    side: int
    rear: int


@dataclass
class ArmorDef:
    id: str
    thresholds: dict[str, ArmorArcDef]
    fatigue_on_block: int
    noise: int


@dataclass
class WeaponDef:
    id: str
    penetration: int
    damage_type: str
    shock: int
    base_severity: str


@dataclass
class EntityTemplate:
    id: str
    faction_id: str
    body_parts: list[BodyPartDef]
    mobility: int
    dexterity: int
    armor_id: str | None
    weapon_id: str | None


@dataclass
class FactionDef:
    id: str
    settlements: list[str]


@dataclass
class EncounterEntry:
    weight: int
    entity_template_id: str


@dataclass
class EncounterTableDef:
    id: str
    entries: list[EncounterEntry]


@dataclass
class RumorTemplateDef:
    id: str
    event_type: str
    base_confidence: float
    ttl_ticks: int
    max_hops: int
    text_pattern: str


@dataclass
class ContentBundle:
    terrains: list[TerrainDef]
    factions: list[FactionDef]
    entities: list[EntityTemplate]
    weapons: list[WeaponDef]
    armors: list[ArmorDef]
    wound_types: list[WoundTypeDef]
    wound_severities: list[WoundSeverityDef]
    encounter_tables: list[EncounterTableDef]
    rumor_templates: list[RumorTemplateDef]
