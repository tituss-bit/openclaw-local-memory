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
- **Local embeddings + sqlite-vec** — semantic search across thousands of messages
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
│  │ rules    │    │ + RAG       │    │ icy: custom   │    │
│  │ (layer2) │    │ (search)    │    │ (layer 1)     │    │
│  └──────────┘    └─────────────┘    └──────────────┘    │
│                         │                                 │
│  Cron: sessions_to_chunks.py every 10 min ($0 cost)     │
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
| OpenClaw sessions | [`sessions_to_chunks.py`](scripts/sessions_to_chunks.py) | `memory/sessions/*.md` | Every 10 min (cron) |
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
      "sessions": { "deltaMessages": 10 }
    }
  }
}
```

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

No GPU required. Works on CPU. ~350MB disk for embeddings model.

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
- ~350MB disk for embeddings model
- (Optional) GPU server for local LLM inference

## Philosophy

Vigil is built on three principles:

1. **Persistent memory over ephemeral context.** Sessions end. Memory shouldn't.
2. **Trust through competence, not autonomy.** The agent earns trust by being reliable, not by acting independently.
3. **Rules that survive.** Behavioral constraints are only useful if they persist beyond the initial prompt.

The name comes from Latin *vigilia* — "watchfulness." A vigil stays awake when others sleep. The daemon runs 24/7. Memory persists everything. It doesn't sleep. It doesn't forget. It watches.

## License

MIT
