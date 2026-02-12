from hexcrawler.content import load_content
from hexcrawler.sim import Simulation


def test_non_penetration_causes_secondary_effects():
    content = load_content("data/content.json")
    sim = Simulation(seed=1, content=content)
    sim.init_world()
    a = sim.spawn_entity("scout", (0, 0))
    d = sim.spawn_entity("raider", (0, 1))
    sim.world.entities[a].weapon_id = "club"  # low penetration vs mail front
    result = sim.attack(a, d, arc="front")
    assert not result["penetrated"]
    assert sim.world.entities[d].stagger >= 1
    assert sim.world.entities[d].fatigue >= 1


def test_penetration_applies_wound_and_treatment_recovery():
    content = load_content("data/content.json")
    sim = Simulation(seed=3, content=content)
    sim.init_world()
    a = sim.spawn_entity("raider", (0, 0))
    d = sim.spawn_entity("scout", (0, 1))
    before_mobility = sim.world.entities[d].mobility
    result = sim.attack(a, d, arc="rear")
    assert result["penetrated"]
    assert len(sim.world.entities[d].wounds) >= 1
    assert sim.world.entities[d].mobility < before_mobility
    assert sim.treat_wound(d)
    sim.tick(80)
    assert sim.world.entities[d].mobility == before_mobility
