from hexcrawler.content import load_content
from hexcrawler.sim import Simulation


def test_world_persists_without_player_entity():
    content = load_content("data/content.json")
    sim = Simulation(seed=55, content=content)
    sim.init_world()
    player = sim.spawn_entity("scout", (0, 0))
    sim.place_spawner((2, 2), "wilds_basic", interval_ticks=5)

    sim.remove_entity(player)
    sim.tick(20)

    assert sim.world.tick == 20
    assert len(sim.world.entities) > 0
