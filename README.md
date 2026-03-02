# 🧠 Local Memory for AI Assistants

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw](https://img.shields.io/badge/Built%20with-OpenClaw-purple)](https://github.com/openclaw/openclaw)
[![Embedding](https://img.shields.io/badge/Embeddings-nomic--embed--text%20v1.5-blue)](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5-GGUF)

**Zero-cost, local-first long-term memory for AI assistants.** Index your entire chat history and live sessions — no cloud APIs, no token costs, no privacy concerns. Works with OpenClaw, Claude, or any LLM agent.

## What This Does

- Exports your Telegram chat history to searchable markdown chunks
- **Auto-indexes live OpenClaw sessions** — no manual export needed for ongoing conversations
- Indexes everything locally using `nomic-embed-text-v1.5` embeddings + `sqlite-vec`
- Provides instant semantic search across thousands of messages
- Optional git backup to a second machine

## Why?

Cloud embedding APIs (OpenAI, Voyage, etc.) cost $5-10/month and send your private conversations to third parties. This runs 100% locally on your hardware — even a laptop CPU handles it fine.

## Benchmark Results

We tested 5 embedding models on real bilingual (Russian/English) chat data (157 chunks, 7178 messages):

| Model | Size | Index Time | Avg Top-1 Score |
|-------|------|-----------|-----------------|
| **nomic-embed-text v1.5** | **84MB** | **2.4s** | **0.69** |
| EmbeddingGemma 300M | ~200MB | 3.6s | 0.60 |
| Qwen3-Embedding 0.6B | 639MB | 7.6s | 0.56 |
| nomic-embed-text v2 MoE | 512MB | 1.7s | 0.37 |
| jina-embeddings-v5-small | 639MB | 4.9s | 0.35 |

nomic-embed-text v1.5 wins: smallest, fastest, most accurate on multilingual conversational data.

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

This creates daily markdown files (~50 messages each), optimized for embedding search.

### 3. Configure OpenClaw

Add to your `openclaw.json` under `agents.defaults`:

```json
{
  "memorySearch": {
    "provider": "local",
    "enabled": true,
    "sources": ["memory", "sessions"],
    "sync": {
      "intervalMinutes": 10,
      "watch": true,
      "onSessionStart": true
    }
  }
}
```

Key settings:
- `sources: ["memory", "sessions"]` — indexes both memory files AND live session transcripts
- `sync.intervalMinutes: 10` — re-indexes every 10 minutes
- `sync.watch: true` — watches for file changes in real-time
- `sync.onSessionStart: true` — ensures fresh index on every new session

### 4. Index

```bash
openclaw memory index --force
```

### 5. Search

Your AI assistant now has full memory. Ask it anything about past conversations — it searches locally, instantly, for free.

## Auto-Indexing Live Sessions

OpenClaw stores session transcripts as JSONL files. With `sources: ["sessions"]` enabled, these are automatically indexed alongside your memory files.

For additional control, use `scripts/sessions_to_chunks.py` to convert session transcripts into readable markdown chunks:

```bash
python scripts/sessions_to_chunks.py ~/.openclaw/agents/main/sessions/ memory/sessions/
```

This filters out heartbeats and system noise, keeping only human↔assistant dialogue.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Mac (Gateway Host)                 │
│                                                      │
│  Telegram ←→ OpenClaw Gateway ←→ Claude/LLM          │
│                    │                                  │
│                    ↓                                  │
│  Session JSONL → auto-index ──┐                      │
│                               ↓                      │
│  memory/*.md ──────────→ nomic-embed-text v1.5       │
│  memory/tg_history/*.md ─┘         ↓                 │
│                              sqlite-vec (local DB)   │
│                                    ↓                 │
│                            memory_search("query")    │
│                                                      │
│  Sync: watch + reindex every 10 min                  │
└──────────────────────┬──────────────────────────────┘
                       │ git push (backup)
                       ↓
              ┌─────────────────┐
              │  Remote Server   │
              │  (git backup)    │
              │  pull every 5min │
              └─────────────────┘
```

**Single-machine design:** Everything runs on the gateway host. No remote indexing, no distributed components. The remote server is just a git backup — if it's offline, nothing breaks.

## Git Backup (Optional)

Keep a copy of your memory on a second machine:

```bash
# On gateway host
cd memory/
git init && git add -A && git commit -m "init"
git remote add origin user@server:~/memory.git
git push -u origin main

# On backup server (cron, every 5 min)
*/5 * * * * cd ~/memory && git pull origin main --quiet
```

This is purely for redundancy. The backup server doesn't run any indexing or search.

## Scaling

| Messages | Chunks | Index Time | Search Quality |
|----------|--------|-----------|---------------|
| 7K | 157 | 2.4s | Excellent |
| 10K+ | 429 | ~8s | Excellent |
| 100K | ~2,000 | ~30s | Excellent |
| 1M+ | ~20,000 | ~5min | Good (consider knowledge graph) |

## Requirements

- [OpenClaw](https://github.com/openclaw/openclaw) (any recent version)
- Node.js 20+
- Python 3.10+ (for export/chunk scripts)
- ~100MB disk for embeddings model

No GPU required. Works on CPU (M-series Mac, any x86 laptop).

## What's Next

This is Phase 1. We're building **Vigil** — a full autonomous memory system with:
- Knowledge graph for entity relationships
- Hybrid search (vector + BM25 keyword via SQLite FTS5)
- Local LLM entity extraction
- Continuity protocols (auto-checkpoint, session recovery)

Stay tuned.

## License

MIT
