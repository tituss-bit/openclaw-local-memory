#!/usr/bin/env python3
"""
Convert OpenClaw session transcripts (JSONL) into daily markdown chunks
for semantic memory indexing.

Usage:
    python3 sessions_to_chunks.py [sessions_dir] [output_dir]

Defaults:
    sessions_dir: ~/.openclaw/agents/main/sessions/
    output_dir:   ~/.openclaw/workspace/memory/sessions/
"""
import json, os, sys, glob
from collections import defaultdict
from datetime import datetime

SESSIONS_DIR = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/.openclaw/agents/main/sessions")
OUTPUT_DIR = sys.argv[2] if len(sys.argv) > 2 else os.path.expanduser("~/.openclaw/workspace/memory/sessions")
CHUNK_SIZE = 50  # messages per chunk
MARKER_FILE = os.path.join(OUTPUT_DIR, ".last_processed")

def get_text(message_obj):
    """Extract text from OpenClaw message content."""
    content = message_obj.get("content", "")
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for c in content:
            if isinstance(c, dict) and c.get("type") == "text":
                parts.append(c.get("text", ""))
            elif isinstance(c, str):
                parts.append(c)
        return " ".join(parts).strip()
    return ""

def process_session(filepath):
    """Parse one JSONL session file into (date, time, role, text) tuples."""
    entries = []
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            
            if obj.get("type") != "message":
                continue
            
            msg = obj.get("message", {})
            role = msg.get("role", "")
            if role not in ("user", "assistant"):
                continue
            
            text = get_text(msg)
            if not text or text in ("HEARTBEAT_OK", "NO_REPLY"):
                continue
            # Skip heartbeat prompts
            if text.startswith("Read HEARTBEAT.md"):
                continue
            # Truncate very long messages
            if len(text) > 500:
                text = text[:500] + "..."
            
            ts = obj.get("timestamp", "")
            date = ts[:10]
            time = ts[11:16]
            
            label = "Human" if role == "user" else "Vigil"
            entries.append((date, time, label, text))
    
    return entries

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Check what we already processed
    processed = set()
    if os.path.exists(MARKER_FILE):
        with open(MARKER_FILE) as f:
            processed = set(f.read().strip().split("\n"))
    
    # Collect all messages grouped by date
    by_date = defaultdict(list)
    session_files = glob.glob(os.path.join(SESSIONS_DIR, "*.jsonl"))
    new_files = []
    
    for sf in session_files:
        basename = os.path.basename(sf)
        mtime = os.path.getmtime(sf)
        key = f"{basename}:{mtime}"
        
        if key in processed:
            continue
        
        new_files.append(key)
        entries = process_session(sf)
        for date, time, label, text in entries:
            by_date[date].append((time, label, text))
    
    if not new_files:
        print("No new sessions to process")
        return
    
    # Sort within each day
    for date in by_date:
        by_date[date].sort()
    
    # Write chunks
    total_chunks = 0
    for date in sorted(by_date):
        msgs = by_date[date]
        for i in range(0, len(msgs), CHUNK_SIZE):
            chunk = msgs[i:i+CHUNK_SIZE]
            chunk_num = i // CHUNK_SIZE + 1
            filename = f"session-{date}-{chunk_num}.md"
            filepath = os.path.join(OUTPUT_DIR, filename)
            
            lines = [f"# OpenClaw session {date} (part {chunk_num})", ""]
            for time, label, text in chunk:
                # Single line per message for density
                lines.append(f"[{time}] {label}: {text}")
            
            with open(filepath, "w") as f:
                f.write("\n".join(lines) + "\n")
            total_chunks += 1
    
    # Update marker
    processed.update(new_files)
    with open(MARKER_FILE, "w") as f:
        f.write("\n".join(sorted(processed)) + "\n")
    
    print(f"Processed {len(new_files)} sessions → {total_chunks} chunks ({sum(len(v) for v in by_date.values())} messages)")

if __name__ == "__main__":
    main()
