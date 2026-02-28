#!/usr/bin/env python3
"""
Split Telegram Desktop export (JSON) into daily markdown chunks for semantic search.

Usage:
    python tg_to_chunks.py path/to/result.json output_dir/

Creates one .md file per day (or per 50-message block for busy days).
"""
import json, sys, os
from collections import defaultdict

def main():
    if len(sys.argv) < 2:
        print("Usage: python tg_to_chunks.py <result.json> [output_dir]")
        sys.exit(1)

    input_file = sys.argv[1]
    outdir = sys.argv[2] if len(sys.argv) > 2 else './tg_chunks'

    with open(input_file, 'r') as f:
        data = json.load(f)

    messages = data.get('messages', data) if isinstance(data, dict) else data

    # Group by date
    days = defaultdict(list)
    for msg in messages:
        if msg.get('type') != 'message':
            continue
        date = msg.get('date', '')[:10]
        if not date:
            continue

        # Extract text (handles Telegram's mixed text format)
        text_parts = msg.get('text', '')
        if isinstance(text_parts, list):
            text = ''
            for p in text_parts:
                if isinstance(p, str):
                    text += p
                elif isinstance(p, dict):
                    text += p.get('text', '')
        else:
            text = str(text_parts)

        if not text.strip():
            continue

        who = msg.get('from', 'unknown')
        time = msg.get('date', '')[11:16]
        days[date].append(f"[{time}] {who}: {text}")

    os.makedirs(outdir, exist_ok=True)

    count = 0
    total_msgs = 0
    for date in sorted(days.keys()):
        msgs = days[date]
        total_msgs += len(msgs)
        chunk_size = 50
        for i in range(0, len(msgs), chunk_size):
            chunk = msgs[i:i+chunk_size]
            suffix = f"-{i//chunk_size+1}" if len(msgs) > chunk_size else ""
            filename = f"tg-{date}{suffix}.md"
            with open(os.path.join(outdir, filename), 'w') as f:
                f.write(f"# Telegram chat {date}{suffix}\n\n")
                f.write('\n'.join(chunk))
            count += 1

    print(f"Created {count} chunks from {len(days)} days, {total_msgs} messages")
    print(f"Output: {outdir}/")

if __name__ == '__main__':
    main()
