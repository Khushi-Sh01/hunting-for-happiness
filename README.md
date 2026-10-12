# #HuntingForHappiness 🌿

**A real-world gamified habit breaker. Success means you stop using your screen.**

<!-- Replace with an original photograph or clearly labeled artwork. This is a banner placeholder. -->
<!-- ![Hunting for Happiness: a small outdoor mission](docs/assets/banner.png) -->

**Banner placeholder:** add your own image at `docs/assets/banner.png` and uncomment the image above. A real outdoor test photo is a strong choice; do not present generated artwork as field-test evidence.

[Demo video — replace](https://www.youtube.com/watch?v=REPLACE_VIDEO_ID) · [Live demo — replace](https://REPLACE_RENDER_SERVICE.onrender.com) · [DEV post — replace](https://dev.to/REPLACE_HANDLE/REPLACE_POST_SLUG)

Built for [Hacktoberfest 2026 Week 1: Touch Grass](https://dev.to/challenges/hacktoberfest-week1-2026-10-05). The code targets **Best Use of Gemma**, **Best Use of MongoDB Atlas**, and **Best Use of Render**. Category claims require an actual tested integration, not this configuration alone.

## What it does

Choose your mood and a five-, ten-, or fifteen-minute window. Gemma chooses an outdoor mission from a curated task catalog. Accept it, and the interface switches to a quiet, dark Zen Mode. Lock your phone and take the mission outdoors. When you return, describe one detail you noticed. Gemma evaluates that reflection against a public rubric; the backend awards bounded XP and saves the completion.

The web app invites you to lock the phone; browsers cannot force the device to lock or prevent other apps from opening. Reflections are self-reported, not verified evidence that a walk happened. This is a low-stakes attention game, not a medical treatment or a location-tracking application.

## Features

- **Zen Mode:** no feed or gamified distractions during the mission; timestamp-based timer survives reloads and phone lock.
- **Open-weight AI Game Master:** real Ollama calls to Gemma for task selection and structured reflection evaluation.
- **Mood and accessibility preferences:** seated observation or a gentle walk; reviewed tasks never require collecting plants, navigation, or wildlife interaction.
- **Reflection first:** short text notes; optional Whisper voice transcription on the backend with transcript review.
- **Server-owned XP:** schema-validated component scores, 20–50 XP per accepted completion, deterministic levels.
- **Retry-safe progress:** one atomic profile update for XP, level, and quest receipt; duplicate submissions return the original receipt.
- **MongoDB Atlas profile:** durable progress, active quests, completed quests, and AI feedback.
- **Local profile:** SQLite + Ollama + FastAPI for fully local processing after installation/model downloads.
- **Offline trail experience:** cached shell, accepted quest, timer, and draft note; submit manually when connected again.
- **Export and deletion:** export your progress JSON or delete your server profile and browser session/draft.
- **Privacy defaults:** no GPS, no photo upload, no third-party browser scripts, no persisted raw reflections by default.
- **Operational basics:** health and readiness endpoints, bounded model concurrency, redacted inference metadata logs, and tests.

## Architecture

```mermaid
flowchart TD
    UI["Browser: mood and field note"] --> API["FastAPI: auth and quest workflow"]
    API --> GM["Gemma via private Ollama"]
    GM --> VALIDATE["Pydantic validation and XP rules"]
    VALIDATE --> API
    API --> DB["Atlas or local SQLite"]
    API --> UI
    UI --> ZEN["Zen Mode: phone away"]
    ZEN --> UI
```

The browser and API are served from the same origin. No CORS configuration is necessary. The app uses an anonymous bearer session with a cryptographically random token; only its SHA-256 digest is stored as the profile identifier. There is no client-supplied player ID or XP value.

### File map

| Path | Responsibility |
| --- | --- |
| `backend/main.py` | FastAPI routes, bearer sessions, accept/reflect workflow, voice endpoint, static hosting |
| `backend/gemma.py` | Ollama HTTP calls, schema-constrained output, concurrency limit, latency/token logs |
| `backend/domain.py` | Curated missions, Pydantic contracts, deterministic XP/level rules |
| `backend/store.py` | MongoDB and SQLite adapters, compare-and-swap persistence |
| `frontend/index.html` | Mood selector, quest offer, Zen Mode, reflection and reward screens |
| `frontend/app.js` | API integration, saved timestamps/drafts, optional audio recording |
| `frontend/sw.js` | Static shell caching; never caches API responses |
| `tests/` | Workflow/contracts/concurrency tests; opt-in real Atlas test |
| `Dockerfile`, `render.yaml` | Hosted FastAPI/frontend service |
| `deploy/Dockerfile.ollama` | Separate private Gemma inference service with preloaded weights |
| `docs/DEV_SUBMISSION.md` | DEV draft matching the official submission template |
| `docs/VIDEO_SCRIPT.md` | Two-minute pitch, shot list, filming checklist |
| `docs/IMPLEMENTATION.md` | Endpoint explanation, data/model boundaries, design tradeoffs |
| `docs/SUBMISSION_CHECKLIST.md` | Verified challenge requirements and evidence to fill in |
| `docs/EVALUATION.md` | Real-model rubric cases and measurement protocol |
| `docs/SOURCES.md` | Official challenge and implementation references |

### Two deployment profiles

| Profile | Model execution | Progress storage | Offline behavior |
| --- | --- | --- | --- |
| Local text profile | Ollama on your computer | SQLite on that computer | Full generation/evaluation work without internet after downloads; keep the app and Ollama running |
| Atlas/Render partner profile | Private hosted Ollama reached by Render FastAPI | MongoDB Atlas | Phone retains accepted quest/timer/draft; generation, evaluation, and persistence require backend connectivity |

An accepted mission can travel with a disconnected phone. Gemma is **not bundled into the mobile browser**. If the phone cannot reach the backend, its note remains a draft until you reconnect. Service-worker caching requires HTTPS or localhost and one successful online load. This is not a guarantee of complete installability on every browser; SVG manifest icons may need additional PNG sizes for some platforms.

This repository uses no closed model API. Self-hosting still consumes RAM, compute, and electricity. Render and Atlas may have separate costs. The inference service is a conventional running service, not serverless on-device inference.

## Local setup

### 1. Requirements

- Python 3.12 recommended; a terminal and browser.
- [Ollama](https://ollama.com/download), installed on the same computer.
- Sufficient available memory for the selected model, KV cache, and operating system. Start with Gemma 3 4B on a capable laptop; measure on your hardware. Do not assume a small/free cloud instance can load it.
- MongoDB Atlas URI if using the partner profile. No database account is required for the SQLite profile.

### 2. Prepare Gemma locally

Start Ollama's desktop application, or run this in a separate terminal if no server is running:

```bash
ollama serve
```

Download and warm the configured model:

```bash
ollama pull gemma3:4b
ollama run gemma3:4b "Reply with one sentence about noticing a leaf."
ollama list
```

The default is **Gemma 3 4B**, not the unspecified `gemma`/`latest` alias. Review [Gemma terms](https://ai.google.dev/gemma/terms) before use or redistribution. Save the model ID shown by `ollama list` with your demo evidence. To try another locally installed Gemma model, set `GEMMA_MODEL` to its exact Ollama tag and repeat the evaluation protocol; model quality is not assumed equivalent.

Ollama listens on loopback by default. Do not expose its unauthenticated API publicly. API requests are sent only from the backend to the operator-configured runtime.

### 3. Install the app

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Windows PowerShell activation/copy:

```powershell
.venv\Scripts\Activate.ps1
Copy-Item .env.example .env
```

The package has a `requirements-lock.txt` with the versions exercised during package validation. For that version set, install it instead of `requirements.txt`. Optional voice uses a separate dependency file and was not validated with actual audio during package creation.

### 4A. Use MongoDB Atlas

Create a cluster, create a **database user** with read/write access to `hunting_for_happiness`, and allow your current IP in Atlas Network Access. Copy the Drivers connection string. Set these in `.env`:

```dotenv
STORAGE_MODE=mongo
MONGODB_URI=mongodb+srv://YOUR_DB_USER:URL_ENCODED_PASSWORD@YOUR_CLUSTER.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB=hunting_for_happiness
OLLAMA_URL=http://127.0.0.1:11434
GEMMA_MODEL=gemma3:4b
STORE_REFLECTIONS=false
ENABLE_VOICE=false
```

Use the database user's credentials, not your Atlas website login. URL-encode special characters in the username/password. Keep `.env` out of Git; `.gitignore` already excludes it. TLS defaults for `mongodb+srv` are retained; do not disable certificate validation.

The collection is `players`. MongoDB's built-in unique `_id` index identifies each profile. This small demo deliberately embeds its bounded history in one document for atomic updates. It allows at most 500 successful quests per profile; export before deleting/resetting a full profile. There is no search/embedding index.

### 4B. Use the fully local profile

Replace the database settings in `.env`:

```dotenv
STORAGE_MODE=sqlite
SQLITE_PATH=data/happiness.sqlite3
OLLAMA_URL=http://127.0.0.1:11434
GEMMA_MODEL=gemma3:4b
STORE_REFLECTIONS=false
ENABLE_VOICE=false
```

This profile does not connect to Atlas and does not count as demonstrated Atlas use. After installation, cached frontend assets and downloaded Gemma weights permit a local text workflow without internet. Do not use an ephemeral SQLite file as the hosted progress database.

### 5. Run

```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload --no-access-log
```

Open [http://localhost:8000](http://localhost:8000). The API schema is at `/openapi.json`; interactive CDN-loaded documentation is disabled to preserve the same-origin asset policy. Liveness is `/healthz`; `/readyz` checks storage and whether Ollama has the configured model tag. Readiness does not pre-run an inference or promise a latency bound.

For a phone on your home network, binding to `0.0.0.0` makes the server reachable via your computer's LAN IP, subject to your firewall. Plain LAN HTTP generally does not enable microphone access or service workers. Use a trusted HTTPS development setup or the Render deployment for those features. Never publish your bare Ollama port.

## Optional voice reflections

Text reflection works without this feature. Voice uses **Whisper via faster-whisper** on the configured backend; Gemma evaluates the resulting text. It does not use browser cloud speech recognition.

```bash
python -m pip install -r requirements-voice.txt
python -c "from faster_whisper import WhisperModel; WhisperModel('tiny.en', device='cpu', compute_type='int8')"
```

Then set:

```dotenv
ENABLE_VOICE=true
WHISPER_MODEL=tiny.en
WHISPER_OFFLINE=true
```

The one-time warm-up downloads the model. `WHISPER_OFFLINE=true` requires it to exist in the backend user's cache; prepare it under the same OS user that runs the app. `tiny.en` is an English baseline; use an installed multilingual checkpoint and test it if needed. Microphone recording requires HTTPS or localhost and browser permission.

Restart the backend. “Record voice note” appears on the reflection screen. Record at most one minute, stop, review the transcript, then submit. The endpoint caps uploaded bytes, rejects overly long decoded audio, and runs one transcription at a time. The app does not persist the audio.

In local mode audio is processed on your backend computer. On Render it reaches the Render backend, so do not describe that mode as device-private. The standard Dockerfile leaves voice disabled; to host it, install `requirements-voice.txt`, prepare weights in the image/cache for the runtime user, allocate enough memory, and test `/api/transcribe` with an actual browser recording.

## Deploy to Render

### Recommended: hosted app + private Ollama + Atlas

1. Create a **new public GitHub repository** during the challenge window. Push this code; keep `.env`, recordings, and database files untracked.
2. In Render, create a **Private Service** from that repository. Choose Docker and the Dockerfile path `deploy/Dockerfile.ollama`. Select a plan with sufficient RAM/CPU for the actual model; the 4B model and context need substantially more than a tiny instance. Inspect current pricing before provisioning.
3. The inference image starts Ollama during its build, pulls `gemma3:4b`, and then serves the cached model on port 11434 at runtime. The build needs network access and enough resources. Review weight-distribution terms; for repeatable builds, pin the Ollama image digest and record the pulled model ID before your final demo. `latest` in this starting Dockerfile is not a reproducibility guarantee.
4. Copy the **actual internal hostname** supplied by Render. Keep this service private; it has no public `onrender.com` URL. Place both services in the same region/private network.
5. Create the app **Web Service** from the root `Dockerfile`, or use the `render.yaml` Blueprint for the web service. The Blueprint does not create the inference service for you and does not specify an inference plan.
6. Set app secrets/config in Render:

   ```dotenv
   STORAGE_MODE=mongo
   MONGODB_URI=YOUR_REAL_ATLAS_CONNECTION_STRING
   MONGODB_DB=hunting_for_happiness
   OLLAMA_URL=http://YOUR_ACTUAL_PRIVATE_HOSTNAME:11434
   GEMMA_MODEL=gemma3:4b
   STORE_REFLECTIONS=false
   ENABLE_VOICE=false
   ```

7. Add the app service's outbound IP ranges from Render to Atlas Network Access. Use a database user scoped to this database. Avoid a global allowlist as the final configuration.
8. The root Dockerfile launches Uvicorn on `0.0.0.0:$PORT`, as required by Render. Set the web health path to `/healthz`. After deploying, visit `/readyz`, then perform a real generate → accept → reflect cycle and inspect the Atlas receipt.
9. Replace the Render/GitHub/video placeholders in this README and the DEV draft only after that verification.

**Critical:** `OLLAMA_URL=http://localhost:11434` on Render points at the Render app container—not your laptop. The app image does not contain Ollama. Use a reachable private runtime.

If private hosting resources are unavailable, a public video demo of the real local Gemma app can meet the challenge's demo requirement, but do not claim a Render integration you have not used. The package doesn't automatically create cloud resources, publish a repository, or provide external accounts.

To push a fresh local folder to an empty GitHub repository (replace the owner and authenticate with your own account):

```bash
git init
git add .
git commit -m "Build HuntingForHappiness Touch Grass prototype"
git branch -M main
git remote add origin git@github.com:YOUR_OWNER/hunting-for-happiness.git
git push -u origin main
```

Inspect `git status` before committing; secrets, downloaded weights, and real recordings do not belong in the repository. If your repository already has an `origin`, update it rather than adding another one.

For the native Python runtime instead of Docker: build with `pip install -r requirements.txt`, start with `uvicorn backend.main:app --host 0.0.0.0 --port $PORT --no-access-log`, select Python 3.12, and configure the same environment variables. The separate inference service is still required.

## API workflow

| Endpoint | Request / action |
| --- | --- |
| `POST /api/session` | Create a random anonymous bearer session; response `{ "token": "..." }` |
| `GET /api/me` | Retrieve your XP, level, active quest and completion receipts |
| `POST /api/quests` | `{ "mood": "curious", "minutes": 5, "mobility": "walking" }` |
| `POST /api/quests/{id}/accept` | Accept once; repeated acceptance retains its original start timestamp |
| `POST /api/quests/{id}/reflection` | `{ "reflection": "I noticed rounded and pointed leaf edges." }` |
| `DELETE /api/quests/{id}` | Abandon the active quest without changing XP |
| `POST /api/transcribe` | Optional multipart `audio` file; returns a transcript for review |
| `DELETE /api/me` | Delete your profile; the frontend also removes its browser state |

Authenticated requests require `Authorization: Bearer YOUR_SESSION_TOKEN`. Never put the bearer token or Atlas URI in URLs or screenshots.

Example reflection response shape (illustrative, not a real model result):

```json
{
  "quest_id": "a-server-issued-uuid",
  "title": "Three shapes, one small adventure",
  "mission_key": "leaf_shapes",
  "xp_awarded": 45,
  "total_xp": 45,
  "level": 1,
  "feedback": "You noticed how the leaf edges differed.",
  "scores": {"relevance": 2, "observation": 2, "reflection": 1},
  "completed_at": 1791676800,
  "elapsed_seconds": 306
}
```

XP is `20 + 5 × sum(scores)` for a accepted completion, or zero for a revision request. Each component is 0–2; every 100 total XP raises the level. Elapsed time is recorded from the server acceptance timestamp but **does not enforce completion or prove screen-off time**. There is no reward for reporting a better mood.

## Tests and evidence

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

At package validation: **16 passed, one real Atlas integration test skipped**. Backend tests use `StubGemma`; the model adapter tests use an HTTP transport double. Actual Gemma inference, Atlas connectivity, voice transcription, and Render deployment require your own runtime/accounts and were not executed during package creation. See `VALIDATION.md` for the complete evidence boundary and browser checks.

To run the real Atlas test, set `TEST_MONGODB_URI` to a database user allowed to write to the dedicated `hfh_integration_tests` database, then run:

```bash
python -m pytest tests/test_mongo_integration.py -q
```

The test creates and deletes one random document in that database; it does not clear a collection. Use a dedicated test user/cluster where possible. Never commit the URI. See `docs/EVALUATION.md` to measure actual model quality, cold/warm latency, tokens, and offline behavior.

Optional DOM smoke checks run the actual frontend JavaScript with a test server and jsdom. These verify flow/state handling, not rendering or real service-worker behavior. Install Node.js 22+ for this optional check. In terminal one:

```bash
python -m tests.ui_server
```

In terminal two:

```bash
npm ci
npm run test:ui
```

The test server is loopback-only, uses a temporary SQLite file, and **always uses StubGemma**. It is not the real application startup command and must not be used as model evidence. Stop it after testing. The user-facing app has no Node dependency or frontend build step.

## Agent session sharing

DevRelay is for sharing the **coding-agent build session**, not an automatic runtime telemetry integration. Follow the current instructions at [DevRelay](https://devrelay.com), record/share a real session, review it for secrets, and paste the returned URL:

```markdown
[My DevRelay build session](REPLACE_WITH_ACTUAL_SHARED_SESSION_URL)
```

The DEV draft also includes the optional `agent_session` embed placeholder from the challenge template. Preview it after replacing the URL. There is no invented SDK, session ID, or claimed published trace in this repository.

## Security, privacy, and limits

- Anonymous sessions are stored in browser localStorage. Possession of that token grants profile access; there is no account recovery or cross-device login. Use on a trusted device. For production, add a deliberate account/session design, secure HttpOnly cookies, and shared abuse controls.
- API output is never cached by the service worker. The frontend inserts model feedback as text, not HTML. The CSP allows only same-origin assets and blocks framing.
- Raw reflections are not stored by default, but derived feedback/scores can still reveal personal details. In the hosted profile those fields reside in Atlas. Avoid sensitive input and use export/delete controls as needed.
- No prompt/output/URI/auth-token logging is implemented. Inference metadata is logged; hosting and network providers may retain their own operational logs.
- Rate limits and concurrency limits are per process. Before a large public rollout, add shared gateway rate limiting, registration abuse prevention, request-size enforcement at the proxy, provider-specific log review, and tested retention/recovery policies.
- Schema validation restricts numeric scores and keys; it does not make semantic prompt injection impossible. The model has no tools or direct database writes. Review judgment quality and adversarial cases before making rewards consequential.
- The curated catalog and mobility check reduce risky generated instructions. Human judgment still applies to weather, surroundings, accessibility, and safety.
- The model timeout is 90 seconds, not a promise that CPU inference is fast. Busy/unavailable inference returns 503; the UI retains the draft. Record actual latency before describing performance.
- One profile supports 500 completion receipts. A production version needs an archival/history design without losing atomic rewards.

## Contributing

Keep contributions aligned with “less screen, more world.” Add a reviewed catalog task, improve seated access, test a Gemma configuration, or document an outdoor field test. Open an issue describing the behavior you want; for code changes, run the relevant tests and include observed evidence. Do not add engagement feeds or competitive streak pressure without discussing the effect on the core design.

## License and credits

Application code: [MIT](LICENSE), copyright 2026 #HuntingForHappiness contributors. Gemma 3 weights: separate [Google Gemma terms](https://ai.google.dev/gemma/terms). Ollama, FastAPI, PyMongo, faster-whisper, and other dependencies retain their own licenses. Model weights and third-party artwork are not included in the package.

The initial code and document package was created with AI assistance; review, real-model evaluation, deployment, and field testing are the maintainer's responsibility. Credit nontrivial external contributions in your submission.

## Challenge timeline

The official Week 1 entry period is 5 October 2026, 9:00 AM PDT through 11 October 2026, 11:59 PM PDT. The deadline is **12 October 2026, 12:29 PM IST**. The project and repository must be created/completed within that window. Submit a public DEV post with the template, required `devchallenge` and `hf26challenge` tags, a demo, a code link, and an explanation of open innovation. See the [official rules](https://dev.to/page/hacktoberfest-week1-2026-10-05-contest-rules).

**Post-deadline changes:** none recorded in this initial package. If you modify the submitted repository after the deadline, document each change here with date, commit, and description, as required by the challenge FAQ. Verify participant eligibility against the linked rules; a prepared package alone is not a submitted entry.
