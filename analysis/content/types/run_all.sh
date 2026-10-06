#!/bin/bash
# Rerun the whole pipeline (see README.md). The verdict files are human judgements and are inputs.
set -e
cd "$(dirname "$0")"
PY=${PY:-$HOME/1f916-archive/.work/venv/bin/python}
$PY apply_rules.py rules_v1 types_all_v1
$PY apply_rules.py rules_v2 types_all_v2
cp types_all_v2.csv.gz types_all.csv.gz
$PY score_validation.py v1
$PY score_validation.py v2
$PY themes_run.py
$PY score_themes.py
$PY analyze_types.py
$PY examples.py
$PY figures.py
$PY report.py
