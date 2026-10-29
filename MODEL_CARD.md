# Model Card
## Model
Google Gemini Live native-audio model, configured by GEMINI_LIVE_MODEL. Model ID is a configurable preview default and may need updating based on Google model availability.
## Intended use
Conversational appointment scheduling with a local JSON demonstration dataset.
## Not intended for
Emergency response, sensitive medical scheduling, identity verification, or multi-tenant production bookings.
## Data
User microphone audio is streamed to Gemini Live. Appointment records persist locally in JSON. ADK conversation events persist in local SQLite. No training dataset is bundled.
## Evaluation
Deterministic booking CRUD and overlap tests are included. Voice latency, interruption quality, speech recognition accuracy, tool-call accuracy and security red-team metrics have not yet been measured.
## Privacy and security
Do not deploy publicly without authentication, user-scoped booking authorization, retention policy, consent and encrypted transport. Demo data is shared across users. API credentials must remain server-side.
## Limitations
Preview model availability and quota vary. Session history persistence does not guarantee seamless restoration of interrupted audio. Single-process JSON locking is not suitable for multiple workers.
## Monitoring
Track tool failures, booking conflicts, interrupted turns, latency, reconnect failures and Gemini API errors without logging raw private audio.
