---
title: "#HuntingForHappiness: I Built an AI Game Master That Sends You Outside"
published: false
tags: devchallenge, hf26challenge, gemma, opensource
---

*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 1: Touch Grass](https://dev.to/challenges/hacktoberfest-week1-2026-10-05).*

<!-- AUTHOR: This is a publication draft, not an attestation. Run the app with real Gemma, test outside, deploy it, and replace every REPLACE placeholder before publishing. Verify all first-person statements against your experience. Delete this comment when ready. -->

## What I Built

Most apps ask for one more minute of your attention. **#HuntingForHappiness asks for five minutes of your absence.**

It is a real-world gamified habit breaker for anyone who has opened a feed “for a second” and looked up much later. You choose your mood, how much time you have, and whether you want a gentle walk or a seated outdoor activity. An open-weight Gemma model chooses a small mission: notice three leaf shapes, map a few sounds, or find a color you normally miss.

Then you accept it, and the app gets quiet.

The dashboard disappears. A dark, minimal Zen Mode offers a suggested timer and one invitation: **lock your phone and go notice something.** There is no scrolling feed, leaderboard, photo checkpoint, or notification asking you to return.

When you are back, you leave a short field note—or record a voice note when local transcription is enabled. Gemma evaluates your reflection, and the backend awards bounded XP. The achievement is paying attention, not writing a perfect paragraph or proving that you feel happier.

**Success means you stop using the screen.**

### How It Fits the “Touch Grass” Theme

The physical world supplies the content. The model cannot invent the shape of the leaf you actually noticed; the user has to bring that experience back.

The interaction has three deliberate stages:

1. **Before:** choose a mood and accept a short outdoor mission.
2. **During:** the interface collapses to Zen Mode. Lock the phone and put it away.
3. **After:** describe something you noticed, receive a small reward, and close the app.

A browser cannot force a device to lock. I designed the interface to encourage the action instead. The timer uses a saved timestamp, so it does not need to stay visible or run accurately in the background. A mission can be ended early without punishment. A seated mode makes observation possible without requiring a walk.

### Taking It Outside: My Field Test

**[REPLACE WITH YOUR REAL OUTDOOR TEST BEFORE PUBLISHING. This story scaffold is not a completed test.]**

> I tested #HuntingForHappiness on [DATE] in [GENERAL SETTING; DO NOT PUBLISH AN ADDRESS]. I chose [MOOD], accepted “[ACTUAL MISSION],” and locked my phone for [MEASURED DURATION]. The detail I would usually have missed was [REAL OBSERVATION]. When I returned, I wrote “[YOUR ACTUAL SHORT REFLECTION].” Gemma returned [ACTUAL FEEDBACK] and the server awarded [ACTUAL XP].
>
> The part that worked was [OBSERVED BEHAVIOR]. The part that needed fixing was [REAL FRICTION]. I changed [ACTUAL CHANGE], because [WHAT THE TEST TAUGHT YOU].

**[REPLACE: add one original outdoor photo or a brief clip, with a caption. Do not use a generated image as evidence of field testing.]**

The experiment I want to report is simple: how much of a five-minute mission happened with the phone put away? I would rather show one honest field test than claim an unmeasured reduction in screen time.

## Demo

**YouTube pitch:** [Watch the two-minute demo](https://www.youtube.com/watch?v=REPLACE_VIDEO_ID)

**Live app:** [Try #HuntingForHappiness](https://REPLACE_RENDER_SERVICE.onrender.com)

The video starts with doomscrolling indoors, follows one real quest outdoors with the phone locked, and returns to a voice or text reflection. It ends with the XP receipt, the evaluation code, the Atlas document, and the build-session link.

<!-- After uploading, replace the ID and optionally use this DEV embed:
{% youtube REPLACE_VIDEO_ID %}
Use text reflection in the video unless you enabled and actually tested voice. -->

## Code

[GitHub: hunting-for-happiness](https://github.com/REPLACE_OWNER/hunting-for-happiness)

The repository includes the FastAPI backend, framework-free frontend, model prompts and contracts, offline shell, optional Whisper transcription, tests, Docker configuration, and Render deployment guide.

The application code is MIT licensed. The Gemma 3 weights are governed separately by the [Gemma terms](https://ai.google.dev/gemma/terms); the repository does not bundle model weights. Dependencies retain their own licenses.

## How I Built It

### Gemma: an Open-Weight AI Game Master

The default is **Gemma 3 4B through Ollama**, configured as `gemma3:4b`. This is an explicit, practical baseline—not a claim that it is the newest or fastest model. The application only needs short mission choices and short structured evaluations. A smaller model keeps the hardware requirement more approachable than a large model, while the public rubric makes its decisions inspectable.

Gemma has two real jobs:

- Choose a mission from an application-owned catalog using mood and mobility preferences.
- Read the returned field note and score relevance, concrete observation, and reflection.

I deliberately constrain mission generation. Gemma selects the task; the application supplies its reviewed physical instructions. The model cannot invent a challenge involving an unfamiliar route or picking an unknown plant. The backend also rejects a walking mission selected for seated mode.

The evaluation is schema-constrained JSON and is validated again with Pydantic. A valid JSON shape is still not proof of correct judgment, so the rubric is documented and real-model evaluation cases are provided for manual review.

### The Model Suggests; the Server Awards

I did not give the model an unrestricted `xp` field.

For an accepted completion:

```text
XP = 20 + 5 × (relevance + observation + reflection)
Each score is 0, 1, or 2. Award range: 20–50 XP.
Level = 1 + floor(total XP / 100).
```

If the note does not plausibly describe the mission, the app invites a revision and awards no XP. A brief observation can score well; there is no minimum essay length and no requirement to report an improved mood.

A reflection is self-reported. Neither Gemma nor the timer proves that someone went outdoors. I chose a supportive, low-stakes game over collecting location history, photographs, or biometric evidence.

### MongoDB Atlas: Durable Progress Without Duplicate Rewards

In the partner deployment, Atlas stores each player's XP, level, active quest, and completed quest receipts. Those receipts include the mission, score components, award, feedback, and timestamp. Raw reflections are not stored by default.

XP and the completion receipt are written together in one version-checked document replacement. If two requests race, one wins and the other reads the committed receipt. If a phone loses its connection after saving, submitting the same quest again returns its original award.

This is a database-backed game built on an open-weight model. I do not claim to use Atlas Vector Search or add a vector database for a task that does not need retrieval.

### Render: the Hosted Game Master Backend and Frontend

Render's web service serves FastAPI and the frontend from one origin. A separately provisioned private Ollama service runs Gemma and communicates with the app over Render's private network.

**[REPLACE: show the actual deployment screenshot and `/readyz` response. Do not claim a deployed integration until these work.]**

The hosted profile sends requests to the Render backend and stores progress in Atlas. This is different from running everything on your own laptop. A cloud service cannot reach `localhost` on your personal computer, so the deployment guide uses a real private inference hostname.

### Offline Behavior, With Clear Boundaries

Once a quest is accepted and the application shell is cached, Zen Mode and a text draft work while the phone is disconnected. The reflection waits until the user reconnects and presses Submit; the app never invents a local XP receipt.

For entirely offline generation and evaluation, the local profile runs Ollama, FastAPI, and SQLite on the same computer after model downloads. This package does **not** put Gemma inside the mobile browser. On a trail, a disconnected phone can keep an accepted mission and draft; server evaluation happens on reconnection.

### Optional Voice: Speech First, Gemma Second

Gemma is not used as a speech recognizer. The optional pipeline records a short clip, sends it to the configured backend, and runs **faster-whisper** there. The user reviews the transcript before submitting it to Gemma. Audio is processed transiently and is not stored by the app.

Local profile means local transcription on the backend computer. Hosted profile means the audio reaches the hosted backend. The default deployment leaves voice disabled until its dependencies and model cache are prepared.

### Engineering Evidence

The test suite exercises duplicate and concurrent submissions, session isolation, model outages, invalid model output, mobility constraints, and deterministic XP boundaries. These tests use a named model stub. They check application behavior; they do not establish Gemma's real-world judgment quality.

**[REPLACE: paste your own test output, run the optional real Atlas integration test, and record real Gemma evaluations. Include hardware, model tag/digest, cold/warm latency, and at least one failure case.]**

Inference logs contain model name, latency, and token counts, without the prompt or reflection. A short generation and a short evaluation are enough for one completed quest; I avoided building a continuous chatbot around an experience that should happen away from the screen.

## Why Does Open Innovation Matter?

For this project, running open weights changes what I can promise and inspect.

**Control over sensitive context.** A field note can casually reveal where someone spends time. The app never requests GPS, and the local text profile can evaluate the note without sending it to a closed model API. Hosted requests still reach the operator's backend; open weights alone do not make every deployment private.

**An offline path I can actually build.** After downloading the weights, the local profile can generate missions and evaluate reflections without internet. The phone's cached mission and draft also remain usable during a disconnected walk. I separate those two claims instead of pretending that server-hosted inference runs offline inside the phone.

**No metered model API fee for local inference.** Running Gemma locally does not require a paid per-token API. The computer, electricity, installation downloads, Atlas, and Render are separate costs. “Zero model API spend” is the useful claim—not “all infrastructure is free.”

**A Game Master contributors can change.** The prompts, mission catalog, schemas, and reward rules are visible. A contributor can review why a mission was chosen, improve the rubric, test another Gemma size, or adapt the outdoor tasks without relying on a proprietary endpoint's continued availability.

That matters because this app handles a personal experience, not just a generic chat prompt. The person taking the walk should have a meaningful choice about where their reflection is processed.

## My Agent Session

I used AI assistance for the initial implementation and documentation package. The coding session is separate from the app's runtime inference logs.

**[REPLACE: share a real, reviewed DevRelay session. Remove secrets, private reflections, and Atlas connection strings before sharing.]**

[Explore the build session on DevRelay](REPLACE_WITH_ACTUAL_SHARED_SESSION_URL)

<!-- Alternative embed: use the agent_session tag with the exact URL supplied by DevRelay; preview it in DEV before publishing.
{% agent_session REPLACE_WITH_ACTUAL_SHARED_SESSION_URL %}
Do not guess a session URL. If the embed is unsupported, use the Markdown link above. -->

The useful moments to inspect are the choice to constrain missions, the schema validation around model output, and the fix that makes concurrent reflection submissions award XP once.

## Prize Categories

**[AUTHOR: keep only categories supported by the completed, demonstrated deployment.]**

- **Best Use of Gemma:** real Gemma inference selects missions and evaluates reflections. **[REPLACE: actual model tag/digest and recorded result.]**
- **Best Use of MongoDB Atlas:** Atlas is the progress and quest-receipt data layer. **[REPLACE: Atlas integration test and redacted document screenshot.]**
- **Best Use of Render:** Render hosts the agent frontend and FastAPI orchestration backend, with Gemma served privately. **[REPLACE: actual Render URL and service evidence.]**

DevRelay documents the build process; I am not treating an unimplemented tracking integration as a prize-category feature.

**Built by:** [REPLACE: your DEV handle; list teammate handles if applicable].

My favorite potential outcome is very small: someone closes a feed, walks outside, and notices a leaf they would otherwise have passed. That is the moment #HuntingForHappiness is built for.
