# Official source notes

Reviewed 10 October 2026. URLs below are primary sources; model/runtime/library behavior and plans can change. The package chooses a documented Gemma 3 tag rather than assuming the newest model is required.

| Source | Used for |
| --- | --- |
| [Week 1 challenge page](https://dev.to/challenges/hacktoberfest-week1-2026-10-05) | Theme, required tags, category descriptions, and submission-template link |
| [Launch post](https://dev.to/devteam/join-the-hacktoberfest-open-source-ai-challenge-week-1-touch-grass-2450-in-prizes-across-17-4pom) | Outdoor testing encouragement; writing quality priority; optional DevRelay evidence |
| [Week 1 contest rules](https://dev.to/page/hacktoberfest-week1-2026-10-05-contest-rules) | Entry period, new-project requirement, demo/code links, one entry/one prize |
| [Hub and FAQ](https://dev.to/challenges/hf26) | Partner participation and post-deadline change documentation |
| [General contest rules](https://dev.to/page/official-hackathon-rules) | Participant eligibility reference; review directly before submitting |
| [Ollama: Gemma 3 4B](https://ollama.com/library/gemma3:4b) | Downloadable model tag used by the package |
| [Ollama: structured outputs](https://docs.ollama.com/capabilities/structured-outputs) | JSON schema in `format`, schema in prompt, independent Pydantic validation |
| [Google: Gemma terms](https://ai.google.dev/gemma/terms) | Separate weight license/use terms; no claim that MIT covers the weights |
| [PyMongo: create a client](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/connect/mongoclient/) | AsyncMongoClient configuration |
| [PyMongo: async migration](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/reference/migration/) | Async driver approach instead of older Motor examples |
| [Render: FastAPI](https://render.com/docs/deploy-fastapi) | Hosted API start command and environment-provided port |
| [Render: private services](https://render.com/docs/private-services) | Private inference service versus public web service |
| [Render: private network](https://render.com/docs/private-network) | Internal hostname/networking between app and model service |
| [Render: Docker](https://render.com/docs/docker) | Custom Dockerfile service deployment |
| [DevRelay](https://devrelay.com) | Share actual coding-agent session; no invented SDK integration |
| [faster-whisper repository](https://github.com/SYSTRAN/faster-whisper) | Optional CPU/int8 transcription and one-time weight download |

The app's scoring formula, data layout, prompts, mission catalog, privacy defaults, and offline draft workflow are original implementation decisions in this package. They are not claims about a partner's certified scoring system, guaranteed model quality, or production readiness.
