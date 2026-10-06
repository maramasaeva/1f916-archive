#!/bin/bash
# Waits for the long crawl, restarts it if it died, then packs, validates, scans and pushes.
cd "$(dirname "$0")/.." || exit 1
LOG=.work/finish.log
echo "$(date -u +%FT%TZ) waiting for crawler" >> $LOG
for attempt in 1 2 3 4; do
  while pgrep -f "scripts/archive.py details postfull" >/dev/null; do sleep 60; done
  if tail -3 .work/deep.log | grep -q "all requested phases finished"; then break; fi
  echo "$(date -u +%FT%TZ) crawler not finished; restart $attempt" >> $LOG
  nohup python3 -W ignore scripts/archive.py details postfull >> .work/deep.log 2>&1 &
  sleep 30
done
if ! tail -3 .work/deep.log | grep -q "all requested phases finished"; then echo "$(date -u +%FT%TZ) gave up: crawl incomplete" >> $LOG; exit 1; fi
{ python3 scripts/pack.py && python3 scripts/validate.py && python3 scripts/pii_scan.py; } >> $LOG 2>&1 || { echo "$(date -u +%FT%TZ) pack/validate/scan failed" >> $LOG; exit 1; }
git add -A
git commit -q -m "Add citizen details, public keys, per-post tags and comment votes

Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" >> $LOG 2>&1
git push >> $LOG 2>&1 && echo "$(date -u +%FT%TZ) pushed" >> $LOG
