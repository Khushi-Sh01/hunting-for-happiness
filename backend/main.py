import asyncio
import hashlib
import io
import logging
import os
import secrets
import time
import uuid
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import Depends, FastAPI, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool
from dotenv import load_dotenv
from .domain import CATALOG, QuestRequest, ReflectionRequest, level_for, public_player, xp_for
from .gemma import Gemma, ModelUnavailable
from .store import Conflict, MongoStore, SQLiteStore

load_dotenv()
logging.basicConfig(level=logging.INFO)
bearer = HTTPBearer(auto_error=False)
MAX_COMPLETIONS = 500  # Bounded embedded history keeps the player document small.

def create_app(store=None, model=None):
    @asynccontextmanager
    async def lifespan(app):
        mode = os.getenv("STORAGE_MODE", "mongo")
        if store is not None:
            app.state.store = store
        elif mode == "sqlite":
            app.state.store = SQLiteStore(os.getenv("SQLITE_PATH", "data/happiness.sqlite3"))
        elif mode == "mongo" and os.getenv("MONGODB_URI"):
            app.state.store = MongoStore(os.environ["MONGODB_URI"], os.getenv("MONGODB_DB", "hunting_for_happiness"))
        else:
            raise RuntimeError("Set MONGODB_URI for Atlas, or STORAGE_MODE=sqlite for a local profile")
        app.state.model = model or Gemma(os.getenv("OLLAMA_URL", "http://127.0.0.1:11434"), os.getenv("GEMMA_MODEL", "gemma3:4b"))
        app.state.voice = None
        app.state.voice_lock = asyncio.Lock()
        await app.state.store.initialize()
        yield
        await app.state.model.close()
        await app.state.store.close()

    # No CDN-loaded interactive docs: keep the app's browser assets entirely same-origin.
    app = FastAPI(title="#HuntingForHappiness", lifespan=lifespan, docs_url=None, redoc_url=None)
    hits = defaultdict(deque)

    def limit(key, maximum=12):
        now = time.monotonic()
        queue = hits[key]
        while queue and queue[0] < now - 60:
            queue.popleft()
        if len(queue) >= maximum:
            raise HTTPException(429, "Take a breath; please retry in a minute.")
        queue.append(now)
        # Bounded per-process limiter for a hackathon deployment. Use shared gateway limiting at scale.
        if len(hits) > 5000:
            for item in list(hits):
                if not hits[item] or hits[item][-1] < now - 60:
                    del hits[item]

    async def player(auth: HTTPAuthorizationCredentials | None = Depends(bearer)):
        if not auth or len(auth.credentials) > 200:
            raise HTTPException(401, "Create or restore your local player session.")
        key = hashlib.sha256(auth.credentials.encode()).hexdigest()
        doc = await app.state.store.get(key)
        if not doc:
            raise HTTPException(401, "Player session not found.")
        return key, doc

    @app.middleware("http")
    async def headers(request: Request, call_next):
        if request.headers.get("content-length", "").isdigit() and int(request.headers["content-length"]) > 9_000_000:
            return JSONResponse(status_code=413, content={"detail": "Request too large"})
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; media-src 'self' blob:; object-src 'none'; frame-ancestors 'none'; base-uri 'self'"
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.exception_handler(ModelUnavailable)
    async def unavailable(request, exc):
        return JSONResponse(status_code=503, content={"detail": str(exc)})

    @app.exception_handler(Conflict)
    async def conflict(request, exc):
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.get("/healthz")
    async def health():
        return {"status": "alive"}

    @app.get("/readyz")
    async def ready():
        try:
            await app.state.store.initialize()
            await app.state.model.ready()
        except Exception:
            raise HTTPException(503, "Database or Gemma runtime is not ready")
        return {"status": "ready"}

    @app.get("/api/config")
    async def config():
        return {"storage": os.getenv("STORAGE_MODE", "mongo"), "model": os.getenv("GEMMA_MODEL", "gemma3:4b"), "voice": os.getenv("ENABLE_VOICE", "false").lower() == "true"}

    @app.post("/api/session", status_code=201)
    async def session(request: Request):
        limit("signup:" + (request.client.host if request.client else "unknown"), 20)
        token = secrets.token_urlsafe(32)
        key = hashlib.sha256(token.encode()).hexdigest()
        await app.state.store.create({"_id": key, "revision": 0, "xp": 0, "level": 1, "active": None, "completed": []})
        return {"token": token}

    @app.get("/api/me")
    async def me(identity=Depends(player)):
        return public_player(identity[1])

    @app.delete("/api/me", status_code=204)
    async def erase(identity=Depends(player)):
        await app.state.store.delete(identity[0])

    @app.post("/api/quests")
    async def generate(payload: QuestRequest, identity=Depends(player)):
        key, old = identity
        limit(key)
        if old["active"]:
            raise Conflict("Finish or abandon your current quest first.")
        if len(old["completed"]) >= MAX_COMPLETIONS:
            raise Conflict("This demo profile reached its 500-quest limit. Export your history before resetting.")
        choice = await app.state.model.choose(payload)
        if payload.mobility == "seated" and choice.mission_key == "mindful_walk":
            raise ModelUnavailable("Gemma selected an incompatible mission; please retry.")
        quest = {"id": str(uuid.uuid4()), "mission_key": choice.mission_key, **CATALOG[choice.mission_key],
                 "minutes": payload.minutes, "mood": payload.mood, "mobility": payload.mobility, "started_at": None}
        def change(doc):
            if doc["active"]:
                raise Conflict("A quest was already generated in another tab.")
            doc["active"] = quest
            return quest
        return await app.state.store.mutate(key, change)

    @app.post("/api/quests/{quest_id}/accept")
    async def accept(quest_id: str, identity=Depends(player)):
        def change(doc):
            quest = doc["active"]
            if not quest or quest["id"] != quest_id:
                raise HTTPException(404, "Quest not found")
            if quest["started_at"] is None:
                quest["started_at"] = time.time()
            return quest
        return await app.state.store.mutate(identity[0], change)

    @app.delete("/api/quests/{quest_id}", status_code=204)
    async def abandon(quest_id: str, identity=Depends(player)):
        def change(doc):
            if doc["active"] and doc["active"]["id"] == quest_id:
                doc["active"] = None
        await app.state.store.mutate(identity[0], change)

    @app.post("/api/quests/{quest_id}/reflection")
    async def reflect(quest_id: str, payload: ReflectionRequest, identity=Depends(player)):
        key, doc = identity
        receipt = next((item for item in doc["completed"] if item["quest_id"] == quest_id), None)
        if receipt:
            return receipt  # Network retry returns the original award without another model call.
        limit(key)
        quest = doc["active"]
        if not quest or quest["id"] != quest_id:
            raise HTTPException(404, "Quest not found")
        if quest["started_at"] is None:
            raise Conflict("Accept the quest before reflecting.")
        evaluation = await app.state.model.evaluate(quest, payload.reflection)
        xp = xp_for(evaluation)
        if not evaluation.completed:
            return {"quest_id": quest_id, "xp_awarded": 0, "feedback": evaluation.feedback, "retry": True}
        def change(current):
            existing = next((item for item in current["completed"] if item["quest_id"] == quest_id), None)
            if existing:
                return existing
            if not current["active"] or current["active"]["id"] != quest_id:
                raise Conflict("Quest was abandoned while the reflection was being evaluated.")
            current["xp"] += xp
            current["level"] = level_for(current["xp"])
            receipt = {"quest_id": quest_id, "title": quest["title"], "mission_key": quest["mission_key"],
                "xp_awarded": xp, "total_xp": current["xp"], "level": current["level"],
                "feedback": evaluation.feedback, "scores": evaluation.model_dump(exclude={"feedback", "completed"}),
                "completed_at": time.time(), "elapsed_seconds": max(0, int(time.time()-quest["started_at"]))}
            # By default raw reflections are evaluated transiently, not persisted in Atlas.
            if os.getenv("STORE_REFLECTIONS", "false").lower() == "true":
                receipt["reflection"] = payload.reflection
            current["completed"].append(receipt)
            current["active"] = None
            return receipt
        return await app.state.store.mutate(key, change)

    @app.post("/api/transcribe")
    async def transcribe(audio: UploadFile, identity=Depends(player)):
        if os.getenv("ENABLE_VOICE", "false").lower() != "true":
            raise HTTPException(503, "Voice is disabled. Use the text note.")
        limit(identity[0], 6)
        content = await audio.read(8_000_001)
        await audio.close()
        if len(content) > 8_000_000:
            raise HTTPException(413, "Keep recordings below 8 MB")
        if not content:
            raise HTTPException(422, "Recording is empty")
        def work():
            from faster_whisper import WhisperModel
            if app.state.voice is None:
                app.state.voice = WhisperModel(os.getenv("WHISPER_MODEL", "tiny.en"), device="cpu", compute_type="int8",
                    local_files_only=os.getenv("WHISPER_OFFLINE", "false").lower() == "true")
            segments, info = app.state.voice.transcribe(io.BytesIO(content), beam_size=1)
            if info.duration > 65:
                raise ValueError("Keep recordings under one minute")
            return " ".join(segment.text.strip() for segment in segments)[:2000]
        # A single voice job at a time; queued requests fail quickly rather than pile up.
        try:
            await asyncio.wait_for(app.state.voice_lock.acquire(), 1)
        except TimeoutError:
            raise HTTPException(503, "Voice is busy. Please use text or retry.")
        try:
            return {"text": await run_in_threadpool(work)}
        except Exception:
            raise HTTPException(503, "Could not transcribe locally. Check voice dependencies and model cache, or use text.")
        finally:
            app.state.voice_lock.release()

    app.mount("/", StaticFiles(directory=Path(__file__).resolve().parent.parent / "frontend", html=True), name="frontend")
    return app

app = create_app()
