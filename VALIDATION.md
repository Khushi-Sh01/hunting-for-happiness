# Validation record

Validated on 10 October 2026 using Python 3.12.14 and Node 24.19.0.

## Completed checks

- Backend tests: **16 passed, 1 skipped** with `python -m pytest -q`.
- The skipped test is the real MongoDB/Atlas compare-and-swap integration; no `TEST_MONGODB_URI` was supplied.
- Tests exercise sequential/concurrent idempotent rewards, anonymous session isolation, unaccepted/foreign quests, model outage recovery, schema rejection, XP bounds, mobility constraints, deletion, disabled voice, and static/API headers.
- Application tests use the explicitly named `StubGemma`, and malformed-output tests use an HTTP transport double. Neither is a real Gemma quality evaluation.
- Actual SQLite reads/writes and compare-and-swap operations are exercised, including concurrent requests.
- `python -m compileall -q backend scripts tests` passes.
- JavaScript parser checks for `frontend/app.js` and `frontend/sw.js` pass via `node --check`.
- A jsdom flow check ran the actual frontend JavaScript against the FastAPI/SQLite test server. It passed timestamp restoration, reflection draft restoration, failed offline submission retaining the draft, no offline reward, reconnect submission, reward display, and result persistence, with no captured DOM script errors. The model was `StubGemma`; jsdom is not a real browser and does not validate layout, microphone recording, or service workers.
- Installed Python dependency consistency check passes (`python -m pip check`). `requirements-lock.txt` records the exercised runtime versions.
- The standard root Dockerfile, private Ollama Dockerfile, and Render Blueprint are provided but have not been built/deployed in this environment.

The installed Starlette test client emits a deprecation warning about its HTTPX transport. Tests pass; this is a library migration notice, not a model or app failure.

## Not executed during package creation

- Actual Gemma download/inference and rubric quality review.
- Actual Atlas connectivity or live persistence.
- Render provisioning, resource sizing, private-network connectivity, or cost measurements.
- Real audio transcription/Whisper installation or mobile microphone capture.
- An outdoor field test, measured screen-off time, a YouTube recording, or a published DevRelay session.
- Full visual/browser QA: Playwright was available but no browser executable was installed. Browser downloads returned invalid/truncated archives in this environment, so no browser rendering/real service-worker results are claimed.

## Required next verification

Use `docs/EVALUATION.md` and `docs/SUBMISSION_CHECKLIST.md`. Run real Gemma, test one quest outdoors, verify the actual Atlas/Render integration for the corresponding categories, and replace draft placeholders with recorded evidence.

Text descriptions of expected responses are labeled illustrative; screenshots, latency claims, and first-person test stories must come from the maintainer's real run.
