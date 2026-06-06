from app.memory.memory_store import InMemoryStore, MemoryContext


def test_memory_upsert_get_reset():
    store = InMemoryStore()
    context = MemoryContext(
        session_id="s1",
        user_id="u1",
        home_id="h1",
        last_intent="DEVICE_HISTORY",
        last_device_slug="den_bep",
    )
    store.upsert(context)

    loaded = store.get("s1", "u1")
    assert loaded is not None
    assert loaded.last_device_slug == "den_bep"

    store.reset("s1", "u1")
    assert store.get("s1", "u1") is None

