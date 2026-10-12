"""Single-document compare-and-swap: XP and the receipt commit together."""
import asyncio
import copy
import json
import sqlite3
from pathlib import Path

class Conflict(Exception):
    pass

class Store:
    async def mutate(self, key, change):
        for _ in range(12):
            old = await self.get(key)
            if old is None:
                raise KeyError(key)
            new = copy.deepcopy(old)
            result = change(new)  # Pure callback; may run again after a CAS race.
            new["revision"] = old["revision"] + 1
            if await self.cas(key, old["revision"], new):
                return result
        raise Conflict("Another request changed this player. Please retry.")

class MongoStore(Store):
    def __init__(self, uri, database):
        from pymongo import AsyncMongoClient
        from pymongo.write_concern import WriteConcern
        self.client = AsyncMongoClient(uri, serverSelectionTimeoutMS=8000)
        self.collection = self.client[database].get_collection("players", write_concern=WriteConcern("majority"))
    async def initialize(self):
        await self.client.admin.command("ping")
    async def create(self, doc):
        await self.collection.insert_one(doc)
    async def get(self, key):
        return await self.collection.find_one({"_id": key})
    async def cas(self, key, revision, doc):
        result = await self.collection.replace_one({"_id": key, "revision": revision}, doc)
        return result.modified_count == 1
    async def delete(self, key):
        await self.collection.delete_one({"_id": key})
    async def close(self):
        await self.client.close()

class SQLiteStore(Store):
    """Optional entirely local profile; never presented as an Atlas connection."""
    def __init__(self, path):
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
    def _connect(self):
        return sqlite3.connect(self.path, timeout=10)
    async def initialize(self):
        def work():
            with self._connect() as db:
                db.execute("CREATE TABLE IF NOT EXISTS players (id TEXT PRIMARY KEY, revision INTEGER NOT NULL, doc TEXT NOT NULL)")
        await asyncio.to_thread(work)
    async def create(self, doc):
        def work():
            with self._connect() as db:
                db.execute("INSERT INTO players VALUES (?, ?, ?)", (doc["_id"], doc["revision"], json.dumps(doc)))
        await asyncio.to_thread(work)
    async def get(self, key):
        def work():
            with self._connect() as db:
                row = db.execute("SELECT doc FROM players WHERE id=?", (key,)).fetchone()
                return json.loads(row[0]) if row else None
        return await asyncio.to_thread(work)
    async def cas(self, key, revision, doc):
        def work():
            with self._connect() as db:
                return db.execute("UPDATE players SET revision=?, doc=? WHERE id=? AND revision=?", (doc["revision"], json.dumps(doc), key, revision)).rowcount == 1
        return await asyncio.to_thread(work)
    async def delete(self, key):
        def work():
            with self._connect() as db:
                db.execute("DELETE FROM players WHERE id=?", (key,))
        await asyncio.to_thread(work)
    async def close(self):
        pass

