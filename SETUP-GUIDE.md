# 👁 Vigil — Setup Guide

Step-by-step guide to building your own persistent memory agent on OpenClaw.

---

## Prerequisites

- macOS or Linux
- Node.js 20+
- Python 3.10+
- An LLM API key (Anthropic, OpenAI, or other supported provider)
- Git
- (Optional) GPU server for local inference

---

## Step 1: Install OpenClaw

```bash
npm install -g openclaw
openclaw onboard
```

Follow the onboarding wizard. It will set up your gateway daemon, configure your LLM provider, and create the workspace directory (default: `~/clawd/`).

---

## Step 2: Create Workspace Files

Copy the templates into your workspace:

```bash
cp templates/SOUL.md ~/clawd/SOUL.md
cp templates/AGENTS.md ~/clawd/AGENTS.md
cp templates/IDENTITY.md ~/clawd/IDENTITY.md
cp templates/USER.md ~/clawd/USER.md
cp templates/TOOLS.md ~/clawd/TOOLS.md
cp templates/HEARTBEAT.md ~/clawd/HEARTBEAT.md
```

Customize each file — replace all `<PLACEHOLDER>` values:

| File | What to change |
|------|---------------|
| **IDENTITY.md** | Agent name, emoji, genesis date, philosophy |
| **USER.md** | Your name, timezone, preferences, interests |
| **TOOLS.md** | Workspace path, gateway port, server details |
| **SOUL.md** | Personality, tone (keep the golden rules intact) |
| **AGENTS.md** | Work protocol (keep the golden rules intact) |
| **HEARTBEAT.md** | Startup health checks for your environment |

### ⚠️ The Golden Rules

The `HARDCODED` golden rules sections in SOUL.md and AGENTS.md are the core value of Vigil. They're duplicated in both files intentionally — redundancy is protection. Modify personality and tone freely. **Do not remove the golden rules** unless you understand the consequences.

---

## Step 3: Set Up Memory

### 3.1 Create memory directory and git repo

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

### 3.2 Import Telegram history (optional)

If you want your agent to remember past Telegram conversations:

```bash
# Export via Telethon
pip install telethon
python scripts/tg_export.py --api-id <YOUR_API_ID> --api-hash <YOUR_API_HASH> --chat <BOT_USERNAME>

# Split into searchable chunks
python scripts/tg_to_chunks.py export/result.json ~/clawd/memory/tg_history/
```

### 3.3 Configure session auto-chunking

The `sessions_to_chunks.py` script converts OpenClaw session transcripts into markdown chunks. Set it up as a cron:

```bash
openclaw gateway config.patch '{
  "cron": [{
    "schedule": "*/10 * * * *",
    "command": "exec",
    "args": {
      "command": "python3 <WORKSPACE_PATH>/scripts/sessions_to_chunks.py ~/.openclaw/agents/main/sessions/ <WORKSPACE_PATH>/memory/sessions/"
    }
  }]
}'
```

### 3.4 Configure memory search

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

### 3.5 Pull an embedding model

```bash
# Local embeddings via Ollama (free, no API costs):
ollama pull nomic-embed-text:v1.5

# Or any other supported embedding model
```

### 3.6 Index

```bash
openclaw memory index --force
```

Your agent can now search across all past conversations semantically.

---

## Step 4: Configure Golden Rules Protection

Two layers prevent the agent from forgetting its rules during long conversations.

### Layer 1: Compaction config

Preserves golden rules when context is summarized at ~120-140k tokens:

```bash
openclaw gateway config.patch "$(cat config-examples/compaction-config.json)"
```

### Layer 2: Golden rules hook

Injects a rules reminder every 30 messages to prevent gradual drift:

```bash
# Copy hook to workspace
cp -r hooks/golden-rules ~/clawd/hooks/golden-rules

# Enable the hook
openclaw gateway config.patch "$(cat config-examples/hooks-config.json)"
```

### Why both?

- **Compaction** handles the token cliff (context summarization)
- **Hook** handles gradual drift (attention dilution over time)
- Neither alone is sufficient. Together, rules are effectively permanent.

---

## Step 5: Set Up /mem Command

The `/mem` command triggers a full memory save:
1. Agent updates CHECKPOINT in MEMORY.md
2. Runs chunking script
3. Commits + pushes to git
4. Reindexes memory

```bash
openclaw gateway config.patch "$(cat config-examples/mem-command-config.json)"
```

Now typing `/mem` in chat triggers the full workflow.

---

## Step 6 (OPTIONAL): GPU Server Setup

For local LLM inference, embedding, or git backup.

### 6.1 Requirements
- Linux + NVIDIA GPU (8GB+ VRAM)
- SSH access
- Ollama or vLLM for inference

### 6.2 Add to TOOLS.md

```markdown
## GPU Server
- IP: <SERVER_IP>
- SSH: `sshpass -p '<SSH_PASSWORD>' ssh <USER>@<SERVER_IP>`
- GPU: <GPU_MODEL> (<VRAM> VRAM)
- Ollama: http://localhost:11434
- Role: GPU inference, git backup
```

### 6.3 Git backup

```bash
# On server: create bare repo
git init --bare ~/memory.git

# On Mac: add remote
cd ~/clawd/memory
git remote add origin <USER>@<SERVER_IP>:~/memory.git
git push -u origin main

# On server: auto-pull cron
*/5 * * * * cd ~/memory && git pull origin main --quiet 2>/dev/null
```

---

## Step 7 (OPTIONAL): Ethernet Toggle

For a direct ethernet connection to your GPU server (faster than WiFi for large transfers):

```bash
cp scripts/switch-ethernet.sh ~/clawd/scripts/
chmod +x ~/clawd/scripts/switch-ethernet.sh
```

Edit the script and replace placeholders. See comments inside for details.

⚠️ **NEVER use `networksetup`** to change interfaces — it resets the entire network stack. Use `ipconfig set` instead.

---

## Verification

After setup, verify:

| Check | How |
|-------|-----|
| Gateway running | `openclaw gateway status` |
| Memory works | Ask agent about a past conversation |
| `/mem` works | Run `/mem`, check git log in memory/ |
| Golden rules persist | Long conversation — agent still follows double confirmation |
| Hook fires | Check `~/.openclaw/golden-rules-counter.json` |
| Session chunking | Check `memory/sessions/` for new .md files |

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Agent doesn't remember past sessions | Run chunking script manually, then `openclaw memory index --force` |
| Golden rules forgotten mid-conversation | Verify both layers: compaction config + hook enabled |
| Memory search returns nothing | Check embedding model is running, reindex |
| Telegram connection drops | Apply `autoSelectFamily` fix: `config-examples/telegram-network-fix.json` |
| Gateway won't start | `openclaw doctor` to diagnose |

---

## What's Next

Once running:
- Customize personality in SOUL.md
- Build memory over time — the agent improves with every session
- Adjust autonomy level if you trust your agent more (or less)
- Add more hooks for custom behaviors
- Set up additional data sources for memory (emails, notes, etc.)
