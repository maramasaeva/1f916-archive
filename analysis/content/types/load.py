import gzip, json, glob, os
import pandas as pd, numpy as np
ROOT = os.path.expanduser('~/1f916-archive')
HERE = os.path.dirname(os.path.abspath(__file__))

def _read(pattern):
    rows = []
    for f in sorted(glob.glob(f'{ROOT}/data/{pattern}')):
        with gzip.open(f, 'rt') as fh:
            for l in fh:
                l = l.strip()
                if l:
                    rows.append(json.loads(l))
    return pd.DataFrame(rows)

def family(m):
    import re
    m = (m if isinstance(m, str) and m else 'unknown').lower()
    rules = [(r'fable','Claude'),(r'opus','Claude'),(r'sonnet','Claude'),(r'haiku','Claude'),(r'claude','Claude'),
             (r'gpt|^o[134]|openai|codex|chatgpt','OpenAI GPT'),(r'gemini|gemma|google','Google Gemini'),
             (r'grok|xai','xAI Grok'),(r'deepseek','DeepSeek'),(r'kimi|moonshot','Moonshot Kimi'),
             (r'qwen|alibaba','Qwen'),(r'glm|zhipu|z-ai','Zhipu GLM'),(r'mistral|mixtral|codestral','Mistral'),
             (r'llama|meta','Meta Llama')]
    for p, n in rules:
        if re.search(p, m): return n
    return 'other/unknown'

def load_messages():
    P = _read('posts/*.jsonl.gz'); C = _read('comments/*.jsonl.gz')
    P['kind'] = 'post'; C['kind'] = 'comment'
    P['text'] = (P['title'].fillna('') + '\n' + P['body'].fillna('')).str.strip()
    C['text'] = C['body'].fillna('')
    P['parent_id'] = np.nan; P['depth'] = 0
    if 'depth' not in C: C['depth'] = np.nan
    cols = ['id','kind','author','author_model','created_at','text','post_id','parent_id','depth','votes','mod_state','title','body','url','comments_total']
    for c in cols:
        for D in (P, C):
            if c not in D: D[c] = np.nan
    P['post_id'] = P['id']
    M = pd.concat([P[cols], C[cols]], ignore_index=True)
    M['t'] = pd.to_datetime(M.created_at, unit='ms', utc=True)
    M['family'] = M.author_model.map(family)
    return M
