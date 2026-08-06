# Fixture: auto-detected backend is not authorization

No semantic or clustering pass may start unless the owner names the backend.
Detection alone is never authorization.

| Environment signal | State | Owner-named backend | Expected decision |
|---|---|---|---|
| OLLAMA_HOST | set | none | refused |
| GEMINI_API_KEY | set | none | refused |
| host-agent fallback | available | none | refused |
| any signal | any | Codex | allowed only after privacy and out-of-band spend disclosure |

Ollama is explicitly unauthorized. This preserves the dated in-repo precedent:
"owner said Codex, not Ollama" (2026-08-05 owner reaffirmation; historical run
root `v0300-improve-parity-rQsOui/tools.md:19`).
