---
name: golden-rules
description: "Inject golden rules reminder every N messages to prevent mid-context forgetting"
metadata: { "openclaw": { "emoji": "⚡", "events": ["message:preprocessed"] } }
---

# Golden Rules Injection

Appends a golden rules reminder to every 30th incoming message body,
so the agent doesn't lose critical behavioral rules in long sessions.
