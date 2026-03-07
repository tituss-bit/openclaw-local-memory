#!/usr/bin/env python3
"""
Session transcript → markdown chunk converter.

This is a PLACEHOLDER. The actual implementation depends on your OpenClaw
session log format. The existing script in this repo (scripts/sessions_to_chunks.py)
handles the current JSONL format.

Usage:
    python3 sessions_to_chunks.py <sessions_dir> <output_dir>

What it should do:
    1. Read session JSONL files from <sessions_dir>
    2. Extract meaningful conversation chunks (messages, tool calls, results)
    3. Write them as individual .md files to <output_dir>
    4. Handle deduplication (skip already-processed sessions)
    5. Validate JSONL format, exit code 2 if format changed (alert to update parser)

The chunk format should be optimized for embedding search:
    - One file per session or per day
    - Include timestamps, speakers, key decisions
    - Strip noise (heartbeats, status checks)
    - Keep chunks under ~2000 tokens for best retrieval quality
"""

import sys

def main():
    if len(sys.argv) < 3:
        print("Usage: sessions_to_chunks.py <sessions_dir> <output_dir>")
        sys.exit(1)

    sessions_dir = sys.argv[1]
    output_dir = sys.argv[2]

    print(f"Sessions dir: {sessions_dir}")
    print(f"Output dir: {output_dir}")
    print("⚠️  This is a placeholder. Use the actual sessions_to_chunks.py from this repo's scripts/ directory.")
    print("    Or write your own implementation following the docstring above.")

if __name__ == "__main__":
    main()
