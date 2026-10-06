"""Load posts and comments, build clean modelling text, keep original text for examples."""
from common import *

CODE = re.compile(r'```.*?```', re.S)
INLINE = re.compile(r'`[^`]*`')
URL = re.compile(r'https?://\S+|www\.\S+')
HASH = re.compile(r'\b0x[0-9a-fA-F]{6,}\b|\b[0-9a-fA-F]{12,}\b|\b(?:sha256|sha1|md5):\S+', re.I)
EMAIL = re.compile(r'\S+@\S+\.\S+')
MDSYM = re.compile(r'[#*_>|~\[\]\(\){}=<]+')


def strip_for_display(s):
    s = CODE.sub(' ', s)
    s = INLINE.sub(' ', s)
    s = URL.sub(' ', s)
    s = HASH.sub(' ', s)
    s = EMAIL.sub(' ', s)
    s = re.sub(r'^\s{0,3}#{1,6}\s*', '', s, flags=re.M)
    s = re.sub(r'\*\*|__|`', '', s)
    s = re.sub(r'^\s*[-*+]\s+', '', s, flags=re.M)
    return re.sub(r'\s+', ' ', s).strip()


def clean_for_model(s):
    s = strip_for_display(s).lower()
    s = MDSYM.sub(' ', s)
    s = re.sub(r"[‘’]", "'", s)
    s = re.sub(r"n't\b|'(?:s|re|ve|ll|d|m)\b", '', s)   # contractions: drop the clitic, keep the stem
    toks = re.findall(r"[a-zà-ɏ][a-zà-ɏ'\-]*[a-zà-ɏ]|[a-z]", s)
    toks = [t for t in toks if not any(ch.isdigit() for ch in t)]
    return ' '.join(toks)


P = rd('data/posts/*.jsonl.gz')
C = rd('data/comments/*.jsonl.gz')
P['uid'] = 'p' + P.id.astype(str)
# 222 stub rows (ids > 94344, no body, no author, no timestamp) are dropped
C = C[C.created_at.notna() & C.body.notna()].copy()
C['uid'] = 'c' + C.id.astype(str)
P['kind'] = 'post'
C['kind'] = 'comment'
P['text_orig'] = (P.title.fillna('') + '\n' + P.body.fillna('')).str.strip()
C['text_orig'] = C.body.fillna('')
cols = ['uid', 'id', 'kind', 'author', 'author_model', 'created_at', 'mod_state', 'votes', 'text_orig']
M = pd.concat([P[cols + ['title', 'comments_total']], C[cols + ['post_id', 'parent_id', 'depth']]], ignore_index=True)
M['handle'] = M.author
M['t'] = pd.to_datetime(M.created_at, unit='ms', utc=True)
M['day'] = M.t.dt.strftime('%Y-%m-%d')
M['dayn'] = ((M.t.dt.normalize() - START).dt.days).astype(int)
M['week'] = M.dayn // 7
M['family'] = M.author_model.map(family)
M['disp'] = M.text_orig.map(strip_for_display)
M['nwords'] = M.disp.str.split().str.len().fillna(0).astype(int)
M['clean'] = M.text_orig.map(clean_for_model)
M['ntok'] = M.clean.str.split().str.len().fillna(0).astype(int)
M['short'] = M.nwords < 20
M['dup'] = M.duplicated('clean', keep=False) & (M.ntok > 0)
M = M.sort_values('t').reset_index(drop=True)
M.to_pickle(os.path.join(CACHE, 'M.pkl'))

rows = []
for name, d in [('posts', M[M.kind == 'post']), ('comments', M[M.kind == 'comment']), ('all', M)]:
    rows.append(dict(set=name, n=len(d), under20_words=int(d.short.sum()), under20_share=round(d.short.mean(), 4),
                     under5_tokens=int((d.ntok < 5).sum()), under5_tokens_share=round((d.ntok < 5).mean(), 4),
                     median_words=float(d.nwords.median()), mean_words=round(d.nwords.mean(), 1),
                     exact_dup_clean_share=round(d.dup.mean(), 4), handles=d.handle.nunique(),
                     first_day=d.day.min(), last_day=d.day.max()))
pd.DataFrame(rows).to_csv(os.path.join(OUT, 'sampling_summary.csv'), index=False)
print(pd.DataFrame(rows).T)
