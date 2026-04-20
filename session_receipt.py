#!/usr/bin/env python3
"""
Session receipt — runs on Stop hook.
Shows a token cost breakdown for the current session,
including heuristic rate-limit pause detection.
"""
import json, os, glob, sys
from datetime import datetime, timezone

def tc(r,g,b): return f"\033[38;2;{r};{g};{b}m"
SKY  = tc(86, 180, 233)
TEAL = tc(0, 158, 115)
AMBR = tc(230, 159, 0)
VERM = tc(213, 94, 0)
DIM  = "\033[2m"
BOLD = "\033[1m"
RST  = "\033[0m"

# Known Pro plan soft cap (community benchmark; actual limit varies)
PRO_CAP_5H = 44_000   # ~44K tokens per 5-hour window (sonnet-4 on Pro)

def fmt_k(n):
    if n >= 1_000_000: return f"{n/1_000_000:.2f}M"
    if n >= 1_000:     return f"{n/1_000:.1f}K"
    return str(n)

proj_dir = os.path.expanduser("~/.claude/projects/")
files    = glob.glob(proj_dir + "**/*.jsonl", recursive=True)

# Most recently modified = current session
files.sort(key=os.path.getmtime, reverse=True)
if not files:
    sys.exit(0)

exchanges = []
all_events = []   # (ts, role) for gap analysis

with open(files[0], encoding="utf-8", errors="ignore") as f:
    for line in f:
        try:
            obj   = json.loads(line)
            ts_s  = obj.get("timestamp")
            if not ts_s:
                continue

            ts = datetime.fromisoformat(ts_s.replace("Z", "+00:00"))

            # Track roles for gap analysis
            role = obj.get("message", {}).get("role") if obj.get("message") else None
            if role in ("user", "assistant"):
                all_events.append((ts.timestamp(), role))

            usage = obj.get("message", {}).get("usage", {})
            if not usage:
                continue

            inp      = usage.get("input_tokens", 0) + usage.get("cache_creation_input_tokens", 0)
            cached_r = usage.get("cache_read_input_tokens", 0)
            out_tok  = usage.get("output_tokens", 0)
            exchanges.append({
                "time":   ts.strftime("%H:%M"),
                "ts":     ts.timestamp(),
                "input":  inp,
                "cached": cached_r,
                "output": out_tok,
                "total":  inp + out_tok
            })
        except:
            pass

if not exchanges:
    sys.exit(0)

total_in  = sum(e["input"]  for e in exchanges)
total_out = sum(e["output"] for e in exchanges)
total_cac = sum(e["cached"] for e in exchanges)
grand     = total_in + total_out

# ── Rate-limit heuristic ──────────────────────────────────────────────────
# Find gaps between a user message and the following assistant response.
# Gaps > 3 min after the 3rd exchange likely aren't just typing time.
PAUSE_THRESHOLD = 180  # seconds

suspected_pauses = []
all_events.sort(key=lambda x: x[0])
for i, (ts, role) in enumerate(all_events):
    if role != "user":
        continue
    # Find the next assistant message
    for j in range(i + 1, len(all_events)):
        next_ts, next_role = all_events[j]
        if next_role == "assistant":
            gap = next_ts - ts
            exchange_num = sum(1 for x in all_events[:i] if x[1] == "user")
            if gap > PAUSE_THRESHOLD and exchange_num >= 3:
                t = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%H:%M")
                suspected_pauses.append((gap, t))
            break

# ── Assemble output ───────────────────────────────────────────────────────
out = [
    f"\n{BOLD}── Session kvitto ──────────────────────{RST}",
    f"  {DIM}Antal exchanges:{RST}  {len(exchanges)}",
    f"  {DIM}Input tokens:  {RST}  {SKY}{fmt_k(total_in)}{RST}",
    f"  {DIM}Output tokens: {RST}  {TEAL}{fmt_k(total_out)}{RST}",
    f"  {DIM}Cache reads:   {RST}  {DIM}{fmt_k(total_cac)}{RST}  {DIM}(gratis){RST}",
    f"  {BOLD}Totalt:         {AMBR}{fmt_k(grand)}{RST}",
]

# Last 5 exchanges (chronological, for per-prompt debugging)
out.append(f"\n  {DIM}Senaste prompts:{RST}")
for e in exchanges[-5:]:
    flag = f"  {VERM}⚠{RST}" if e["total"] >= 50_000 else ""
    out.append(f"    {e['time']}  in={fmt_k(e['input'])}  out={fmt_k(e['output'])}  → {AMBR}{fmt_k(e['total'])}{RST}{flag}")

# Top 3 costliest exchanges
if len(exchanges) > 1:
    top = sorted(exchanges, key=lambda x: x["total"], reverse=True)[:3]
    out.append(f"\n  {DIM}Dyraste totalt:{RST}")
    for i, e in enumerate(top, 1):
        out.append(f"    {i}. {e['time']}  in={fmt_k(e['input'])}  out={fmt_k(e['output'])}  → {AMBR}{fmt_k(e['total'])}{RST}")

# Rate limit warnings
if suspected_pauses:
    out.append(f"\n  {VERM}⚠ Misstänkta rate-limit-pauser:{RST}")
    for gap, at in sorted(suspected_pauses, reverse=True)[:5]:
        out.append(f"    {DIM}kl {at}:{RST}  {VERM}{gap/60:.1f} min väntetid{RST}")
    out.append(f"  {DIM}(Claude Code pausar tyst vid rate limits — dessa är heuristiska){RST}")

# Billing sanity note
out.append(f"\n  {DIM}Plan:{RST}  Pro  {DIM}(fast pris, ingen extra-debitering på claude.ai){RST}")
out.append(f"  {DIM}Om du ser extra avgifter: kolla api.anthropic.com/settings/billing{RST}")
out.append(f"  {DIM}(API-nycklar debiteras separat från claude.ai-prenumerationen){RST}")

out.append(f"{BOLD}────────────────────────────────────────{RST}\n")

msg = "\n".join(out)
sys.stdout.buffer.write(msg.encode("utf-8"))
