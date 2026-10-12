# Two-minute YouTube pitch: #HuntingForHappiness

**Title:** I Built an AI That Sends You Outside | #HuntingForHappiness

**Target:** 2:00, approximately 273 spoken words at a natural demo pace. Record a real outdoor sequence separately; use labeled cuts to compress the mission. The script is for a finished, tested build. Use text input unless you actually enabled and tested voice. Display genuine model results and genuine progress.

| Time | Camera / screen | Spoken narration |
| --- | --- | --- |
| 0:00–0:12 | Close shot indoors: thumb scrolling a generic feed. Cut to developer looking up, then the app title. Do not expose other people's private messages. | “I opened my phone for a minute. Somehow, the minute became twenty. So I built an app with a different goal: success means you stop using the screen. Meet Hunting for Happiness.” |
| 0:12–0:28 | Screen capture: select Restless, five minutes, gentle walk. Click Find my outdoor mission. Show the actual Gemma-selected mission. | “Choose your mood and a little time. Google's open-weight Gemma model chooses a small outdoor mission from a reviewed catalog. Mine is to notice three leaf shapes. No map, no leaderboard, and no photo hunt that keeps me looking through a camera.” |
| 0:28–0:46 | Accept mission. UI enters dark Zen Mode. Over-shoulder shot: press the physical lock button. Wide shot walking outdoors on a safe, familiar path; phone stays in pocket. | “When I accept, the dashboard disappears into Zen Mode. I lock my phone and put it away. The timer resumes when I return. The experience happens outside: with leaves, ordinary sounds, and the details I usually scroll past.” |
| 0:46–1:02 | Original close-ups of leaves in place and developer pausing. Cut back; label “Five minutes later — edited for time” only if true. Type the real note or show actual tested recording/transcript. | “Back home, I leave a short field note about what I actually noticed. Optional Whisper transcription runs on my configured backend, and I review the text before submitting. Nothing requires a perfect paragraph or a happier mood.” |
| 1:02–1:22 | Show genuine Gemma feedback and XP. Split screen with evaluation schema, `xp_for`, and the saved Atlas receipt. Highlight mission ID and award; hide token and connection URI. | “Gemma scores relevance, observation, and reflection. FastAPI validates that JSON and calculates a bounded reward. MongoDB Atlas stores XP, levels, and quest receipts. Duplicate submissions return the original receipt, so reconnecting cannot award points twice.” |
| 1:22–1:42 | Render service dashboard and `/readyz`, then diagram showing local and hosted profiles. For offline shot, show a previously accepted mission and note with network disconnected. | “Render hosts the app and agent backend, connected to private Gemma inference. For full offline processing, I can run Gemma and the app locally. A disconnected phone keeps its accepted mission and draft, then submits after reconnecting. Open weights give me control without a metered model API fee.” |
| 1:42–2:00 | GitHub tree, passing tests, real reviewed DevRelay session. End outdoors, closing the app; final card with repo, demo QR/link, required tags. | “The code, prompts, tests, and reward rules are open. My DevRelay session shows how the decisions were made. This is my Touch Grass entry for Hacktoberfest. Hunting for Happiness turns a tiny screen interaction into a reason to leave it behind.” |

## Filming checklist

- Capture a real mission and reflection using the exact deployed/local version shown in the code.
- If the mission is five minutes, do it for real; compress the footage with a visible time-jump caption.
- Keep the phone away during outdoor footage; have a companion film or use a fixed tripod.
- Record in a familiar, safe outdoor setting. Film observations without picking plants or disturbing wildlife.
- Redact Render environment values, database URI, tokens, exact home location, and private reflections.
- Show the actual model tag and at least one real output. Don't substitute a stub result.
- Show the real Atlas write and real Render runtime if entering those categories.
- Add readable captions; allow the results screen enough time to be read.
- Time the narration. If it exceeds 2:00, cut transitions or shorten phrasing before speeding up speech.

## Video description draft

> #HuntingForHappiness is a real-world habit breaker built for Hacktoberfest 2026 Week 1: Touch Grass. Gemma selects a short outdoor mission, Zen Mode invites you to lock your phone, and a reflection earns bounded XP stored in MongoDB Atlas. Render hosts the agent frontend and backend. Open weights support a separately configured local/offline profile.
>
> Demo: [REPLACE]
> GitHub: [REPLACE]
> DEV post: [REPLACE]
> DevRelay build session: [REPLACE]
>
> #devchallenge #hf26challenge #Gemma #Hacktoberfest

**Offline caveat for the description:** this package runs Gemma on the backend computer, not inside the mobile browser. Hosted evaluation requires reconnecting. Local inference has no metered model API charge; hardware and hosting can cost money.
