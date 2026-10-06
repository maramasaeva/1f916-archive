#!/bin/sh
# Rerun the whole topic analysis. Needs ~/1f916-archive/.work/venv with pandas numpy scikit-learn matplotlib scipy.
# Runtime about 40 minutes on an Apple-silicon laptop (02 and 03 dominate). Optional: K=18 sh run_all.sh to skip the k rule.
set -e
cd "$(dirname "$0")"
PY=../../../.work/venv/bin/python
for s in 01_prepare 02_vectorize_sweep 03_fit 04_topics 05_examples 06_time 07_who_reply 08_vocab 09_figures 10_validation_sample 11_validation_score 12_report; do
  echo "== $s"; $PY $s.py
done
