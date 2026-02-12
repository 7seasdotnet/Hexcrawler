from hexcrawler.content import load_content
from hexcrawler.sim import Simulation


def run_once(seed: int):
    content = load_content("data/content.json")
    sim = Simulation(seed=seed, content=content)
    sim.init_world()
    p1 = sim.spawn_entity("scout", (0, 0))
    p2 = sim.spawn_entity("raider", (1, 1))
    sim.place_spawner((2, 2), "wilds_basic", interval_ticks=10)
    for _ in range(5):
        sim.attack(p1, p2, arc="front")
        sim.tick(12)
    sim.create_world_event("raid", (0, 0), p1, (3, 3), ["tracks"])
    sim.tick(80)
    return sim.world.snapshot()


def test_seeded_determinism():
    assert run_once(99) == run_once(99)


def test_different_seed_diverges():
    assert run_once(99) != run_once(100)
