# 👁 Upgrading OpenClaw to Vigil Architecture

Already have a working OpenClaw installation? This guide adds persistent memory, session continuity, and system monitoring on top of your existing setup. Nothing breaks — Vigil is additive.

---

## What You're Adding

| Feature | What it does |
|---------|-------------|
| **Persistent memory** | MEMORY.md + semantic search (hybrid FTS5 + vectors) |
| **Session continuity** | CHECKPOINT + auto-summarization of past sessions |
| **System watchdog** | vigildog.sh — monitors gateway/Ollama, runs chunking, git backup |
| **Golden rules protection** | Two-layer injection (compaction + hook) — rules survive long sessions |
| **Memory pipeline** | JSONL → chunks → summaries → git backup, fully automated |

## What Changes

- Agent reads workspace files on every session start (personality, rules, identity)
- Memory persists across sessions via MEMORY.md (CHECKPOINT + SESSIONS)
- vigildog monitors system health independently (runs even if gateway is down)
- Heartbeat keeps memory fresh every 30 min (9:00–00:00)
- `/mem` provides manual save points

## What Doesn't Change

- OpenClaw gateway works the same
- All existing channels/plugins unchanged
- No config breaking changes
- Your existing conversations and sessions are preserved

---

## Prerequisites

- Working OpenClaw gateway with Telegram (or other channel)
- LLM API key configured and working
- Git installed
- Python 3.10+
- [Ollama](https://ollama.ai) installed (for local embeddings)

---

## Step 1: Create Workspace Files

Copy templates into your workspace directory:

```bash
cd /path/to/openclaw-local-memory

cp templates/SOUL.md ~/clawd/SOUL.md
cp templates/AGENTS.md ~/clawd/AGENTS.md
cp templates/IDENTITY.md ~/clawd/IDENTITY.md
cp templates/USER.md ~/clawd/USER.md
cp templates/TOOLS.md ~/clawd/TOOLS.md
cp templates/HEARTBEAT.md ~/clawd/HEARTBEAT.md
```

Replace all `<PLACEHOLDER>` values. See [SETUP-GUIDE.md — Step 2](./SETUP-GUIDE.md#step-2-create-workspace-files) for details on each file.

⚠️ **Keep the golden rules sections in SOUL.md and AGENTS.md intact.** These are the core of Vigil's behavioral persistence.

---

## Step 2: Set Up Memory Directory + Git Repo

```bash
mkdir -p ~/clawd/memory/sessions
cd ~/clawd/memory
git init

cat > MEMORY.md << 'EOF'
# Memory

## CHECKPOINT
No checkpoint yet.
EOF

git add -A && git commit -m "init: memory repo"
```

(Optional) Add a remote for backup — see [SETUP-GUIDE.md — Step 7](./SETUP-GUIDE.md#step-7-optional-gpu-server-setup).

---

## Step 3: Configure Memory Search

Pull an embedding model:

```bash
ollama pull nomic-embed-text:v1.5
```

Configure OpenClaw:

```bash
openclaw gateway config.patch '{
  "agents": {
    "defaults": {
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
  }
}'
```

Build the index:

```bash
openclaw memory index --force
```

---

## Step 4: Install Vigildog

```bash
cp scripts/vigildog.sh ~/clawd/scripts/vigildog.sh
chmod +x ~/clawd/scripts/vigildog.sh
```

Edit the script — replace paths and server IPs for your environment.

Add to crontab:

```bash
crontab -e
# Add:
*/5 * * * * /path/to/clawd/scripts/vigildog.sh
```

Vigildog runs independently of the gateway. If the gateway crashes, vigildog restarts it. It also handles session chunking, git push, config backup, and log rotation. See [SETUP-GUIDE.md — Step 6](./SETUP-GUIDE.md#step-6-set-up-vigildog-system-watchdog) for full details.

---

## Step 5: Set Up Golden Rules Protection

### Layer 1: Compaction config

```bash
openclaw gateway config.patch "$(cat config-examples/compaction-config.json)"
```

### Layer 2: Golden rules hook

```bash
cp -r hooks/golden-rules ~/clawd/hooks/golden-rules
openclaw gateway config.patch "$(cat config-examples/hooks-config.json)"
```

Both layers are needed. Compaction handles the token cliff (~120-140k). Hook handles gradual drift. See [SETUP-GUIDE.md — Step 4](./SETUP-GUIDE.md#step-4-configure-golden-rules-protection).

---

## Step 6: Set Up /mem Command

```bash
openclaw gateway config.patch "$(cat config-examples/mem-command-config.json)"
```

Now `/mem` in chat triggers: CHECKPOINT update → chunking → git commit → reindex.

---

## Step 7: Configure Heartbeat Cron

Add a heartbeat that fires every 30 minutes during active hours:

```bash
openclaw gateway config.patch '{
  "cron": [{
    "schedule": "*/30 9-23 * * *",
    "command": "heartbeat"
  }]
}'
```

The agent uses heartbeats to:
1. Update CHECKPOINT in MEMORY.md
2. Summarize new session chunks into SESSIONS section
3. Run health checks
4. Git commit + push

---

## Step 8: Verify Everything Works

| Check | How |
|-------|-----|
| Gateway running | `openclaw gateway status` |
| Memory search works | Ask agent about something from a past session |
| `/mem` works | Run `/mem`, check `git log` in memory/ |
| Golden rules persist | Long conversation — agent still follows double confirmation |
| Hook fires | Check `~/.openclaw/golden-rules-counter.json` |
| Session chunking | Check `memory/sessions/` for `.md` files |
| Vigildog running | `tail ~/clawd/logs/vigildog.log` |
| Vigildog crontab | `crontab -l \| grep vigildog` |
| Heartbeat fires | Check MEMORY.md for recent CHECKPOINT updates |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Agent doesn't remember past sessions | Run chunking manually, then `openclaw memory index --force` |
| Golden rules forgotten mid-conversation | Verify both layers: compaction config + hook enabled |
| Memory search returns nothing | Check Ollama is running, reindex with `--force` |
| Vigildog not running | Check crontab entry, check log for errors |
| Heartbeat not summarizing | Verify cron schedule, check gateway logs |

---

## Migration Checklist

- [ ] Workspace files created and customized
- [ ] Memory directory initialized with git
- [ ] Embedding model pulled (Ollama)
- [ ] Memory search configured and indexed
- [ ] Vigildog installed and in crontab
- [ ] Golden rules: compaction config applied
- [ ] Golden rules: hook installed and enabled
- [ ] `/mem` command configured
- [ ] Heartbeat cron configured
- [ ] All verification checks pass
