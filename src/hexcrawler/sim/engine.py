from __future__ import annotations

import random
from dataclasses import dataclass

from hexcrawler.content.loader import ContentIndex

from .models import EntityState, PatrolRoute, RumorInstance, Site, Spawner, TrackObject, WorldEvent, WorldState, WoundInstance


@dataclass
class SimConfig:
    tick_ms: int = 100
    encounter_interval_ticks: int = 20
    supply_interval_ticks: int = 30
    fatigue_interval_ticks: int = 25
    ai_interval_ticks: int = 15
    rumor_decay_interval_ticks: int = 10


class Simulation:
    def __init__(self, seed: int, content: ContentIndex, config: SimConfig | None = None):
        self.rng = random.Random(seed)
        self.content = content
        self.config = config or SimConfig()
        self.world = WorldState()
        self._next_id = 1

    def _id(self, prefix: str) -> str:
        out = f"{prefix}_{self._next_id}"
        self._next_id += 1
        return out

    def init_world(self, width: int = 12, height: int = 12, terrain_id: str = "plains") -> None:
        self.world.width = width
        self.world.height = height
        self.world.terrain = {(q, r): terrain_id for q in range(width) for r in range(height)}

    def spawn_entity(self, template_id: str, at_hex: tuple[int, int]) -> str:
        t = self.content.entities[template_id]
        ent_id = self._id("ent")
        self.world.entities[ent_id] = EntityState(
            id=ent_id,
            template_id=t.id,
            faction_id=t.faction_id,
            hex=at_hex,
            mobility=t.mobility,
            dexterity=t.dexterity,
            armor_id=t.armor_id,
            weapon_id=t.weapon_id,
        )
        return ent_id

    def remove_entity(self, entity_id: str) -> None:
        self.world.entities.pop(entity_id, None)

    def place_site(self, kind: str, at_hex: tuple[int, int]) -> str:
        site_id = self._id("site")
        self.world.sites[site_id] = Site(id=site_id, kind=kind, hex=at_hex)
        return site_id

    def add_patrol_route(self, points: list[tuple[int, int]]) -> str:
        rid = self._id("patrol")
        self.world.patrol_routes[rid] = PatrolRoute(id=rid, points=list(points))
        return rid

    def place_spawner(self, at_hex: tuple[int, int], encounter_table_id: str, interval_ticks: int = 50) -> str:
        sid = self._id("spawn")
        self.world.spawners[sid] = Spawner(
            id=sid,
            hex=at_hex,
            encounter_table_id=encounter_table_id,
            interval_ticks=interval_ticks,
            next_spawn_tick=self.world.tick + interval_ticks,
        )
        return sid

    def paint_terrain(self, at_hex: tuple[int, int], terrain_id: str) -> None:
        self.world.terrain[at_hex] = terrain_id

    def create_world_event(self, event_type: str, source_hex: tuple[int, int], actor_entity_id: str, target_hex: tuple[int, int], evidence_types: list[str]) -> str:
        eid = self._id("event")
        event = WorldEvent(
            id=eid,
            event_type=event_type,
            source_hex=source_hex,
            actor_entity_id=actor_entity_id,
            target_hex=target_hex,
            evidence_types=evidence_types,
            tick=self.world.tick,
        )
        self.world.events[eid] = event
        self._place_tracks(event)
        self._create_rumor(event)
        return eid

    def discover_track(self, entity_id: str, track_id: str) -> bool:
        if entity_id not in self.world.entities or track_id not in self.world.tracks:
            return False
        self.world.tracks[track_id].discovered_by.add(entity_id)
        return True

    def validate_track(self, entity_id: str, track_id: str) -> bool:
        track = self.world.tracks.get(track_id)
        if not track or entity_id not in track.discovered_by:
            return False
        track.validated_by.add(entity_id)
        return True

    def _place_tracks(self, event: WorldEvent) -> None:
        for evidence in event.evidence_types:
            tid = self._id("track")
            self.world.tracks[tid] = TrackObject(
                id=tid,
                event_id=event.id,
                hex=event.target_hex,
                evidence_type=evidence,
                created_tick=self.world.tick,
            )

    def _create_rumor(self, event: WorldEvent) -> None:
        template = self.content.rumor_by_event.get(event.event_type)
        if not template:
            return
        rid = self._id("rumor")
        self.world.rumors[rid] = RumorInstance(
            id=rid,
            template_id=template.id,
            event_id=event.id,
            text=template.text_pattern.format(event_type=event.event_type, x=event.target_hex[0], y=event.target_hex[1]),
            confidence=template.base_confidence,
            ttl_ticks=template.ttl_ticks,
            evidence_types=list(event.evidence_types),
            source_hex=event.source_hex,
            known_by={event.actor_entity_id},
        )

    def update_rumor_template(self, template_id: str, ttl_ticks: int, max_hops: int) -> None:
        template = self.content.rumor_templates[template_id]
        template.ttl_ticks = ttl_ticks
        template.max_hops = max_hops

    def update_weapon(self, weapon_id: str, penetration: int) -> None:
        self.content.weapons[weapon_id].penetration = penetration

    def update_armor_threshold(self, armor_id: str, damage_type: str, arc: str, value: int) -> None:
        setattr(self.content.armors[armor_id].thresholds[damage_type], arc, value)

    def update_wound_type(self, wound_type_id: str, mobility_delta: int, dexterity_delta: int) -> None:
        wt = self.content.wound_types[wound_type_id]
        wt.mobility_delta = mobility_delta
        wt.dexterity_delta = dexterity_delta

    def update_faction_settlement(self, faction_id: str, settlement: str) -> None:
        faction = self.content.factions[faction_id]
        if settlement not in faction.settlements:
            faction.settlements.append(settlement)

    def attack(self, attacker_id: str, defender_id: str, arc: str = "front") -> dict:
        attacker = self.world.entities[attacker_id]
        defender = self.world.entities[defender_id]
        weapon = self.content.weapons[attacker.weapon_id]
        armor_threshold = 0
        if defender.armor_id:
            armor = self.content.armors[defender.armor_id]
            armor_threshold = armor.thresholds[weapon.damage_type].__dict__[arc]
        penetration_value = weapon.penetration + self.rng.randint(-1, 1)
        penetrated = penetration_value >= armor_threshold
        result = {"penetrated": penetrated, "penetration_value": penetration_value, "threshold": armor_threshold}
        if penetrated:
            self._apply_wound(defender, weapon)
        else:
            defender.stagger += max(1, weapon.shock)
            defender.fatigue += 1
        return result

    def _apply_wound(self, defender: EntityState, weapon) -> None:
        template = self.content.entities[defender.template_id]
        draw = self.rng.random()
        cumulative = 0.0
        body_part = template.body_parts[0].id
        for bp in template.body_parts:
            cumulative += bp.coverage
            if draw <= cumulative:
                body_part = bp.id
                break
        wound_type = self.content.wound_types["slash" if weapon.damage_type == "cut" else "blunt"]
        severity = self.content.wound_severities[weapon.base_severity]
        wi = WoundInstance(
            body_part=body_part,
            wound_type=wound_type.id,
            severity=severity.id,
            mobility_delta=wound_type.mobility_delta,
            dexterity_delta=wound_type.dexterity_delta,
            recover_at_tick=self.world.tick + severity.recovery_ticks,
        )
        defender.wounds.append(wi)
        defender.mobility += wound_type.mobility_delta
        defender.dexterity += wound_type.dexterity_delta

    def treat_wound(self, entity_id: str) -> bool:
        entity = self.world.entities[entity_id]
        untreated = [w for w in entity.wounds if not w.treated]
        if not untreated:
            return False
        wound = untreated[0]
        wound.treated = True
        wound.recover_at_tick = max(self.world.tick + 10, wound.recover_at_tick // 2)
        return True

    def _tick_rumors(self) -> None:
        to_delete = []
        for rumor in self.world.rumors.values():
            rumor.ttl_ticks -= 1
            if rumor.ttl_ticks <= 0:
                to_delete.append(rumor.id)
                continue
            template = self.content.rumor_templates[rumor.template_id]
            if rumor.hops < template.max_hops and self.world.tick % self.config.ai_interval_ticks == 0:
                rumor.hops += 1
                rumor.confidence = max(0.1, rumor.confidence - 0.1)
                rumor.known_by.add(f"hop_{rumor.hops}")
            if rumor.hops >= template.max_hops:
                region_key = f"{rumor.source_hex[0]//4},{rumor.source_hex[1]//4}"
                self.world.regional_unrest[region_key] = self.world.regional_unrest.get(region_key, 0) + 1
        for rid in to_delete:
            del self.world.rumors[rid]

    def _tick_recovery(self) -> None:
        for e in self.world.entities.values():
            remaining = []
            for w in e.wounds:
                if self.world.tick >= w.recover_at_tick:
                    e.mobility -= w.mobility_delta
                    e.dexterity -= w.dexterity_delta
                else:
                    remaining.append(w)
            e.wounds = remaining

    def _tick_spawners(self) -> None:
        for sp in self.world.spawners.values():
            if self.world.tick >= sp.next_spawn_tick:
                table = self.content.encounter_tables[sp.encounter_table_id]
                roll = self.rng.randint(1, sum(e.weight for e in table.entries))
                accum = 0
                pick = table.entries[0].entity_template_id
                for entry in table.entries:
                    accum += entry.weight
                    if roll <= accum:
                        pick = entry.entity_template_id
                        break
                self.spawn_entity(pick, sp.hex)
                sp.next_spawn_tick = self.world.tick + sp.interval_ticks

    def tick(self, steps: int = 1) -> None:
        for _ in range(steps):
            self.world.tick += 1
            self._tick_spawners()
            if self.world.tick % self.config.rumor_decay_interval_ticks == 0:
                self._tick_rumors()
            if self.world.tick % self.config.fatigue_interval_ticks == 0:
                for e in self.world.entities.values():
                    e.fatigue += 1
            self._tick_recovery()

    def simulate_days(self, days: int) -> None:
        self.tick(days * 24 * 60 * 6)
