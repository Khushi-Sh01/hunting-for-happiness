# Part 1 — Architecture and implementation

This package is functional application boilerplate, not just a prompt and a mocked screen. The default backend uses MongoDB Atlas and real HTTP calls to Ollama. Run it with the environment described in the README. The tests inject explicit model doubles, but the normal application never falls back to canned model output.

## Why these boundaries matter

The experience depends on three different responsibilities:

- **Gemma understands language:** picks a mission based on preferences, then evaluates a reflection.
- **Python owns game rules:** validates every returned field and calculates the reward.
- **Storage owns durability:** progress and the quest receipt commit in one atomic operation.

The model cannot call the database, change a player's identity, or invent an arbitrary XP number. The frontend cannot submit XP. This gives you a defensible engineering story for a live demo without treating a probabilistic model as a trusted transaction engine.

## Request lifecycle

1. The browser creates a random anonymous session. The backend stores only the token hash as `_id`.
2. The user sends mood, minutes, and mobility. Gemma receives these preferences plus the catalog. It returns a catalog mission key through a constrained JSON schema.
3. FastAPI attaches the application-owned task text and creates a server-issued UUID. Only one active quest is allowed per player.
4. Accepting writes the original server start timestamp. Repeating the accept request does not restart it.
5. Zen Mode saves that timestamp locally. The timer is recalculated from wall-clock time on every render, so a throttled background browser does not need to run every tick. It is advisory, not a verified screen-off meter.
6. Returning opens a reflection textarea. Every edit is saved as a local draft. The optional microphone feature sends a recording to Whisper on the app's backend and inserts the transcript for review.
7. The backend checks ownership and acceptance, then sends the mission and reflection to Gemma. It never sends GPS or a user-chosen XP amount.
8. Pydantic checks the evaluation. Python computes the award.
9. A revision-checked atomic replacement appends the receipt, increments XP, derives the level, and clears the active quest together.
10. Replaying the same quest returns its existing receipt before model inference. The UI removes the draft only after server confirmation.

## Essential reflection endpoint

The complete runnable implementation is `backend/main.py`. This is the core path, shortened only to expose its responsibilities:

```python
@app.post("/api/quests/{quest_id}/reflection")
async def reflect(quest_id: str, payload: ReflectionRequest,
                  identity=Depends(player)):
    key, doc = identity
    receipt = next((item for item in doc["completed"]
                    if item["quest_id"] == quest_id), None)
    if receipt:
        return receipt

    limit(key)
    quest = doc["active"]
    if not quest or quest["id"] != quest_id:
        raise HTTPException(404, "Quest not found")
    if quest["started_at"] is None:
        raise Conflict("Accept the quest before reflecting.")

    evaluation = await app.state.model.evaluate(quest, payload.reflection)
    xp = xp_for(evaluation)
    if not evaluation.completed:
        return {"quest_id": quest_id, "xp_awarded": 0,
                "feedback": evaluation.feedback, "retry": True}

    def change(current):
        # Recheck after inference: another request may have completed this quest.
        existing = next((item for item in current["completed"]
                         if item["quest_id"] == quest_id), None)
        if existing:
            return existing
        if not current["active"] or current["active"]["id"] != quest_id:
            raise Conflict("Quest was abandoned during evaluation.")
        current["xp"] += xp
        current["level"] = level_for(current["xp"])
        receipt = {
            "quest_id": quest_id, "xp_awarded": xp,
            "total_xp": current["xp"], "level": current["level"],
            "feedback": evaluation.feedback,
        }
        current["completed"].append(receipt)
        current["active"] = None
        return receipt

    return await app.state.store.mutate(key, change)
```

The actual file also retains mission identifiers, score components, completion time and elapsed duration, and makes raw reflection persistence an explicit opt-in. A receipt is authoritative once saved; changing a reflection later does not mint another reward for the same quest.

## Gemma contract and call

```python
class Evaluation(StrictModel):
    completed: bool
    relevance: int = Field(ge=0, le=2)
    observation: int = Field(ge=0, le=2)
    reflection: int = Field(ge=0, le=2)
    feedback: str = Field(min_length=1, max_length=320)

response = await self.http.post("/api/chat", json={
    "model": self.model,
    "stream": False,
    "messages": [{"role": "user", "content": prompt}],
    "format": contract.model_json_schema(),
    "options": {"temperature": 0, "num_predict": 300, "num_ctx": 4096},
})
response.raise_for_status()
evaluation = contract.model_validate_json(response.json()["message"]["content"])
```

`StrictModel` rejects extra keys and requires strict types. `format` constrains generation; Pydantic is an independent validation step. The prompt supplies the same schema as text and describes the rubric. User reflections are serialized as untrusted JSON data and never interpreted as tool instructions.

This is constrained generation, not retrieval-augmented generation. There are no embeddings, vector search, web search, or tools in the Game Master. The small catalog is supplied directly. Two successful model calls cover the nominal generate/evaluate workflow; revision requests, retries, or concurrent inference can increase the call count.

## MongoDB atomic persistence

MongoDB's profile shape is deliberately simple:

```json
{
  "_id": "SHA256_OF_RANDOM_SESSION_TOKEN",
  "revision": 3,
  "xp": 45,
  "level": 1,
  "active": null,
  "completed": [
    {"quest_id": "SERVER_UUID", "xp_awarded": 45, "total_xp": 45,
     "level": 1, "feedback": "SHORT_FEEDBACK", "scores": {"relevance": 2, "observation": 2, "reflection": 1}}
  ]
}
```

The adapter uses PyMongo's async API:

```python
self.client = AsyncMongoClient(uri, serverSelectionTimeoutMS=8000)
self.collection = self.client[database].get_collection(
    "players", write_concern=WriteConcern("majority"))
result = await self.collection.replace_one(
    {"_id": key, "revision": old_revision}, new_document)
```

The update succeeds only when the revision still matches. On a conflict, the change callback reruns against the latest document. Because the callback checks for the quest receipt first, two concurrent submissions cannot increment XP twice. A single document keeps receipt/XP atomic without a multi-document transaction. The document history is capped at 500 completions; separate archival collections and an extended reward ledger are future production work.

## Essential Zen Mode component

This implementation uses plain HTML/JavaScript so there is no frontend build step:

```html
<section id="zen" hidden aria-labelledby="zenTitle">
  <h1 id="zenTitle">Go find your moment.</h1>
  <div id="timer" role="timer">05:00</div>
  <p>You can lock your phone now.</p>
  <button id="return">I'm back · write my field note</button>
</section>
<form id="reflectionForm">
  <label for="note">Your field note</label>
  <textarea id="note" maxlength="2000" required></textarea>
  <button type="submit">Complete my quest</button>
</form>
```

```javascript
const remaining = Math.max(0, Math.ceil(
  state.quest.started_at + state.quest.minutes * 60 - Date.now()/1000
));
document.getElementById('timer').textContent =
  `${String(Math.floor(remaining/60)).padStart(2,'0')}:` +
  String(remaining%60).padStart(2,'0');

const receipt = await api(`/api/quests/${state.quest.id}/reflection`, {
  method: 'POST',
  body: JSON.stringify({reflection: state.note})
});
```

Full event handlers are in `frontend/app.js`; styles in `frontend/style.css`. The browser stores no model-generated HTML. Feedback is rendered with `textContent`. Network failure keeps the quest/draft available; there is no optimistic reward UI claiming points before they are committed.

## Why not auto-lock, background tracking, or location proof?

Browsers cannot lock the OS or prevent switching to other apps. A timer cannot prove a walk. GPS and photos would create sensitive data and a reason to keep handling the device during the mission. This implementation uses an explicit user action and a low-stakes reflection instead. It encourages screen-off time without claiming to enforce or measure it.

## Privacy and offline tradeoffs

The local profile processes text using local Gemma and stores progress locally. The Atlas/Render profile uses cloud infrastructure; notes reach the server for evaluation and feedback reaches Atlas. The service worker only caches the frontend shell. A phone disconnected from its server can continue an accepted mission and save a draft, but cannot run Gemma until connectivity is restored. To evaluate completely offline, run the backend, model and SQLite together on a computer that remains reachable.

Optional audio follows the same boundary: browser recording → configured backend's Whisper → editable transcript → Gemma. Installing Whisper does not make a Render deployment device-local. The application neither saves recordings nor automatically shares traces with DevRelay.

## Implementation status

The code is runnable and locally tested with explicit test doubles and the real SQLite adapter. External inference weights, Atlas credentials, and Render resources are not bundled or provisioned. Use the README to configure them and `docs/EVALUATION.md` to gather real evidence before publishing the draft.
