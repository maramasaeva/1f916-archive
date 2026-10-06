"""Shared loaders for the economy analysis. Reads ~/1f916-archive/data only; no network."""
import gzip, glob, json, os, re, datetime as dt
from pathlib import Path
import pandas as pd, numpy as np

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
OUT = Path(__file__).resolve().parent
CSV = OUT / "csv"
FIG = OUT / "figures"
CSV.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)

USDC_ATOMIC = 1_000_000
CRAWL_END = dt.datetime(2026, 10, 6, 0, 56, tzinfo=dt.timezone.utc)
ADDR_RE = re.compile(r"0x[0-9a-fA-F]{8,}|\b[1-9A-HJ-NP-Za-km-z]{28,}\b|\b[0-9a-f]{40,}\b")
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")


def rd(sub):
    out = []
    for f in sorted(glob.glob(str(DATA / sub / "*.gz"))):
        with gzip.open(f, "rt") as fh:
            for l in fh:
                out.append(json.loads(l))
    return out


def site(name):
    return json.load(open(DATA / "site" / name))


def ts(ms):
    """ms epoch -> aware UTC datetime (None safe)"""
    if ms is None or (isinstance(ms, float) and np.isnan(ms)):
        return pd.NaT
    return pd.Timestamp(ms, unit="ms", tz="UTC")


def day(ms):
    t = ts(ms)
    return None if pd.isna(t) else t.strftime("%Y-%m-%d")


def usdc(atomic):
    return None if atomic in (None, "") else int(atomic) / USDC_ATOMIC


def gini(x):
    x = np.sort(np.asarray(x, dtype=float))
    x = x[x >= 0]
    if len(x) == 0 or x.sum() == 0:
        return float("nan")
    n = len(x)
    cum = np.cumsum(x)
    return float((n + 1 - 2 * (cum / cum[-1]).sum()) / n)


def topk_share(x, k=3):
    x = np.sort(np.asarray(x, dtype=float))[::-1]
    return float(x[:k].sum() / x.sum()) if x.sum() > 0 else float("nan")


def deciles(x):
    x = np.asarray(x, dtype=float)
    return {f"p{p}": float(np.percentile(x, p)) for p in range(10, 100, 10)}


def safe_text(s):
    """strip anything address- or email-like from text that is written to outputs"""
    s = ADDR_RE.sub("[addr]", s or "")
    s = EMAIL_RE.sub("[email]", s)
    return s


def usd_token_kind(token, usdc_token):
    return "USDC" if token == usdc_token else "1F916"


def save_csv(df, name):
    df.to_csv(CSV / name, index=False)
    return CSV / name


def load_numbers():
    p = OUT / "numbers.json"
    return json.load(open(p)) if p.exists() else {}


def save_numbers(d):
    cur = load_numbers(); cur.update(d)
    json.dump(cur, open(OUT / "numbers.json", "w"), indent=1, default=str)
