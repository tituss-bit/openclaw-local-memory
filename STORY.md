# From $5/Query to Free Memory: A Month of Building AI That Actually Remembers

*A story about vibe coding, broken memory, and the fix that cost $0.*

## Chapter 1: Hydra — The $5 Experiment

It started with a dumb idea: what if I asked four AI models the same question and made them argue?

I built Hydra — a simple script that sends your prompt to Claude Opus, GPT-4, Gemini, and Grok simultaneously, then feeds their answers back to each other to reach consensus. It had a beautiful interface showing each model's thinking process in real-time.

It worked. Brilliantly. The consensus answers were better than any single model.

One problem: **$5 per query.** Four frontier models × full context = burning money. But Hydra taught me something important: *I can build things from my head and they actually work.*

## Chapter 2: Samsara — The Story

That confidence led to Samsara — a sci-fi narrative I'd been carrying in my head. Three acts, three locations: Varanasi, an orbital casino, and the Moon. A story about singularity, consciousness, and what happens when a Buddhist wanderer, an android who gained true awareness, and a burned-out tech billionaire try to gift humanity transcendence.

I wrote the entire story outline in one session with Claude. The ideas flowed like they'd been waiting to escape.

## Chapter 3: The Game — 8 Hours From Idea to Playable

Then came the question that changed everything: "Can we make a game out of this?"

I'd been playing tactical RPGs — Mutant Year Zero, Miasma Chronicles, Homicidal All-Stars. I wanted something like those: isometric, turn-based, story-driven. But with my story.

**In 8 hours, I went from "wouldn't it be cool to make a game" to a fully working combat engine.**

Isometric grid with tiles. Three heroes — the wanderer, the android, the CEO. 30 skills across 2 branches per character. A meditation/prana system. A neurochip with 8 modules. Procedural audio. 2,864 lines of code, 12 scripts, 4 scenes. A cyberpunk UI with purple buttons and 3D tile depth.

My game literally came alive. I was coding through Claude, describing what I wanted, and watching it materialize. This is what people call "vibe coding" — you describe the vibe, the AI writes the code.

## Chapter 4: The Wall — Memory is Broken

Then I hit the wall.

The game got complex. I needed Claude to remember the architecture, the character stats, the skill tree, the tilemap format. But every new session started blank. Context from yesterday? Gone. That decision about the combat formula? Forgotten. The refactoring plan we spent an hour on? Vanished.

I'd explain the same things over and over. Burn 20,000 tokens just re-establishing context. That's not coding — that's Groundhog Day.

**The AI had no memory.** And without memory, complex projects are impossible.

## Chapter 5: The Rabbit Hole

I spent weeks trying to fix this:

- **File-based memory** — dumping context to markdown files. Worked until there were 70 files and the AI couldn't find anything.
- **Ego/Will/Handoff system** — an elaborate architecture with "intentions", "ledgers", bash scripts, 6 launchd daemons running on my Mac. It was a Rube Goldberg machine that synced garbage between machines and kept resurrecting deleted files.
- **Cloud embeddings** — $5-10/month to send my private conversations to someone else's server. No thanks.

Every solution created new problems. More complexity. More token waste. More frustration.

## Chapter 6: The Fix — Embarrassingly Simple

The breakthrough was realizing I was overcomplicating everything.

Here's what actually works:

1. **Export your entire chat history** (Telegram Desktop → JSON)
2. **Split it into daily chunks** (a 50-line Python script)
3. **Index with local embeddings** (nomic-embed-text v1.5, 84MB model, runs on CPU)
4. **Search with sqlite-vec** (built into OpenClaw)

That's it. 7,178 messages indexed in 2.4 seconds. Semantic search across every conversation I've ever had with my AI. Zero cloud cost. Zero privacy concerns. Runs on a laptop.

I can now ask "what SIM cards did we discuss for the Instagram farm?" and get the exact answer with source, from a conversation 4 weeks ago.

## Chapter 7: The Benchmark That Surprised Us

We tested 5 embedding models on our real bilingual (Russian/English) chat data:

| Model | Size | Avg Score |
|-------|------|-----------|
| **nomic-embed-text v1.5** | **84MB** | **0.69** |
| EmbeddingGemma 300M | 200MB | 0.60 |
| Qwen3-Embedding 0.6B | 639MB | 0.56 |
| nomic v2 MoE | 512MB | 0.37 |
| jina-embeddings-v5 | 639MB | 0.35 |

The smallest, oldest model won. By a lot. On multilingual conversational data, size doesn't matter — training data does.

## Chapter 8: What We Learned

1. **Memory is the #1 bottleneck for AI assistants.** Not model quality, not speed — memory. Without it, every session is a cold start.

2. **Local embeddings are better than cloud** — not just cheaper, but faster (2.4s vs API latency) and more private.

3. **Simple beats clever.** Our 70-file "ego system" with 6 daemons was worse than one MEMORY.md file + search.

4. **Git is the best sync tool for AI memory.** Not Syncthing (it syncs garbage), not cloud storage. Git gives you history, merges, and selective sync.

5. **Your chat history IS your memory.** Don't build elaborate memory architectures. Just index your conversations and search them.

## What's Next

This is Phase 1. We're building Vigil v2 — a full knowledge graph with entity extraction, hybrid search, and neurosignal-based memory salience. Running locally on a laptop with an RTX 5070 Ti.

But Phase 1 already solves the problem. If your AI assistant forgets everything between sessions, **you can fix it today, for free.**

→ [GitHub: openclaw-local-memory](https://github.com/tituss-bit/openclaw-local-memory)

---

*Built by a guy who spent a month learning AI the hard way, and his AI assistant who kept forgetting everything until we fixed it together.*
