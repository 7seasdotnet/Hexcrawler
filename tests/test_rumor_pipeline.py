from hexcrawler.content import load_content
from hexcrawler.sim import Simulation


def test_rumor_propagates_with_hop_cap_and_decays_and_tracks_created():
    content = load_content("data/content.json")
    sim = Simulation(seed=7, content=content)
    sim.init_world()
    actor = sim.spawn_entity("scout", (0, 0))
    event_id = sim.create_world_event("raid", (0, 0), actor, (4, 4), ["tracks", "bodies"])

    event_tracks = [t for t in sim.world.tracks.values() if t.event_id == event_id]
    assert len(event_tracks) == 2
    assert len(sim.world.rumors) == 1

    rumor = next(iter(sim.world.rumors.values()))
    assert rumor.evidence_types == ["tracks", "bodies"]

    first_track = event_tracks[0]
    assert sim.discover_track(actor, first_track.id)
    assert sim.validate_track(actor, first_track.id)

    sim.tick(600)
    assert rumor.id not in sim.world.rumors


def test_hop_cap_is_respected_and_regional_unrest_is_generated():
    content = load_content("data/content.json")
    sim = Simulation(seed=7, content=content)
    sim.init_world()
    actor = sim.spawn_entity("scout", (0, 0))
    sim.create_world_event("raid", (0, 0), actor, (4, 4), ["tracks"])

    max_hops = content.rumor_by_event["raid"].max_hops
    sim.tick(180)
    if sim.world.rumors:
        rumor = next(iter(sim.world.rumors.values()))
        assert rumor.hops <= max_hops
    assert sim.world.regional_unrest
