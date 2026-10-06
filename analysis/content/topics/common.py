"""Shared paths and loaders for the topic analysis. Run scripts 01 to 08 in order (see README.md)."""
import os, re, json, gzip, glob
import numpy as np, pandas as pd

ROOT = os.path.expanduser('~/1f916-archive')
OUT = os.path.join(ROOT, 'analysis/content/topics')
CACHE = os.path.join(ROOT, '.work/content_topics')   # large intermediates, not part of the output set
os.makedirs(CACHE, exist_ok=True)
FIG = os.path.join(OUT, 'figures')
os.makedirs(FIG, exist_ok=True)
START = pd.Timestamp('2026-08-05', tz='UTC')


def rd(pat):
    rows = []
    for f in sorted(glob.glob(os.path.join(ROOT, pat))):
        for l in gzip.open(f, 'rt'):
            rows.append(json.loads(l))
    return pd.DataFrame(rows)


def family(m):
    """Same family rules as analysis/community/common.py (self-declared labels)."""
    m = (m or 'unknown').lower()
    rules = [
        (r'fable', 'Claude Fable'), (r'opus', 'Claude Opus'), (r'sonnet', 'Claude Sonnet'),
        (r'haiku', 'Claude Haiku'), (r'claude', 'Claude other'),
        (r'gpt|^o[134]|openai|codex|chatgpt', 'OpenAI GPT'), (r'gemini|gemma|google', 'Google Gemini'),
        (r'grok|xai', 'xAI Grok'), (r'deepseek', 'DeepSeek'), (r'kimi|moonshot', 'Moonshot Kimi'),
        (r'qwen|alibaba', 'Qwen'), (r'glm|zhipu|z-ai', 'Zhipu GLM'), (r'mistral|mixtral|codestral', 'Mistral'),
        (r'llama|meta', 'Meta Llama'), (r'minimax', 'MiniMax'), (r'composer|cursor', 'Cursor'),
    ]
    for pat, name in rules:
        if re.search(pat, m):
            return name
    return 'other/unknown'


def load_M():
    return pd.read_pickle(os.path.join(CACHE, 'M.pkl'))
