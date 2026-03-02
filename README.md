# Local Memory for AI Assistants

Zero-cost, local-first long-term memory for OpenClaw (or any AI assistant). Index your entire chat history and session transcripts — search semantically, no cloud APIs, no token costs.

## What This Does

- Converts Telegram chat history to searchable markdown chunks
- Auto-converts OpenClaw session transcripts to markdown (every 10 min)
- Indexes everything locally using embeddings + `sqlite-vec`
- Provides instant semantic search across thousands of messages
- Syncs memory between machines via git (backup only)

## Why?

Cloud embedding APIs (OpenAI, Voyage, etc.) cost $5-10/month and send your private conversations to third parties. This runs 100% locally on your hardware — even a laptop CPU handles it fine.

## Architecture

Single-machine setup. Mac runs everything, Ubuntu is GPU server + git backup only.

```
                        ┌─────────────────────────────────────────┐
                        │            Mac (Gateway Host)           │
                        │                                         │
  Telegram ←──→ OpenClaw Gateway                                  │
                        │                                         │
  memory/*.md ──────────→ embeddinggemma-300m ──→ sqlite-vec      │
  memory/sessions/*.md ─┘      (local, free)       (local DB)    │
                        │                                         │
  Cron: sessions_to_chunks.py every 10 min (systemEvent, $0)     │
  Sync: reindex every 10 min (watch + interval)                   │
                        │                                         │
                        │  git push ──→ Ubuntu (bare repo backup) │
                        └─────────────────────────────────────────┘
```

## Data Sources

| Source | Script | Output | Schedule |
|--------|--------|--------|----------|
| Telegram history | `tg_to_chunks.py` | `memory/tg_history/*.md` | Manual (on export) |
| OpenClaw sessions | `sessions_to_chunks.py` | `memory/sessions/*.md` | Every 10 min (cron) |
| Manual notes | — | `memory/*.md` | As needed |

## Quick Start

### 1. Export Telegram History

**Windows:** Telegram Desktop → Chat → ⋮ → Export chat history → JSON

**macOS/Linux:** Use the included Telethon script:
```bash
pip install telethon
python scripts/tg_export.py --api-id YOUR_API_ID --api-hash YOUR_API_HASH --chat BOT_USERNAME
```

Get API credentials at https://my.telegram.org/apps

### 2. Split into Chunks

```bash
python scripts/tg_to_chunks.py export/result.json memory/tg_history/
```

Creates daily markdown files (~50 messages each), optimized for embedding search.

### 3. Configure OpenClaw

Add to your `openclaw.json` under `agents.defaults`:

```json
{
  "memorySearch": {
    "provider": "local",
    "enabled": true,
    "sources": ["memory", "sessions"],
    "sync": {
      "onSessionStart": true,
      "watch": true,
      "intervalMinutes": 10,
      "sessions": {
        "deltaMessages": 10
      }
    }
  }
}
```

### 4. Set Up Session Auto-Backup

```bash
# OpenClaw cron (systemEvent — no API cost):
# Every 10 min, convert live sessions to markdown + git push
python3 scripts/sessions_to_chunks.py ~/.openclaw/agents/main/sessions/ memory/sessions/
```

The script validates JSONL format and exits with code 2 if the format changes (alerting you to update the parser).

### 5. Index

```bash
openclaw memory index --force
```

### 6. Search

Your AI assistant now has full memory. Ask it anything about past conversations — it searches locally, instantly, for free.

## Git Sync (Backup)

Keep a backup on a remote machine:

```bash
# On backup server
git init --bare ~/memory.git

# On gateway (source of truth)
cd memory/
git remote add origin user@server:~/memory.git
git push -u origin main

# On backup server — auto-pull every 5 min
*/5 * * * * cd ~/memory && git pull origin main --quiet
```

If the sqlite index breaks: `openclaw memory index --force` rebuilds from markdown files.

## Scaling

| Messages | Chunks | Files | Index Time |
|----------|--------|-------|-----------|
| 7K | 157 | ~160 | ~3s |
| 50K+ | 4,249 | 234 | ~30s |
| 1M+ | ~20,000 | ~1,000 | ~5min |

## Requirements

- [OpenClaw](https://github.com/openclaw/openclaw) (any recent version)
- Node.js 20+
- Python 3.10+ (for export/chunk scripts)
- ~350MB disk for embeddings model

No GPU required. Works on CPU.

## What's Next

Phase 1 (memory + search) is done. Building **Vigil** — an OF chatbot with:
- Persona steering vectors (layers 14-18)
- LorablatedStock 12B + bge-m3 embeddings
- LanceDB (vector) + FalkorDB (knowledge graph)
- EWMA emotion tracking (17 emotions)
- Async fast/slow path architecture

## License

MIT
