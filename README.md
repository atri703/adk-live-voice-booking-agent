# ADK Live Voice Booking Agent

A Python Google ADK speech-to-speech appointment assistant with Gemini Live, FastAPI WebSockets, persistent ADK sessions, JSON appointment CRUD, interruption support and a browser microphone client.

## Architecture
Browser 16-kHz PCM microphone -> FastAPI WebSocket -> ADK LiveRequestQueue -> Runner.run_live() -> Gemini Live -> streamed 24-kHz PCM speaker output. ADK tool calls access a local JSON booking store. ADK sessions persist separately in SQLite (not a booking database).

## Setup
Requires Python 3.11+, Google Gemini API key, and a currently supported Gemini Live native-audio model.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
# Set GOOGLE_API_KEY and a supported GEMINI_LIVE_MODEL in .env
mkdir -p data
uvicorn app.main:app --reload
```

Open http://localhost:8000 in Chrome/Edge and allow microphone access. Speak naturally. Disconnect and reconnect from the same browser to reuse the same ADK user/session IDs.

Example: "Book Alex tomorrow at 3 PM for 30 minutes, India time." Then "What bookings do I have?" and "Move Alex's appointment to 4 PM."

## Session recovery
ADK DatabaseSessionService stores conversation history in local SQLite so server restarts preserve events. Live session resumption is requested through RunConfig, but long disconnects start a new audio transport; seamless mid-sentence recovery is not guaranteed.

## Turn taking
Gemini Live server-side VAD handles turn boundaries. Bidirectional tasks allow user interruption. Client clears queued audio when ADK reports interruption.

## Booking data
BOOKINGS_PATH defaults to data/bookings.json; it is created on first write. Booking tools list, create, update and delete appointments. ISO 8601 offsets are required. Overlapping slots are rejected. Atomic replacement and a process-local lock protect the file in a single worker.

## Tests
```bash
ruff check .
python -m pytest -q
```
GitHub Actions runs lint, compilation and unit tests without real API keys.

## Security / limitations
**Local demo only.** The WebSocket is unauthenticated, browser IDs are not secure identities, and every user shares the booking JSON. Do not expose publicly without login, authorization per booking, rate limits, CSRF/origin restrictions, HTTPS and storage locking across processes. Run a single Uvicorn worker. Audio quality and model support depend on the Gemini Live API and device. Use HTTPS for remote microphone access.

## Official documentation
- https://adk.dev/live/get-started/
- https://adk.dev/live/custom-server/
- https://adk.dev/live/sessions/
- https://adk.dev/live/configuration/
- https://adk.dev/live/tools/
