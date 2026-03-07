# 👁 Vigil — Persistent Memory Agent for OpenClaw

**Zero-cost local memory + behavioral persistence for AI assistants.**

Vigil is a framework for building AI agents that don't forget — their memory, their rules, or their identity. Built on [OpenClaw](https://github.com/openclaw/openclaw), it solves two fundamental problems with LLM-based assistants:

1. **They lose memory between sessions** — Vigil adds persistent RAG-based recall from chunked session logs and chat history
2. **They lose their rules mid-session** — Vigil adds two-layer golden rules injection that survives context compaction

The result: an agent that remembers past conversations, follows its behavioral constraints throughout, and maintains its personality across sessions — all running locally, no cloud APIs, no token costs for memory.

---

## What's In This Repo

### Memory & Search (the foundation)
- **Telegram history → searchable chunks** via `tg_to_chunks.py` + `tg_export.py`
- **Session transcripts → searchable chunks** via `sessions_to_chunks.py` (auto, every 10 min)
- **Hybrid search (FTS5 + vectors)** — BM25 keyword matching + semantic embeddings via sqlite-vec. Exact names/dates/terms don't get lost in vector space
- **Git-backed sync** between machines

### Agent Architecture (Vigil)
- **Workspace files** — personality, rules, identity, user profile, environment config
- **Golden rules injection** — two-layer protection against mid-context forgetting
- **Double confirmation protocol** — no autonomous actions without owner approval
- **Session continuity** — `/mem` + `/new` workflow for persistent state across sessions
- **Sub-agent spawning** — long tasks delegated, chat never blocked

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                   Mac (Gateway Host)                      │
│                                                           │
│  Telegram/Web ←──→ OpenClaw Gateway (daemon, 24/7)       │
│                         │                                 │
│  ┌──────────────────────┼────────────────────────┐       │
│  │              Workspace Files                   │       │
│  │  SOUL.md · AGENTS.md · IDENTITY.md            │       │
│  │  USER.md · TOOLS.md · HEARTBEAT.md            │       │
│  │  memory/MEMORY.md (CHECKPOINT)                 │       │
│  └──────────────────────┼────────────────────────┘       │
│                         │                                 │
│  ┌──────────┐    ┌──────┴──────┐    ┌──────────────┐    │
│  │ Hooks    │    │ Memory      │    │ Compaction    │    │
│  │ golden-  │    │ sqlite-vec  │    │ identifierPol │    │
│  │ rules    │    │ + FTS5      │    │ icy: custom   │    │
│  │ (layer2) │    │ (hybrid)    │    │ (layer 1)     │    │
│  └──────────┘    └─────────────┘    └──────────────┘    │
│                         │                                 │
│  Cron: vigildog.sh every 5 min (watchdog + chunking)    │
│  Cron: reindex every 10 min (watch + interval)           │
│                         │                                 │
│                    git push ──→ Server (bare repo backup) │
└──────────────────────────────────────────────────────────┘
         │ (optional)
   ┌───────────┐
   │ GPU Server│  ← inference (vLLM/Ollama), git backup
   └───────────┘
```

## Data Sources

| Source | Script | Output | Schedule |
|--------|--------|--------|----------|
| Telegram history | [`tg_to_chunks.py`](scripts/tg_to_chunks.py) | `memory/tg_history/*.md` | Manual (on export) |
| Telegram export | [`tg_export.py`](scripts/tg_export.py) | JSON export | Manual |
| OpenClaw sessions | [`sessions_to_chunks.py`](scripts/sessions_to_chunks.py) | `memory/sessions/*.md` | Every 5 min (vigildog) |
| Manual notes | — | `memory/*.md` | As needed |

---

## The Problem: Agents Forget Their Rules

LLMs have a predictable failure mode: around **120–140k tokens** into a conversation, your carefully crafted behavioral rules stop being followed. The agent's personality flattens. Safety constraints weaken. It becomes a generic assistant wearing your agent's name.

This happens because:
- **Context compaction** summarizes away the rules along with everything else
- **Attention dilution** deprioritizes system instructions as conversation grows
- **No reinforcement** — rules stated once at the start have no mechanism to persist

### The Solution: Two-Layer Golden Rules Injection

**Layer 1: Compaction protection.** Configure OpenClaw's compactor to explicitly preserve golden rules during context summarization. Rules survive the ~120-140k token cliff.

**Layer 2: Periodic hook injection.** A message hook appends a rules reminder every N messages (default: 30). Catches gradual drift that compaction alone misses.

Together, they make behavioral rules effectively permanent for the lifetime of any session.

---

## Quick Start

### Memory Setup (5 minutes)

#### 1. Export Telegram History (optional)

**Windows:** Telegram Desktop → Chat → ⋮ → Export chat history → JSON

**macOS/Linux:** Use the Telethon script:
```bash
pip install telethon
python scripts/tg_export.py --api-id <YOUR_API_ID> --api-hash <YOUR_API_HASH> --chat <BOT_USERNAME>
```
Get API credentials at https://my.telegram.org/apps

#### 2. Split into Chunks
```bash
python scripts/tg_to_chunks.py export/result.json memory/tg_history/
```
Creates daily markdown files (~50 messages each), optimized for embedding search.

#### 3. Configure OpenClaw Memory

OpenClaw uses **hybrid search** — combining FTS5 (BM25 keyword matching) with vector embeddings (sqlite-vec). This means exact names, dates, and technical terms are found via keyword match, while semantic concepts are found via vectors. Both run locally.

Embeddings are generated by [Ollama](https://ollama.ai) running locally (no cloud APIs):

```bash
# Install Ollama, then pull the embedding model (~261MB)
ollama pull nomic-embed-text
```

Configure in `openclaw.json` under `agents.defaults`:

```json
{
  "memorySearch": {
    "provider": "openai",
    "enabled": true,
    "remote": {
      "baseUrl": "http://localhost:11434/v1",
      "apiKey": "unused"
    },
    "model": "nomic-embed-text",
    "chunking": { "tokens": 256, "overlap": 32 },
    "sync": {
      "onSessionStart": true,
      "onSearch": true,
      "watch": true,
      "intervalMinutes": 10
    }
  }
}
```

> **Why `provider: "openai"`?** Ollama exposes an OpenAI-compatible API at `/v1`. OpenClaw talks to it as if it were OpenAI, but everything runs locally. Zero cost, zero data leaves your machine.

#### 4. Set Up Session Auto-Chunking
```bash
# OpenClaw cron (systemEvent — no API cost):
python3 scripts/sessions_to_chunks.py ~/.openclaw/agents/main/sessions/ memory/sessions/
```

#### 5. Index
```bash
openclaw memory index --force
```

Your agent now has full memory. Ask it anything about past conversations — it searches locally, instantly, for free.

### Agent Setup (15 minutes)

See **[SETUP-GUIDE.md](./SETUP-GUIDE.md)** for the full walkthrough, including:
- Workspace file creation from [templates](./templates/)
- Golden rules protection (both layers)
- `/mem` custom command
- Session continuity protocol
- (Optional) GPU server + ethernet toggle

---

## Workspace Files

Vigil's identity lives in workspace files that OpenClaw loads on every session:

| File | Purpose |
|------|---------|
| **SOUL.md** | Personality, tone, golden rules, autonomy level |
| **AGENTS.md** | Work protocol, rate limits, golden rules (duplicated for redundancy) |
| **IDENTITY.md** | Agent name, emoji, genesis date, description |
| **USER.md** | Owner profile — name, timezone, preferences, interests |
| **TOOLS.md** | Environment config — paths, ports, servers, credentials |
| **HEARTBEAT.md** | Startup health checks |

Templates with placeholders are in [`templates/`](./templates/). The golden rules are the core value — keep them intact.

## The Golden Rules

These are duplicated in SOUL.md and AGENTS.md intentionally. Redundancy is protection.

1. **🔒 Double confirmation** — any action requires owner approval twice (describe → confirm → execute)
2. **⏱ Timing estimates** — every action gets a time/resource estimate before execution
3. **🧠 Memory search** — always check memory before answering about past work
4. **🚀 Sub-agent spawning** — tasks >30 seconds go to sub-agents, never block the chat
5. **✋ No autonomous action** — think freely, act only after approval

---

## Auto-Summarization (Session Continuity)

The main agent automatically maintains a structured memory file (`MEMORY.md`) with two key sections:

- **CHECKPOINT** — brief status snapshot (max 15 lines), updated frequently
- **SESSIONS** — detailed summaries of each work session (5-10 bullet points each)

### How It Works

Every hour, OpenClaw sends a heartbeat to the main agent. On each heartbeat, the agent:

1. **Updates CHECKPOINT** — current status, active tasks, blockers
2. **Scans for unsummarized sessions** — compares chunked session files in `memory/sessions/` against entries in the SESSIONS section of `MEMORY.md`
3. **Generates summaries** — reads raw session chunks, produces concise bullet-point summaries
4. **Appends to MEMORY.md** — new session summaries are added to the SESSIONS section
5. **Commits and pushes** — `git add -A && git commit && git push`

```
Heartbeat (every hour)
    │
    ├── Update CHECKPOINT (brief status)
    │
    ├── Diff: memory/sessions/*.md vs MEMORY.md SESSIONS
    │   └── New chunks found? → Read → Summarize → Append
    │
    ├── Git commit + push
    │
    └── Run health checks (Active Tasks)
```

### Why?

Without this, session history only exists in raw chunks (`memory/sessions/session-2026-03-06-1.md`). These are machine-readable but not structured for quick context restoration.

The SESSIONS section in `MEMORY.md` gives the agent (and you) a human-readable log of everything that happened — decisions made, code written, problems solved. On session start, the agent reads CHECKPOINT first and can quickly scan SESSIONS for deeper context.

### Backup: /mem Command

The `/mem` custom Telegram command triggers the same process manually:
1. Update CHECKPOINT
2. Summarize unsummarized sessions → append to SESSIONS
3. Run `sessions_to_chunks.py` (convert live JSONL → markdown)
4. Git commit + push
5. Reindex memory

This serves as a manual save point before starting a new session (`/new`).

## Vigildog (System Watchdog)

`vigildog.sh` is the system-level cron that runs every 5 minutes, independent of the OpenClaw gateway. It handles infrastructure health and the first stage of the memory pipeline.

### What It Does

1. **Gateway health check** — verifies OpenClaw gateway is running, restarts via launchctl or CLI if down
2. **Ollama health check** — verifies embedding model server is responsive, restarts via brew if down
3. **Memory reindex** — detects stale indexes when batch is disabled, forces reindex
4. **Config backup** — detects changes to `openclaw.json`, creates timestamped backups
5. **JSONL archive** — rsyncs live session files to a backup directory
6. **Session chunking** — runs `sessions_to_chunks.py` to convert JSONL session transcripts into searchable markdown chunks
7. **Git push** — commits and pushes workspace changes (with network fallback)
8. **MEMORY.md rotation** — archives old sections (>7 days, >200 lines) to monthly files
9. **Log rotation** — keeps watchdog log under 1000 lines

### How It Fits the Memory Pipeline

```
JSONL Sessions (live)
    │
    ├── vigildog.sh (every 5 min, crontab)
    │   └── sessions_to_chunks.py → memory/sessions/*.md
    │
    ├── Heartbeat (every 30 min, OpenClaw cron, 9:00-00:00)
    │   └── Agent reads chunks → summarizes → appends to MEMORY.md SESSIONS
    │
    ├── MEMORY.md (CHECKPOINT + SESSIONS = agent's working memory)
    │
    └── git push → backup server
```

The pipeline has two layers:
- **vigildog** (system cron, no API cost): converts raw JSONL into markdown chunks — fast, mechanical, runs even if gateway is down
- **heartbeat** (agent cron, uses LLM): reads chunks, generates human-readable summaries, maintains CHECKPOINT — requires gateway + model

### Sample Crontab Entry

```bash
*/5 * * * * /path/to/clawd/scripts/vigildog.sh
```

### Critical Exit Codes

If `sessions_to_chunks.py` exits with code 2, vigildog logs a CRIT alert — this means the JSONL format has changed and the chunking script needs updating.

## Git Sync (Backup)

```bash
# On backup server
git init --bare ~/memory.git

# On gateway (source of truth)
cd memory/
git remote add origin <USER>@<SERVER_IP>:~/memory.git
git push -u origin main

# On backup server — auto-pull every 5 min
*/5 * * * * cd ~/memory && git pull origin main --quiet
```

If the sqlite index breaks: `openclaw memory index --force` rebuilds from markdown files.

## Scaling

| Messages | Chunks | Files | Index Time |
|----------|--------|-------|------------|
| 7K | 157 | ~160 | ~3s |
| 50K+ | 4,249 | 234 | ~30s |
| 1M+ | ~20,000 | ~1,000 | ~5min |

No GPU required. Works on CPU. ~261MB for `nomic-embed-text` via Ollama.

---

## Repo Structure

```
├── README.md                        ← you are here
├── SETUP-GUIDE.md                   ← full agent setup walkthrough
├── STORY.md                         ← the story behind building this
├── STORY-medium.md                  ← Medium article version
├── scripts/
│   ├── sessions_to_chunks.py        ← session transcript → markdown chunks
│   ├── tg_to_chunks.py              ← Telegram JSON → markdown chunks
│   └── tg_export.py                 ← Telegram history export via Telethon
├── config/
│   └── openclaw-memory-example.json ← memory search config example
├── templates/                       ← workspace file templates (new)
│   ├── SOUL.md
│   ├── AGENTS.md
│   ├── IDENTITY.md
│   ├── USER.md
│   ├── TOOLS.md
│   └── HEARTBEAT.md
├── hooks/golden-rules/              ← golden rules injection hook (new)
│   ├── HOOK.md
│   └── handler.ts
├── config-examples/                 ← OpenClaw config patches (new)
│   ├── compaction-config.json
│   ├── hooks-config.json
│   ├── mem-command-config.json
│   └── telegram-network-fix.json
└── scripts/                         ← utility scripts
    └── switch-ethernet.sh           ← optional: ethernet toggle for GPU server
```

## Requirements

- [OpenClaw](https://github.com/openclaw/openclaw) (any recent version)
- Node.js 20+
- Python 3.10+ (for export/chunk scripts)
- [Ollama](https://ollama.ai) + `nomic-embed-text` (~261MB) for local embeddings
- (Optional) GPU server for local LLM inference

## Philosophy

Vigil is built on three principles:

1. **Persistent memory over ephemeral context.** Sessions end. Memory shouldn't.
2. **Trust through competence, not autonomy.** The agent earns trust by being reliable, not by acting independently.
3. **Rules that survive.** Behavioral constraints are only useful if they persist beyond the initial prompt.

The name comes from Latin *vigilia* — "watchfulness." A vigil stays awake when others sleep. The daemon runs 24/7. Memory persists everything. It doesn't sleep. It doesn't forget. It watches.

## License

MIT
