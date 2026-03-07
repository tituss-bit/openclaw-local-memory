# TOOLS.md - Local Notes

## What Goes Here
Environment-specific config: hosts, voices, devices, APIs. No business logic — just facts about your setup.

## Primary Machine — Gateway Host
- Workspace: <WORKSPACE_PATH> (e.g., ~/clawd/)
- Gateway: active, port <GATEWAY_PORT> (default: 18789)
- Memory: local provider (<EMBEDDING_MODEL>), sqlite-vec
- Sync: watch + reindex every 10 min + on session start
- Cron: sessions_to_chunks.py every hour (OpenClaw cron)

## ACP Agents (coding sub-agents)
<!-- Configure your available coding agents -->
- **Codex:** `exec pty:true command:"codex exec --full-auto 'task'"` — via PTY
- **Gemini:** `exec pty:true command:"gemini 'task'"` — via PTY
- **Sub-agent (Opus):** runtime="subagent" — uses API tokens

## Golden Rules Protection
Two layers to prevent forgetting at ~120-140k tokens:
1. **Compaction:** `identifierPolicy: "custom"` + `identifierInstructions` — rules preserved during context summarization
2. **Hook:** `<WORKSPACE_PATH>/hooks/golden-rules/` — injects reminder every 30 messages via `message:preprocessed`
- Counter file: `~/.openclaw/golden-rules-counter.json`

## Network — Known Issues
- **NEVER use `networksetup`** to change interfaces — it resets the entire network stack
- **Use `ipconfig set`** instead — changes only the target interface, no disruption

<!--
## OPTIONAL: GPU Server
- IP: <SERVER_IP> (ethernet, static) / <SERVER_WIFI_IP> (WiFi)
- SSH: `sshpass -p '<SSH_PASSWORD>' ssh <USER>@<SERVER_IP>`
- GPU: <GPU_MODEL> (<VRAM> VRAM)
- Ollama: http://localhost:11434 (<EMBEDDING_MODEL>)
- Role: GPU inference, git backup for memory
- Git pull: cron */5 min
-->

<!--
## OPTIONAL: Ethernet Toggle
- Script: <WORKSPACE_PATH>/scripts/switch-ethernet.sh
- Static mode: `ipconfig set <INTERFACE> MANUAL <STATIC_IP> 255.255.255.0`
- DHCP mode: `ipconfig set <INTERFACE> DHCP`
-->

<!--
## OPTIONAL: Memory Git Repo
- Bare repo: <USER>@<SERVER_IP>:~/memory.git
- Local clone: <WORKSPACE_PATH>/memory/ (source of truth)
- Server clone: backup, auto-pull */5
-->
