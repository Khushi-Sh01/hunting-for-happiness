"""Loopback-only DOM test server. StubGemma is not a real game/demo runtime."""
import os
import tempfile
from pathlib import Path
import uvicorn
from backend.main import create_app
from backend.store import SQLiteStore
from .test_app import StubGemma

if __name__ == "__main__":
    os.environ["STORAGE_MODE"] = "sqlite"
    os.environ["ENABLE_VOICE"] = "false"
    os.environ["STORE_REFLECTIONS"] = "false"
    with tempfile.TemporaryDirectory(prefix="hfh-ui-test-") as directory:
        uvicorn.run(create_app(SQLiteStore(Path(directory)/"test.sqlite3"), StubGemma()),
                    host="127.0.0.1", port=8765, access_log=False)
