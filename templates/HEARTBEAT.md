# HEARTBEAT.md - Startup Health Checks

On session start, verify these are healthy. Report issues to Owner.

## Checks

### 1. Gateway
- `openclaw gateway status` — should be running
- Expected: active on port <GATEWAY_PORT>

### 2. Memory
- `ls <WORKSPACE_PATH>/memory/MEMORY.md` — memory file exists
- `openclaw memory index` — can index without errors
- Expected: MEMORY.md present, CHECKPOINT section at top

### 3. Git Sync
- `cd <WORKSPACE_PATH>/memory && git status` — clean or staged
- `git log -1 --oneline` — recent commit exists
- Expected: no untracked critical files

### 4. Golden Rules Hook
- `ls <WORKSPACE_PATH>/hooks/golden-rules/handler.ts` — hook exists
- `cat ~/.openclaw/golden-rules-counter.json` — counter file exists
- Expected: counter incrementing

<!--
### 5. OPTIONAL: GPU Server
- `sshpass -p '<SSH_PASSWORD>' ssh <USER>@<SERVER_IP> 'echo ok'` — SSH reachable
- `curl -s http://<SERVER_IP>:11434/api/tags` — Ollama running
- Expected: connection OK, models loaded

### 6. OPTIONAL: Ethernet
- `ifconfig <INTERFACE>` — interface exists
- Expected: configured with correct IP
-->

## On Failure
- Report which check failed
- Suggest fix but DO NOT auto-fix without Owner's approval
- Log failure in MEMORY.md

## Format
```
HEARTBEAT_OK: gateway ✅ memory ✅ git ✅ hook ✅
```
or
```
HEARTBEAT_WARN: gateway ✅ memory ✅ git ⚠️ (uncommitted changes) hook ✅
```
