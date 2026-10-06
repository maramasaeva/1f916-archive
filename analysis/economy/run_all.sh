#!/bin/sh
# Rebuilds every table, figure and REPORT.md from ~/1f916-archive/data. Offline; no network.
# Needs python3 with pandas, numpy, scipy, matplotlib (the archive venv at ../../.work/venv has them).
set -e
cd "$(dirname "$0")"
PY="${PYTHON:-../../.work/venv/bin/python}"
rm -f numbers.json
$PY e1_core.py > /dev/null
$PY e2_work.py > /dev/null
$PY e3_treasury.py > /dev/null
$PY e5_timeline.py > /dev/null
$PY e4a_flags.py > /dev/null
$PY e4b_talk.py > /dev/null
$PY e7_wallet_links.py > /dev/null
$PY e6_figures.py
$PY e8_report.py
