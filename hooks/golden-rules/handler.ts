import fs from "node:fs";
import path from "node:path";
import os from "node:os";

const EVERY_N = 30;
const COUNTER_FILE = path.join(os.homedir(), ".openclaw", "golden-rules-counter.json");

const REMINDER = `

---
⚡ GOLDEN RULES REMINDER (auto-injected every ${EVERY_N} messages):
1. Double confirmation before ANY action (except read/memory_search)
2. Always estimate timing before action
3. Always search memory before answering about past work
4. Spawn sub-agent for tasks >30 seconds
5. No action before Owner's OK
6. End every response with [📎 Memory:] block
---`;

function getCounter(): number {
  try {
    const data = JSON.parse(fs.readFileSync(COUNTER_FILE, "utf-8"));
    return data.count || 0;
  } catch {
    return 0;
  }
}

function setCounter(count: number): void {
  try {
    fs.writeFileSync(COUNTER_FILE, JSON.stringify({ count }), "utf-8");
  } catch {}
}

const handler = async (event: any) => {
  if (event.type !== "message" || event.action !== "preprocessed") return;

  const count = getCounter() + 1;
  setCounter(count);

  if (count % EVERY_N === 0 && event.context?.bodyForAgent) {
    event.context.bodyForAgent += REMINDER;
    console.log(`[golden-rules] Injected reminder at message #${count}`);
  }
};

export default handler;
