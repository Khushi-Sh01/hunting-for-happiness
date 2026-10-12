"""Opt-in real Atlas test. Creates/deletes only one random document in a dedicated DB."""
import asyncio
import os
import uuid
import pytest
from backend.store import MongoStore

@pytest.mark.skipif(not os.getenv("TEST_MONGODB_URI"), reason="No TEST_MONGODB_URI supplied")
def test_atlas_cas_and_concurrency():
    async def run():
        store = MongoStore(os.environ["TEST_MONGODB_URI"], "hfh_integration_tests")
        key = "test-" + str(uuid.uuid4())
        await store.initialize()
        await store.create({"_id":key,"revision":0,"xp":0,"completed":[]})
        try:
            def award(doc):
                if not doc["completed"]:
                    doc["xp"] += 45
                    doc["completed"].append("same-quest")
                return doc["xp"]
            assert await asyncio.gather(store.mutate(key,award),store.mutate(key,award)) == [45,45]
            assert (await store.get(key))["xp"] == 45
        finally:
            await store.delete(key)
            await store.close()
    asyncio.run(run())
