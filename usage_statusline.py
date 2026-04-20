#!/usr/bin/env python3
"""
Claude Code status line: 5h/7d usage bars + last two prompt costs.
Colors: blue (low) -> yellow (mid) -> bright-yellow (high) — colorblind-friendly.
Caches every 60 seconds.

Adjust caps if you hit rate limits before bars reach 100%:
  CAP_5H = 2_000_000
  CAP_7D = 30_000_000
"""

import json, os, glob, time, sys
from datetime import datetime, timezone

# ── Config ────────────────────────────────────────────────────────────────
CACHE_FILE = os.path.expanduser("~/.claude/usage_cache.json")
CACHE_TTL  = 60
BAR_WIDTH  = 8
CAP_5H          = 2_000_000
CAP_7D          = 30_000_000
HEAVY_EXCHANGE  = 50_000     # tokens — flag single turns above this as expensive
HEAVY_PAUSE_S   = 120        # seconds — flag turns that took longer than this

# Okabe-Ito (2008) palette — optimized for deuteranopia, true 24-bit ANSI
# Low → Medium → High → Critical using blue/yellow axis (intact in deutan vision)
def tc(r,g,b): return f"\033[38;2;{r};{g};{b}m"
SKY_BLUE  = tc(86,  180, 233)  # #56B4E9 — low      (cool, light blue)
TEAL      = tc(0,   158, 115)  # #009E73 — medium   (blue-green, distinct from sky)
AMBER     = tc(230, 159, 0  )  # #E69F00 — high     (warm orange-yellow)
VERMILLON = tc(213, 94,  0  )  # #D55E00 — critical (deep orange, dark & warm)
DIM   = "\033[2m"
RESET = "\033[0m"

def color(pct):
    if pct < 0.35: return SKY_BLUE
    if pct < 0.60: return TEAL
    if pct < 0.85: return AMBER
    return VERMILLON

def bar(pct):
    filled = round(pct * BAR_WIDTH)
    filled = max(0, min(BAR_WIDTH, filled))
    c = color(pct)
    return c + "█" * filled + DIM + "░" * (BAR_WIDTH - filled) + RESET

def fmt_k(n):
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000:     return f"{n/1_000:.0f}K"
    return str(n)

# ── Cache ─────────────────────────────────────────────────────────────────
def load_cache():
    try:
        with open(CACHE_FILE) as f:
            c = json.load(f)
        if time.time() - c.get("ts", 0) < CACHE_TTL:
            return c
    except:
        pass
    return None

def save_cache(data):
    try:
        data["ts"] = time.time()
        with open(CACHE_FILE, "w") as f:
            json.dump(data, f)
    except:
        pass

# ── Parse JSONL files ─────────────────────────────────────────────────────
def count_usage():
    proj_dir = os.path.expanduser("~/.claude/projects/")
    files    = glob.glob(proj_dir + "**/*.jsonl", recursive=True)

    now    = datetime.now(timezone.utc).timestamp()
    cut_5h = now - 5 * 3600
    cut_7d = now - 7 * 24 * 3600

    tok_5h = tok_7d = 0
    earliest_5h = None   # oldest exchange inside the 5h window
    # Collect all assistant messages with usage, sorted by time
    exchanges = []

    for path in files:
        try:
            with open(path, encoding="utf-8", errors="ignore") as f:
                for line in f:
                    try:
                        obj   = json.loads(line)
                        ts_s  = obj.get("timestamp")
                        if not ts_s: continue
                        ts    = datetime.fromisoformat(ts_s.replace("Z", "+00:00")).timestamp()
                        usage = obj.get("message", {}).get("usage", {})
                        if not usage: continue

                        tokens = (
                            usage.get("input_tokens", 0)
                            + usage.get("cache_creation_input_tokens", 0)
                            + usage.get("output_tokens", 0)
                        )
                        prompt_cost = tokens

                        if ts >= cut_7d: tok_7d += tokens
                        if ts >= cut_5h:
                            tok_5h += tokens
                            if earliest_5h is None or ts < earliest_5h:
                                earliest_5h = ts

                        exchanges.append((ts, prompt_cost))
                    except:
                        pass
        except:
            pass

    # Last two exchanges by time
    exchanges.sort(key=lambda x: x[0])
    last   = exchanges[-1][1] if len(exchanges) >= 1 else 0
    prev   = exchanges[-2][1] if len(exchanges) >= 2 else 0

    # Current session total (tokens since session start based on most recent JSONL file)
    session_files = sorted(files, key=os.path.getmtime, reverse=True)
    session_total  = 0
    heavy_count    = 0
    if session_files:
        try:
            events = []  # (ts, role, tokens)
            with open(session_files[0], encoding="utf-8", errors="ignore") as f:
                for line in f:
                    try:
                        obj   = json.loads(line)
                        ts_s  = obj.get("timestamp")
                        ts    = datetime.fromisoformat(ts_s.replace("Z", "+00:00")).timestamp() if ts_s else None
                        role  = obj.get("message", {}).get("role") if obj.get("message") else None
                        usage = obj.get("message", {}).get("usage", {})
                        t = 0
                        if usage:
                            t = (
                                usage.get("input_tokens", 0)
                                + usage.get("cache_creation_input_tokens", 0)
                                + usage.get("output_tokens", 0)
                            )
                            session_total += t
                        if ts and role:
                            events.append((ts, role, t))
                    except:
                        pass

            # Count heavy turns: >50K tokens OR response took >2 min after user message
            events.sort(key=lambda x: x[0])
            last_user_ts = None
            for ts, role, t in events:
                if role == "user":
                    last_user_ts = ts
                elif role == "assistant":
                    slow = last_user_ts and (ts - last_user_ts) > HEAVY_PAUSE_S
                    if t >= HEAVY_EXCHANGE or slow:
                        heavy_count += 1
                    last_user_ts = None
        except:
            pass

    return {"tok_5h": tok_5h, "tok_7d": tok_7d, "last": last, "prev": prev,
            "session": session_total, "heavy": heavy_count, "earliest_5h": earliest_5h}

# ── Main ──────────────────────────────────────────────────────────────────
cached = load_cache()
if not cached:
    cached = count_usage()
    save_cache(cached)

t5      = cached["tok_5h"]
t7      = cached["tok_7d"]
last    = cached.get("last", 0)
prev    = cached.get("prev", 0)
session     = cached.get("session", 0)
heavy       = cached.get("heavy", 0)
earliest_5h = cached.get("earliest_5h")

p5 = min(t5 / CAP_5H, 1.0)
p7 = min(t7 / CAP_7D, 1.0)

if prev == 0 or last == prev:
    arrow = "─"
elif last > prev:
    arrow = "▲"
else:
    arrow = "▼"

heavy_str = f"  {VERMILLON}⚠{heavy}{RESET}" if heavy > 0 else ""

# Time until the oldest 5h exchange falls out of the window
if earliest_5h:
    reset_in = int((earliest_5h + 5 * 3600) - time.time())
    if reset_in > 0:
        h, m = divmod(reset_in // 60, 60)
        reset_str = f"  {DIM}reset{RESET} {SKY_BLUE}{h}h{m:02d}m{RESET}" if h else f"  {DIM}reset{RESET} {AMBER}{m}m{RESET}"
    else:
        reset_str = ""
else:
    reset_str = ""

line = (
    f"5h {bar(p5)} {color(p5)}{fmt_k(t5)} {int(p5*100)}%{RESET}{reset_str}  "
    f"7d {bar(p7)} {color(p7)}{fmt_k(t7)} {int(p7*100)}%{RESET}  "
    f"{DIM}session{RESET} {SKY_BLUE}{fmt_k(session)}{RESET}{heavy_str}  "
    f"{DIM}prompt {arrow}{RESET} {TEAL}{fmt_k(last)}{RESET} "
    f"{DIM}prev{RESET} {DIM}{fmt_k(prev)}{RESET}"
)
sys.stdout.buffer.write((line + "\n").encode("utf-8"))
