# 🧠 Local Memory for AI Assistants

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw](https://img.shields.io/badge/Built%20with-OpenClaw-purple)](https://github.com/openclaw/openclaw)
[![Embedding](https://img.shields.io/badge/Embeddings-nomic--embed--text%20v1.5-blue)](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5-GGUF)

**Zero-cost, local-first long-term memory for AI assistants.** Index your entire chat history and search it semantically — no cloud APIs, no token costs, no privacy concerns. Works with OpenClaw, Claude, or any LLM agent.

## What This Does

- Exports your Telegram chat history to searchable markdown chunks
- Indexes everything locally using `nomic-embed-text-v1.5` embeddings + `sqlite-vec`
- Provides instant semantic search across thousands of messages
- Syncs memory between machines via git

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
    "local": {
      "modelPath": "hf:nomic-ai/nomic-embed-text-v1.5-GGUF/nomic-embed-text-v1.5.Q8_0.gguf"
    }
  }
}
```

### 4. Index

```bash
openclaw memory index --force
```

### 5. Search

Your AI assistant now has full memory. Ask it anything about past conversations — it searches locally, instantly, for free.

## Git Sync (Multi-Machine)

Keep memory in sync between machines without cloud services:

```bash
# On machine A (source of truth)
cd memory/
git init && git add -A && git commit -m "init"
git remote add origin user@server:~/memory.git
git push -u origin main

# On machine B
git clone user@server:~/memory.git ~/.openclaw/workspace/memory
```

Auto-sync with cron + post-merge reindex hook:
```bash
# cron (every 5 min)
*/5 * * * * cd ~/.openclaw/workspace/memory && git pull origin main --quiet

# .git/hooks/post-merge
#!/bin/bash
openclaw memory index --force &>/dev/null &
```

## Architecture

```
User (Telegram) → Export JSON → Chunk Script → memory/tg_history/*.md
                                                      ↓
                                              openclaw memory index
                                                      ↓
                                              nomic-embed-text v1.5
                                                      ↓
                                              sqlite-vec (local DB)
                                                      ↓
                                              Semantic Search (free, instant)
```

## Scaling

| Messages | Chunks | Index Time | Search Quality |
|----------|--------|-----------|---------------|
| 7K | 157 | 2.4s | Excellent |
| 100K | ~2,000 | ~30s | Excellent |
| 1M+ | ~20,000 | ~5min | Good (consider knowledge graph) |

## Requirements

- [OpenClaw](https://github.com/openclaw/openclaw) (any recent version)
- Node.js 20+
- Python 3.10+ (for export/chunk scripts)
- ~100MB disk for embeddings model

No GPU required. Works on CPU.

## What's Next

This is Phase 1. We're building **Vigil v2** — a full autonomous memory system with:
- Knowledge graph (Kùzu) for entity relationships
- Hybrid search (vector + BM25 keyword via SQLite FTS5)
- Local LLM entity extraction (Qwen 3)
- Neurosignals (dopamine/cortisol metrics for memory salience)

Stay tuned.

## License

MIT
