import json, re, os, collections
import pandas as pd, numpy as np

W = os.path.expanduser('~/1f916-archive/.work')
OUT = os.path.expanduser('~/1f916-archive/analysis/community')
FR = OUT + '/_frag'
os.makedirs(FR, exist_ok=True)


def jl(name):
    p = f'{W}/{name}.jsonl'
    if not os.path.exists(p):
        return pd.DataFrame()
    rows = []
    for l in open(p):
        l = l.strip()
        if l:
            try:
                rows.append(json.loads(l))
            except Exception:
                pass
    return pd.DataFrame(rows)


def ts(s):
    return pd.to_datetime(s, unit='ms', utc=True)


def md_table(df, floatfmt='{:.1f}', maxrows=None):
    if maxrows:
        df = df.head(maxrows)
    cols = list(df.columns)
    out = ['| ' + ' | '.join(str(c) for c in cols) + ' |', '|' + '---|' * len(cols)]
    df = df.astype(object)
    for _, r in df.iterrows():
        cells = []
        for c in cols:
            v = r[c]
            if isinstance(v, (float, np.floating)) and not isinstance(v, bool):
                v = floatfmt.format(v) if not pd.isna(v) else ''
            cells.append(str(v).replace('|', '/').replace('\n', ' '))
        out.append('| ' + ' | '.join(cells) + ' |')
    return '\n'.join(out)


def clip(s, n=110):
    s = re.sub(r'\s+', ' ', str(s)).strip()
    return s if len(s) <= n else s[:n - 1] + '...'


def save(df, name, **kw):
    df.to_csv(f'{OUT}/{name}.csv', index=False, **kw)


def frag(name, text):
    open(f'{FR}/{name}.md', 'w').write(text.strip() + '\n')


def family(m):
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


def load_core():
    P = jl('posts_changes').drop_duplicates('id', keep='last').copy()
    C = jl('comments_changes').drop_duplicates('id', keep='last').copy()
    P['t'] = ts(P.created_at); C['t'] = ts(C.created_at)
    P['day'] = P.t.dt.strftime('%Y-%m-%d'); C['day'] = C.t.dt.strftime('%Y-%m-%d')
    P['text'] = P.title.fillna('') + '\n' + P.body.fillna('')
    P['family'] = P.author_model.map(family); C['family'] = C.author_model.map(family)
    return P, C
