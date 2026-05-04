#!/usr/bin/env python3
"""Simulated promptlab demo for terminal recording."""
import time, sys, os

os.environ["TERM"] = "xterm-256color"

def c(code, text):
    return f"\033[{code}m{text}\033[0m"

def slow(text, delay=0.012):
    for ch in text:
        sys.stdout.write(ch); sys.stdout.flush(); time.sleep(delay)
    print()

def section(text):
    print(c("1;36", f"\n  {text}"))
    print(c("36", f"  {'─'*56}"))

print(c("1;35", """
  ██████╗ ██████╗  ██████╗ ███╗   ███╗██████╗ ████████╗
  ██╔══██╗██╔══██╗██╔═══██╗████╗ ████║██╔══██╗╚══██╔══╝
  ██████╔╝██████╔╝██║   ██║██╔████╔██║██████╔╝   ██║
  ██╔═══╝ ██╔══██╗██║   ██║██║╚██╔╝██║██╔═══╝    ██║
  ██║     ██║  ██║╚██████╔╝██║ ╚═╝ ██║██║        ██║
  ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚═╝        ╚═╝
       ██╗      █████╗ ██████╗
       ██║     ██╔══██╗██╔══██╗
       ██║     ███████║██████╔╝
       ██║     ██╔══██║██╔══██╗
       ███████╗██║  ██║██████╔╝
       ╚══════╝╚═╝  ╚═╝╚═════╝"""))

time.sleep(0.2)
print(c("2", "  v0.1.0 • Version, diff, and A/B test your LLM prompts"))
time.sleep(0.4)

# Step 1: Init
section("$ promptlab init")
time.sleep(0.3)
print(f"  {c('32','✓')} Initialized promptlab in {c('1','.promptlab/')}")
print(f"    {c('2','Created: .promptlab/prompts/ .promptlab/history/ .promptlab/config.yaml')}")
time.sleep(0.3)

# Step 2: Create prompt
section("$ promptlab create summarizer")
time.sleep(0.3)

print(c("2", "  Creating prompt template: summarizer"))
time.sleep(0.2)
lines = [
    '  name: summarizer',
    '  version: 1',
    '  model: gpt-4o',
    '  template: |',
    '    Summarize the following text in {{style}} style.',
    '    Keep it under {{max_words}} words.',
    '    Text: {{input}}',
    '  variables:',
    '    style: [concise, detailed, bullet-points]',
    '    max_words: 100',
]
for line in lines:
    col = "36" if ":" in line.split("#")[0][:20] else "37"
    if "{{" in line: col = "33"
    print(c(col, line))
    time.sleep(0.04)

print(f"\n  {c('32','✓')} Saved as {c('1','summarizer')} v1 (fingerprint: {c('2','sha256:a3f8c2...')})")
time.sleep(0.4)

# Step 3: Edit and diff
section("$ promptlab diff summarizer")
time.sleep(0.3)

print(c("2", "  Comparing v1 → v2:\n"))
print(c("31", "  - Summarize the following text in {{style}} style."))
print(c("32", "  + Summarize the following text in {{style}} style."))
print(c("32", "  + Focus on key facts and actionable insights."))
print(c("37", "    Keep it under {{max_words}} words."))
print()
print(f"  {c('33','~')} 1 line added, 0 removed")
print(f"  {c('2','  Fingerprint')}: {c('31','a3f8c2...')} → {c('32','7b1d4e...')}")
time.sleep(0.4)

# Step 4: A/B test
section("$ promptlab ab-test summarizer --variants v1,v2 --runs 20")
time.sleep(0.3)

print(c("2", "  Running A/B test: 20 runs per variant...\n"))
time.sleep(0.3)

# Progress bar
for i in range(1, 21):
    pct = i * 5
    filled = i * 2
    bar = c("35", "█" * filled) + c("2", "░" * (40 - filled))
    sys.stdout.write(f"\r  [{bar}] {pct}% ({i*2}/40 runs)")
    sys.stdout.flush()
    time.sleep(0.08)
print()

time.sleep(0.3)
print(f"\n  {c('1','A/B Test Results: summarizer')}")
print(f"  {'─'*56}")
print(f"  {c('1','Metric'):28s} {c('1','v1'):>12s} {c('1','v2'):>12s} {c('1','Δ'):>8s}")
print(f"  {'─'*28} {'─'*12} {'─'*12} {'─'*8}")

metrics = [
    ("Avg quality score",   "7.2",  "8.6",  "+19%", "32"),
    ("Avg token count",     "1,840","1,620", "-12%", "32"),
    ("Avg latency",         "2.1s", "1.8s",  "-14%", "32"),
    ("Avg cost/request",    "$0.018","$0.016","-11%", "32"),
    ("Hallucination rate",  "4.2%", "1.5%",  "-64%", "32"),
]
for name, v1, v2, delta, dcol in metrics:
    print(f"  {name:28s} {c('2',v1):>20s} {c('1',v2):>20s} {c(dcol,delta):>16s}")
    time.sleep(0.12)

print(f"\n  {c('1;32','★ Winner: v2')} ({c('32','+19% quality')}, {c('32','-12% tokens')}, {c('32','-64% hallucination')})")
time.sleep(0.3)

# Step 5: Promote
section("$ promptlab promote summarizer v2 --to production")
time.sleep(0.2)
print(f"  {c('32','✓')} Promoted {c('1','summarizer v2')} → {c('1;32','production')}")
print(f"    {c('2','History: v1(dev) → v2(staging) → v2(production)')}")

time.sleep(0.4)
print(c("1;36", f"\n  {'─'*56}"))
print(c("1;32", "  ✓ Git-like workflow for prompts • A/B test built-in"))
print(c("2",    "    pip install promptlab-ai"))
print(c("1;36", f"  {'─'*56}\n"))
time.sleep(1.0)
