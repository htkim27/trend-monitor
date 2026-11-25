#!/usr/bin/env python3
"""RoboSpine Trend Monitor CLI (vt.py).

Deterministic pipeline for collecting, deduplicating, prefiltering, merging,
accumulating, trend-computing, rendering, and publishing to Google Workspace.
Semantic classification and editorial writing are performed by Gemini.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import html
import json
import os
import re
import sys
import time
import unicodedata
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import feedparser
import requests
import yaml
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"
STATE_DIR = ROOT / "state"
ARCHIVE_DIR = ROOT / "archive"
TRENDS_DIR = ROOT / "trends"
SITE_DIR = ROOT / "site"

KST = dt.timezone(dt.timedelta(hours=9))


# ── Helpers ──────────────────────────────────────────────────────────────────

def now_kst() -> dt.datetime:
    return dt.datetime.now(KST)


def iso_kst(d: dt.datetime) -> str:
    return d.astimezone(KST).replace(microsecond=0).isoformat()


def parse_dt(val: Any) -> Optional[dt.datetime]:
    if not val:
        return None
    if isinstance(val, dt.datetime):
        return val.astimezone(KST) if val.tzinfo else val.replace(tzinfo=KST)
    if isinstance(val, time.struct_time):
        return dt.datetime(*val[:6], tzinfo=dt.timezone.utc).astimezone(KST)
    s = str(val).strip()
    if not s:
        return None
    # ISO 8601
    try:
        iso = s.replace("Z", "+00:00")
        d = dt.datetime.fromisoformat(iso)
        return d.astimezone(KST) if d.tzinfo else d.replace(tzinfo=KST)
    except ValueError:
        pass
    # RFC 2822 / feedparser fallback
    parsed = feedparser._parse_date(s)
    if parsed:
        return dt.datetime(*parsed[:6], tzinfo=dt.timezone.utc).astimezone(KST)
    # YYYY-MM-DD
    m = re.match(r"^(\d{4}-\d{2}-\d{2})", s)
    if m:
        try:
            return dt.datetime.strptime(m.group(1), "%Y-%m-%d").replace(tzinfo=KST)
        except ValueError:
            pass
    return None


def load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def save_yaml(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False, width=120)


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def save_jsonl(path: Path, rows: Sequence[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def append_jsonl(path: Path, rows: Sequence[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def normalize_url(url: str) -> str:
    url = (url or "").strip()
    if not url:
        return ""
    p = urllib.parse.urlsplit(url)
    host = (p.netloc or "").lower()
    qs = urllib.parse.parse_qsl(p.query, keep_blank_values=True)
    filtered_qs = [
        (k, v)
        for k, v in qs
        if not k.lower().startswith("utm_")
        and k.lower() not in ("ref", "fbclid", "gclid", "mc_cid", "mc_eid")
    ]
    new_query = urllib.parse.urlencode(filtered_qs)
    path = p.path.rstrip("/") or "/"
    return urllib.parse.urlunsplit((p.scheme.lower() or "https", host, path, new_query, ""))


def url_id(url: str) -> str:
    return hashlib.sha1(normalize_url(url).encode("utf-8")).hexdigest()[:16]


def detect_lang(text: str) -> str:
    if not text:
        return "en"
    ko_chars = len(re.findall(r"[가-힣]", text))
    if ko_chars >= 3 or (len(text) > 0 and ko_chars / max(len(text), 1) > 0.1):
        return "ko"
    zh_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
    if zh_chars >= 3:
        return "zh"
    return "en"


def strip_html(text: str) -> str:
    if not text:
        return ""
    if "<" in text and ">" in text:
        text = BeautifulSoup(text, "html.parser").get_text(" ", strip=True)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def title_simhash(title: str) -> int:
    norm = unicodedata.normalize("NFKC", (title or "").lower())
    tokens = re.findall(r"[\w가-힣]+", norm)
    if not tokens:
        return 0
    v = [0] * 64
    for tok in tokens:
        h = int(hashlib.md5(tok.encode("utf-8")).hexdigest()[:16], 16)
        for i in range(64):
            v[i] += 1 if (h & (1 << i)) else -1
    out = 0
    for i in range(64):
        if v[i] > 0:
            out |= 1 << i
    return out


def hamming64(a: int, b: int) -> int:
    return bin((a ^ b) & ((1 << 64) - 1)).count("1")


def get_nested(obj: Any, path: str) -> Any:
    if not path:
        return obj
    cur = obj
    for part in path.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return None
    return cur


def make_session(settings: Dict[str, Any]) -> requests.Session:
    s = requests.Session()
    s.headers.update(
        {
            "User-Agent": settings.get("user_agent", "RoboSpineTrendMonitor/0.1"),
            "Accept": "application/rss+xml, application/atom+xml, application/xml, application/json, text/xml, text/html;q=0.9, */*;q=0.8",
        }
    )
    return s


def http_get(
    session: requests.Session,
    url: str,
    timeout: int = 15,
    extra_headers: Optional[Dict[str, str]] = None,
    retry_sec: int = 90,
    retry_max: int = 300,
    allow_retry: bool = True,
) -> requests.Response:
    headers = dict(extra_headers or {})
    resp = session.get(url, timeout=timeout, headers=headers)
    if resp.status_code in (403, 429) and allow_retry:
        ra = resp.headers.get("Retry-After")
        wait = retry_sec
        if ra and ra.isdigit():
            wait = min(int(ra), retry_max)
        wait = min(wait, retry_max)
        # In interactive/check mode keep wait bounded if caller passed small retry_sec
        if wait > 0:
            time.sleep(wait)
            resp = session.get(url, timeout=timeout, headers=headers)
    return resp


# ── Fetchers ─────────────────────────────────────────────────────────────────

def fetch_rss_atom(
    session: requests.Session,
    src: Dict[str, Any],
    health: Dict[str, Any],
    timeout: int,
    max_items: int,
    allow_retry: bool = True,
    retry_sec: int = 90,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    headers: Dict[str, str] = {}
    if health.get("etag"):
        headers["If-None-Match"] = health["etag"]
    if health.get("last_modified"):
        headers["If-Modified-Since"] = health["last_modified"]
    resp = http_get(session, src["url"], timeout=timeout, extra_headers=headers, allow_retry=allow_retry, retry_sec=retry_sec)
    if resp.status_code == 304:
        return [], {"status_code": 304}
    resp.raise_for_status()
    meta = {
        "status_code": resp.status_code,
        "etag": resp.headers.get("ETag"),
        "last_modified": resp.headers.get("Last-Modified"),
    }
    parsed = feedparser.parse(resp.content)
    items: List[Dict[str, Any]] = []
    for e in (parsed.entries or [])[:max_items]:
        link = e.get("link") or ""
        if not link and e.get("links"):
            link = e["links"][0].get("href", "")
        title = strip_html(e.get("title") or "")
        summary = strip_html(e.get("summary") or e.get("description") or "")[:600]
        pub = (
            parse_dt(e.get("published_parsed"))
            or parse_dt(e.get("updated_parsed"))
            or parse_dt(e.get("published"))
            or parse_dt(e.get("updated"))
        )
        if not link or not title:
            continue
        items.append(
            {
                "url": link,
                "title": title,
                "summary": summary,
                "published_at": iso_kst(pub) if pub else None,
                "kind": "article",
                "raw": {},
            }
        )
    return items, meta


def _parse_sitemap_xml(content: bytes) -> Tuple[List[str], List[Tuple[str, Optional[str]]]]:
    root = ET.fromstring(content)
    tag = root.tag.lower()
    sub_sitemaps: List[str] = []
    urls: List[Tuple[str, Optional[str]]] = []
    if tag.endswith("sitemapindex"):
        for sm in root:
            loc = None
            for child in sm:
                if child.tag.lower().endswith("loc") and child.text:
                    loc = child.text.strip()
            if loc:
                sub_sitemaps.append(loc)
    else:
        for u in root:
            loc = None
            lastmod = None
            for child in u:
                if child.tag.lower().endswith("loc") and child.text:
                    loc = child.text.strip()
                elif child.tag.lower().endswith("lastmod") and child.text:
                    lastmod = child.text.strip()
            if loc:
                urls.append((loc, lastmod))
    return sub_sitemaps, urls


def _fetch_page_meta(session: requests.Session, url: str, timeout: int) -> Tuple[str, str, Optional[str]]:
    slug = urllib.parse.urlsplit(url).path.rstrip("/").split("/")[-1].replace("-", " ").strip() or url
    try:
        r = session.get(url, timeout=timeout)
        if r.status_code != 200:
            return slug, "", None
        soup = BeautifulSoup(r.text, "html.parser")
        og = soup.find("meta", property="og:title")
        title = (og.get("content") if og else None) or (soup.title.string if soup.title and soup.title.string else slug)
        desc_tag = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", property="og:description")
        desc = desc_tag.get("content", "") if desc_tag else ""
        pub_tag = soup.find("meta", property="article:published_time") or soup.find("time")
        pub = None
        if pub_tag:
            pub = pub_tag.get("content") or pub_tag.get("datetime")
        return strip_html(str(title)) or slug, strip_html(str(desc))[:600], pub
    except Exception:
        return slug, "", None


def fetch_sitemap(
    session: requests.Session,
    src: Dict[str, Any],
    timeout: int,
    max_items: int,
    check_only: bool = False,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    resp = http_get(session, src["url"], timeout=timeout, allow_retry=not check_only)
    resp.raise_for_status()
    sub_sitemaps, url_pairs = _parse_sitemap_xml(resp.content)
    for sub in sub_sitemaps[:5]:
        try:
            sr = session.get(sub, timeout=timeout)
            if sr.status_code == 200:
                _, more = _parse_sitemap_xml(sr.content)
                url_pairs.extend(more)
        except Exception:
            continue
    extract = src.get("extract") or {}
    include_paths = extract.get("include_paths") or []
    matched: List[Tuple[str, Optional[str]]] = []
    for u, lm in url_pairs:
        path = urllib.parse.urlsplit(u).path
        if not include_paths or any(path.startswith(p) for p in include_paths):
            matched.append((u, lm))

    if check_only:
        sample = [
            {"url": u, "title": urllib.parse.urlsplit(u).path.rstrip("/").split("/")[-1], "summary": "", "published_at": lm, "kind": "article", "raw": {}}
            for u, lm in matched[:max_items]
        ]
        return sample, {"status_code": resp.status_code, "total_matched": len(matched)}

    snap_path = STATE_DIR / "snapshots" / f"{src['id']}.json"
    prev_urls = set(load_json(snap_path, {}).get("urls", []))
    cur_urls = [u for u, _ in matched]
    save_json(snap_path, {"updated_at": iso_kst(now_kst()), "urls": cur_urls})

    if not prev_urls:
        # First collection stores baseline only!
        return [], {"status_code": resp.status_code, "baseline_saved": len(cur_urls)}

    new_pairs = [(u, lm) for u, lm in matched if u not in prev_urls][:max_items]
    items: List[Dict[str, Any]] = []
    for u, lm in new_pairs:
        title, desc, page_pub = _fetch_page_meta(session, u, timeout)
        pub_dt = parse_dt(page_pub) or parse_dt(lm) or now_kst()
        items.append(
            {
                "url": u,
                "title": title,
                "summary": desc,
                "published_at": iso_kst(pub_dt),
                "kind": "article",
                "raw": {},
            }
        )
    return items, {"status_code": resp.status_code, "new_urls": len(new_pairs)}


def fetch_json_list(
    session: requests.Session,
    src: Dict[str, Any],
    timeout: int,
    max_items: int,
    allow_retry: bool = True,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    headers = {"Accept": "application/json"}
    if "api.github.com" in src["url"] and os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    resp = http_get(session, src["url"], timeout=timeout, extra_headers=headers, allow_retry=allow_retry)
    resp.raise_for_status()
    data = resp.json()
    ex = src.get("extract") or {}
    items_path = ex.get("items_path", "")
    arr = get_nested(data, items_path) if items_path else data
    if not isinstance(arr, list):
        arr = []
    out: List[Dict[str, Any]] = []
    for row in arr[:max_items]:
        if not isinstance(row, dict):
            continue
        title = str(get_nested(row, ex.get("title_field", "title")) or "").strip()
        summary = strip_html(str(get_nested(row, ex.get("summary_field", "summary")) or ""))[:600]
        url = str(get_nested(row, ex.get("url_field", "url")) or "").strip()
        if not url and ex.get("url_template"):
            try:
                url = ex["url_template"].format(**row)
            except Exception:
                url = ""
        pub = parse_dt(get_nested(row, ex.get("published_field", "published_at")))
        if not url or not title:
            continue
        # Enrich GitHub repo summary with stars/language/topics if present
        if "api.github.com" in src["url"]:
            stars = row.get("stargazers_count")
            lang = row.get("language")
            topics = row.get("topics") or []
            extras = []
            if stars is not None:
                extras.append(f"★{stars}")
            if lang:
                extras.append(str(lang))
            if topics:
                extras.append("topics:" + ",".join(topics[:5]))
            if extras:
                summary = (summary + " | " if summary else "") + " ".join(extras)
        out.append(
            {
                "url": url,
                "title": title,
                "summary": summary[:600],
                "published_at": iso_kst(pub) if pub else None,
                "kind": "article",
                "raw": {},
            }
        )
    return out, {"status_code": resp.status_code}


def fetch_json_catalog(
    session: requests.Session,
    src: Dict[str, Any],
    timeout: int,
    check_only: bool = False,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    resp = http_get(session, src["url"], timeout=timeout, allow_retry=not check_only)
    resp.raise_for_status()
    data = resp.json()
    ex = src.get("extract") or {}
    arr = get_nested(data, ex.get("items_path", "data")) or []
    key_field = ex.get("key_field", "id")
    title_field = ex.get("title_field", "name")
    url_template = ex.get("url_template", "{id}")
    watch_fields = ex.get("watch_fields") or []
    ignore_fields = set(ex.get("ignore_fields") or [])
    drop_prefixes = tuple(ex.get("drop_key_prefixes") or [])
    drop_suffixes = tuple(ex.get("drop_key_suffixes") or [])
    min_rel = float(ex.get("min_relative_change", 0.10))
    promote_rel = float(ex.get("promote_min_relative_change", 0.20))
    open_w_field = ex.get("open_weights_field")

    cur_map: Dict[str, Dict[str, Any]] = {}
    for row in arr:
        if not isinstance(row, dict):
            continue
        k = str(get_nested(row, key_field) or "")
        if not k or k.startswith(drop_prefixes) or k.endswith(drop_suffixes):
            continue
        cur_map[k] = {
            "title": str(get_nested(row, title_field) or k),
            "open_weights": bool(get_nested(row, open_w_field)) if open_w_field else False,
            "fields": {wf: get_nested(row, wf) for wf in watch_fields},
        }

    if check_only:
        sample = [
            {"url": url_template.format(id=k), "title": v["title"], "summary": "", "published_at": iso_kst(now_kst()), "kind": "catalog_change", "raw": {}}
            for k, v in list(cur_map.items())[:20]
        ]
        return sample, {"status_code": resp.status_code, "catalog_size": len(cur_map)}

    snap_path = STATE_DIR / "snapshots" / f"{src['id']}.json"
    prev_map = load_json(snap_path, {}).get("items", {})
    save_json(snap_path, {"updated_at": iso_kst(now_kst()), "items": cur_map})
    if not prev_map:
        return [], {"status_code": resp.status_code, "baseline_saved": len(cur_map)}

    items: List[Dict[str, Any]] = []
    now_iso = iso_kst(now_kst())
    for k, v in cur_map.items():
        if k not in prev_map:
            items.append(
                {
                    "url": url_template.format(id=k),
                    "title": f"[Catalog Added] {v['title']} ({k})",
                    "summary": ", ".join(f"{f}: {val}" for f, val in v["fields"].items() if val is not None)[:600],
                    "published_at": now_iso,
                    "kind": "catalog_change",
                    "raw": {"change": "added", "promote": True, "open_weights": v["open_weights"]},
                }
            )
            continue
        old = prev_map[k]["fields"]
        diffs = []
        non_ignore_diffs = []
        max_rel = 0.0
        has_non_numeric = False
        for wf in watch_fields:
            a, b = old.get(wf), v["fields"].get(wf)
            if a == b:
                continue
            diffs.append((wf, a, b))
            if wf not in ignore_fields:
                non_ignore_diffs.append((wf, a, b))
                try:
                    fa, fb = float(a), float(b)
                    if fa != 0:
                        max_rel = max(max_rel, abs(fb - fa) / abs(fa))
                    else:
                        has_non_numeric = True
                except (TypeError, ValueError):
                    has_non_numeric = True
        if not non_ignore_diffs:
            continue
        if not has_non_numeric and max_rel < min_rel:
            continue
        promote = (not v["open_weights"]) and (has_non_numeric or max_rel >= promote_rel)
        items.append(
            {
                "url": url_template.format(id=k),
                "title": f"[Catalog Modified] {v['title']} ({k})",
                "summary": "; ".join(f"{wf}: {a} -> {b}" for wf, a, b in non_ignore_diffs)[:600],
                "published_at": now_iso,
                "kind": "catalog_change",
                "raw": {"change": "modified", "promote": promote, "open_weights": v["open_weights"]},
            }
        )
    for k, oldv in prev_map.items():
        if k not in cur_map:
            items.append(
                {
                    "url": url_template.format(id=k),
                    "title": f"[Catalog Removed] {oldv['title']} ({k})",
                    "summary": f"Removed from catalog: {k}",
                    "published_at": now_iso,
                    "kind": "catalog_change",
                    "raw": {"change": "removed", "promote": False},
                }
            )
    return items, {"status_code": resp.status_code, "changes": len(items)}


def fetch_html_list(
    session: requests.Session,
    src: Dict[str, Any],
    timeout: int,
    max_items: int,
    check_only: bool = False,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    resp = http_get(session, src["url"], timeout=timeout, allow_retry=not check_only)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    sel = (src.get("extract") or {}).get("item_selector", "a[href]")
    found: List[Tuple[str, str]] = []
    seen_u = set()
    for a in soup.select(sel):
        href = a.get("href")
        if not href:
            continue
        full = urllib.parse.urljoin(src["url"], href)
        if full in seen_u:
            continue
        seen_u.add(full)
        found.append((full, strip_html(a.get_text(" ", strip=True)) or full))
    if check_only:
        return [
            {"url": u, "title": t, "summary": "", "published_at": None, "kind": "article", "raw": {}}
            for u, t in found[:max_items]
        ], {"status_code": resp.status_code}
    snap_path = STATE_DIR / "snapshots" / f"{src['id']}.json"
    prev_urls = set(load_json(snap_path, {}).get("urls", []))
    save_json(snap_path, {"updated_at": iso_kst(now_kst()), "urls": [u for u, _ in found]})
    if not prev_urls:
        return [], {"status_code": resp.status_code, "baseline_saved": len(found)}
    new_items = [
        {"url": u, "title": t, "summary": "", "published_at": iso_kst(now_kst()), "kind": "article", "raw": {}}
        for u, t in found
        if u not in prev_urls
    ][:max_items]
    return new_items, {"status_code": resp.status_code}


def fetch_source(
    session: requests.Session,
    src: Dict[str, Any],
    health: Dict[str, Any],
    settings: Dict[str, Any],
    defaults: Dict[str, Any],
    check_only: bool = False,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    timeout = int(src.get("timeout_sec") or defaults.get("timeout_sec", 15))
    max_items = int(src.get("max_items_per_fetch") or defaults.get("max_items_per_fetch", 40))
    retry_sec = 0 if check_only else int(settings.get("retry_on_block_sec", 90))
    stype = src.get("type", "rss")
    if stype in ("rss", "atom"):
        return fetch_rss_atom(session, src, health if not check_only else {}, timeout, max_items, allow_retry=not check_only, retry_sec=retry_sec)
    if stype == "sitemap":
        return fetch_sitemap(session, src, timeout, max_items, check_only=check_only)
    if stype == "json_list":
        return fetch_json_list(session, src, timeout, max_items, allow_retry=not check_only)
    if stype == "json_catalog":
        return fetch_json_catalog(session, src, timeout, check_only=check_only)
    if stype == "html_list":
        return fetch_html_list(session, src, timeout, max_items, check_only=check_only)
    raise ValueError(f"Unsupported source type: {stype}")


# ── Command: source-check ────────────────────────────────────────────────────

def cmd_source_check(args: argparse.Namespace) -> int:
    settings = load_yaml(CONFIG_DIR / "settings.yaml")
    src_cfg = load_yaml(CONFIG_DIR / "sources.yaml")
    defaults = src_cfg.get("defaults") or {}
    sources = src_cfg.get("sources") or []
    if args.source:
        sources = [s for s in sources if s["id"] == args.source]
    session = make_session(settings)
    ok_cnt = 0
    fail_cnt = 0
    for src in sources:
        if not args.all and not args.source and src.get("status") not in ("active", "standby"):
            continue
        t0 = time.time()
        try:
            items, meta = fetch_source(session, src, {}, settings, defaults, check_only=True)
            dt_ms = int((time.time() - t0) * 1000)
            if len(items) > 0:
                ok_cnt += 1
                sample_t = items[0]["title"][:65]
                print(f"[PASS] {src['id']:24s} ({src['type']:12s}) n={len(items):3d} {dt_ms:4d}ms | {sample_t}")
            else:
                fail_cnt += 1
                print(f"[WARN] {src['id']:24s} ({src['type']:12s}) n=  0 {dt_ms:4d}ms | 0 items returned")
        except Exception as e:
            fail_cnt += 1
            dt_ms = int((time.time() - t0) * 1000)
            print(f"[FAIL] {src['id']:24s} ({src['type']:12s}) {dt_ms:4d}ms | {e}")
    print(f"\nSummary: {ok_cnt} passed, {fail_cnt} failed/empty")
    return 0 if fail_cnt == 0 else 1


# ── Command: collect ─────────────────────────────────────────────────────────

def cmd_collect(args: argparse.Namespace) -> int:
    settings = load_yaml(CONFIG_DIR / "settings.yaml")
    src_cfg = load_yaml(CONFIG_DIR / "sources.yaml")
    defaults = src_cfg.get("defaults") or {}
    sources = src_cfg.get("sources") or []
    src_by_id = {s["id"]: s for s in sources}

    seen_rows = load_jsonl(STATE_DIR / "seen.jsonl")
    pending_rows = load_jsonl(STATE_DIR / "pending.jsonl")
    health_all = load_json(STATE_DIR / "source_health.json", {})

    seen_ids = {r["id"] for r in seen_rows} | {r["id"] for r in pending_rows}
    seen_hashes: Dict[str, List[int]] = {}
    for r in seen_rows + pending_rows:
        lg = r.get("lang", "en")
        sh = r.get("title_simhash")
        if sh is None and r.get("title"):
            sh = title_simhash(r["title"])
        if sh is not None:
            seen_hashes.setdefault(lg, []).append(int(sh))

    sim_thresh = int(settings.get("simhash_hamming", 3))
    expire_days = int(settings.get("expire_after_days", 7))
    max_fails = int(settings.get("max_consecutive_failures", 10))
    now = now_kst()
    is_monday_am = now.weekday() == 0 and now.hour < 12
    include_standby = args.include_standby or is_monday_am

    session = make_session(settings)
    new_pending: List[Dict[str, Any]] = []
    expired_seen: List[Dict[str, Any]] = []
    stats = {"fetched": 0, "added": 0, "dup_id": 0, "dup_simhash": 0, "expired": 0, "failed_sources": []}

    target_sources = [
        s for s in sources
        if (args.source and s["id"] == args.source)
        or (not args.source and (s.get("status") == "active" or (include_standby and s.get("status") == "standby")))
    ]

    for src in target_sources:
        sid = src["id"]
        h = health_all.setdefault(sid, {"consecutive_failures": 0})
        try:
            raw_items, meta = fetch_source(session, src, h, settings, defaults, check_only=False)
            h["consecutive_failures"] = 0
            h["last_success_at"] = iso_kst(now)
            h["last_status"] = meta.get("status_code", 200)
            if meta.get("etag"):
                h["etag"] = meta["etag"]
            if meta.get("last_modified"):
                h["last_modified"] = meta["last_modified"]
        except Exception as e:
            h["consecutive_failures"] = int(h.get("consecutive_failures", 0)) + 1
            h["last_error"] = str(e)[:200]
            h["last_error_at"] = iso_kst(now)
            stats["failed_sources"].append({"id": sid, "error": str(e)[:120], "failures": h["consecutive_failures"]})
            # Try fallback if configured
            fb_id = src.get("fallback")
            raw_items = []
            if fb_id and fb_id in src_by_id:
                try:
                    raw_items, _ = fetch_source(session, src_by_id[fb_id], {}, settings, defaults, check_only=False)
                except Exception:
                    raw_items = []
            if h["consecutive_failures"] >= max_fails:
                h["auto_dormant_suggested"] = True

        stats["fetched"] += len(raw_items)
        for it in raw_items:
            norm_u = normalize_url(it["url"])
            if not norm_u:
                continue
            iid = url_id(norm_u)
            if iid in seen_ids:
                stats["dup_id"] += 1
                continue
            title = it["title"]
            lang = detect_lang(title + " " + it.get("summary", ""))
            sh = title_simhash(title)
            if any(hamming64(sh, old_sh) <= sim_thresh for old_sh in seen_hashes.get(lang, [])):
                stats["dup_simhash"] += 1
                continue

            pub_dt = parse_dt(it.get("published_at"))
            age_days = (now - pub_dt).total_seconds() / 86400.0 if pub_dt else 0.0
            is_primary = bool(src.get("primary", False))
            if pub_dt and age_days > expire_days and not (is_primary and age_days <= expire_days + 2):
                stats["expired"] += 1
                seen_ids.add(iid)
                expired_seen.append(
                    {"id": iid, "title_simhash": sh, "lang": lang, "source_id": sid, "first_seen": iso_kst(now), "expired": True}
                )
                continue

            seen_ids.add(iid)
            seen_hashes.setdefault(lang, []).append(sh)
            rec = {
                "id": iid,
                "source_id": sid,
                "channel": src.get("channel", "other"),
                "primary": is_primary,
                "url": norm_u,
                "title": title,
                "summary": (it.get("summary") or "")[:600],
                "lang": lang,
                "title_simhash": sh,
                "published_at": iso_kst(pub_dt) if pub_dt else iso_kst(now),
                "collected_at": iso_kst(now),
                "kind": it.get("kind", "article"),
                "keymap": {},
                "raw": it.get("raw") or {},
            }
            new_pending.append(rec)
            stats["added"] += 1

    if new_pending:
        append_jsonl(STATE_DIR / "pending.jsonl", new_pending)
    if expired_seen:
        append_jsonl(STATE_DIR / "seen.jsonl", expired_seen)
    save_json(STATE_DIR / "source_health.json", health_all)

    print(json.dumps(stats, ensure_ascii=False, indent=2))
    return 0


# ── Command: prefilter ───────────────────────────────────────────────────────

def normalize_match_text(text: str) -> str:
    t = unicodedata.normalize("NFKC", (text or "").lower())
    t = re.sub(r"[^\w\s.\-가-힣]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def alias_in_text(alias: str, norm_text: str, min_len: int = 3) -> bool:
    a = normalize_match_text(alias)
    if len(a) < min_len:
        return False
    # For Korean/CJK aliases, word boundaries are softer
    if re.search(r"[가-힣\u4e00-\u9fff]", a):
        return a in norm_text
    pattern = r"(?<![\w\-])" + re.escape(a) + r"(?![\w\-])"
    return bool(re.search(pattern, norm_text))


def prefilter_item(
    title: str,
    summary: str,
    interests: Dict[str, Any],
    keywords_cfg: Dict[str, Any],
) -> Dict[str, Any]:
    norm_text = normalize_match_text(f"{title} {summary}")
    min_len = int((interests.get("matching") or {}).get("min_alias_len", 3))

    # 1. Labs
    labs_hit: List[str] = []
    for lid, linfo in (interests.get("labs") or {}).items():
        for al in linfo.get("aliases") or []:
            if alias_in_text(al, norm_text, min_len=min_len):
                labs_hit.append(lid)
                break

    # 2. Direction signals
    dir_sigs = interests.get("direction_signals") or {}
    all_sigs = list(dir_sigs.get("en") or []) + list(dir_sigs.get("ko") or [])
    has_sig = any(alias_in_text(s, norm_text, min_len=2) for s in all_sigs)
    direction_signal = bool(labs_hit and has_sig)

    # 3. Entities + variants
    matched_entities: List[str] = []
    variants_hit: Dict[str, str] = {}
    for eid, einfo in (interests.get("entities") or {}).items():
        hit = False
        for vname, valiases in (einfo.get("variants") or {}).items():
            for va in valiases:
                if alias_in_text(va, norm_text, min_len=min_len):
                    hit = True
                    variants_hit[eid] = vname
                    break
            if hit:
                break
        if not hit:
            for al in einfo.get("aliases") or []:
                if alias_in_text(al, norm_text, min_len=min_len):
                    hit = True
                    break
        if hit:
            matched_entities.append(eid)

    # 4. Disambiguation rules
    ent_set = set(matched_entities)
    for rule in interests.get("disambiguation") or []:
        ent = rule.get("entity")
        if ent not in ent_set:
            continue
        if "require_any" in rule:
            reqs = rule["require_any"]
            if not any(alias_in_text(r, norm_text, min_len=2) for r in reqs):
                ent_set.discard(ent)
        elif "alt" in rule and "alt_if_any" in rule:
            alt = rule["alt"]
            if any(alias_in_text(w, norm_text, min_len=2) for w in rule["alt_if_any"]):
                ent_set.discard(ent)
                ent_set.add(alt)

    final_ents = sorted(ent_set)
    fixed = final_ents[0] if len(final_ents) == 1 else None
    candidates = final_ents if len(final_ents) > 1 else []

    # 5. User keywords
    kw_hits: List[str] = []
    for kw in keywords_cfg.get("keywords") or []:
        term = kw.get("term", "")
        aliases = [term] + list(kw.get("aliases") or [])
        if any(alias_in_text(a, norm_text, min_len=2) for a in aliases if a):
            reqs = kw.get("require_any") or []
            if not reqs or any(alias_in_text(r, norm_text, min_len=2) for r in reqs):
                kw_hits.append(term)

    return {
        "fixed": fixed,
        "candidates": candidates,
        "variant": variants_hit.get(fixed) if fixed else None,
        "labs": labs_hit,
        "direction_signal": direction_signal,
        "keywords": kw_hits,
    }


def cmd_prefilter(_args: argparse.Namespace) -> int:
    interests = load_yaml(CONFIG_DIR / "interests.yaml")
    keywords_cfg = load_yaml(CONFIG_DIR / "keywords.yaml")
    pending = load_jsonl(STATE_DIR / "pending.jsonl")
    fixed_cnt = 0
    cand_cnt = 0
    kw_cnt = 0
    for it in pending:
        km = prefilter_item(it.get("title", ""), it.get("summary", ""), interests, keywords_cfg)
        it["keymap"] = km
        if km["fixed"]:
            fixed_cnt += 1
        elif km["candidates"]:
            cand_cnt += 1
        if km["keywords"]:
            kw_cnt += 1
    save_jsonl(STATE_DIR / "pending.jsonl", pending)
    print(json.dumps({"total": len(pending), "fixed": fixed_cnt, "candidates": cand_cnt, "keyword_hits": kw_cnt}, ensure_ascii=False))
    return 0


# ── Command: merge-structural ────────────────────────────────────────────────

def cmd_merge_structural(args: argparse.Namespace) -> int:
    settings = load_yaml(CONFIG_DIR / "settings.yaml")
    window_h = float(settings.get("structural_window_h", 24))
    same_win_h = float(settings.get("same_event_window_h", 72))
    max_cands = int(settings.get("same_event_max_candidates", 8))
    min_sig = float(settings.get("discard_below_significance", 0.2))

    run_id = args.run_id
    classified = load_jsonl(STATE_DIR / "classified" / f"{run_id}.jsonl")
    pending_by_id = {r["id"]: r for r in load_jsonl(STATE_DIR / "pending.jsonl")}
    events = load_jsonl(STATE_DIR / "events.jsonl")

    clusters: List[Dict[str, Any]] = []
    for c in classified:
        if not c.get("relevant") or float(c.get("significance", 0)) < min_sig:
            continue
        item = pending_by_id.get(c["item_id"], {})
        pub_dt = parse_dt(item.get("published_at")) or now_kst()
        topic = c.get("entity_key") or (f"lab:{c['lab']}" if c.get("domain") == "direction" and c.get("lab") else None) or (
            (c.get("new_entity") or {}).get("key")
        ) or "unassigned"
        etype = c.get("event_type", "release")
        ver = c.get("version")

        merged = False
        for cl in clusters:
            if cl["topic"] == topic and cl["event_type"] == etype and cl["version"] == ver:
                cl_dt = parse_dt(cl["occurred_at"]) or pub_dt
                if abs((pub_dt - cl_dt).total_seconds()) <= window_h * 3600:
                    cl["items"].append(c)
                    if pub_dt < cl_dt:
                        cl["occurred_at"] = iso_kst(pub_dt)
                    merged = True
                    break
        if not merged:
            clusters.append(
                {
                    "cluster_id": f"{run_id}-{len(clusters)+1:03d}",
                    "topic": topic,
                    "domain": c.get("domain", "harnesses"),
                    "lab": c.get("lab"),
                    "event_type": etype,
                    "version": ver,
                    "occurred_at": iso_kst(pub_dt),
                    "items": [c],
                }
            )

    # Find semantic merge candidates in existing events
    review_needed = []
    for cl in clusters:
        cl_dt = parse_dt(cl["occurred_at"]) or now_kst()
        cands = []
        for ev in reversed(events):
            if ev.get("topic") != cl["topic"]:
                continue
            ev_dt = parse_dt(ev.get("occurred_at"))
            if ev_dt and abs((cl_dt - ev_dt).total_seconds()) <= same_win_h * 3600:
                cands.append({"event_id": ev["event_id"], "occurred_at": ev["occurred_at"], "headline_ko": ev.get("headline_ko", "")})
            if len(cands) >= max_cands:
                break
        cl["existing_candidates"] = cands
        if cands:
            review_needed.append({"cluster_id": cl["cluster_id"], "headline_ko": cl["items"][0].get("headline_ko", ""), "candidates": cands})

    out_path = STATE_DIR / "merges" / f"{run_id}_structural.json"
    save_json(out_path, {"run_id": run_id, "clusters": clusters})
    print(json.dumps({"run_id": run_id, "clusters": len(clusters), "semantic_review_needed": len(review_needed), "review": review_needed}, ensure_ascii=False, indent=2))
    return 0


# ── Command: accumulate ──────────────────────────────────────────────────────

def init_seed_topics(interests: Dict[str, Any], keywords_cfg: Dict[str, Any], topics: Dict[str, Any], now_iso: str) -> None:
    for eid, einfo in (interests.get("entities") or {}).items():
        if eid not in topics:
            topics[eid] = {
                "slug": eid,
                "title": einfo.get("title", eid),
                "domain": einfo.get("domain", "harnesses"),
                "origin": "seed",
                "state": "active",
                "created_at": now_iso,
                "last_update_at": now_iso,
                "status_ko": "",
            }
    for lid, linfo in (interests.get("labs") or {}).items():
        slug = f"lab:{lid}"
        if slug not in topics:
            topics[slug] = {
                "slug": slug,
                "title": linfo.get("title", lid),
                "domain": "embodied_models",
                "origin": "seed",
                "state": "active",
                "created_at": now_iso,
                "last_update_at": now_iso,
                "status_ko": "",
            }
    for kw in keywords_cfg.get("keywords") or []:
        if not kw.get("promote"):
            continue
        slug = "kw:" + re.sub(r"[^a-z0-9]+", "-", kw["term"].lower()).strip("-")
        if slug not in topics:
            topics[slug] = {
                "slug": slug,
                "title": kw["term"],
                "domain": "harnesses",
                "origin": "keyword",
                "state": "active",
                "created_at": now_iso,
                "last_update_at": now_iso,
                "status_ko": kw.get("note", ""),
            }


def has_consecutive_days(day_strs: Sequence[str], n: int = 2) -> bool:
    if len(day_strs) < n:
        return False
    days = sorted({dt.date.fromisoformat(d) for d in day_strs})
    streak = 1
    for i in range(1, len(days)):
        if (days[i] - days[i - 1]).days == 1:
            streak += 1
            if streak >= n:
                return True
        else:
            streak = 1
    return False


def cmd_accumulate(args: argparse.Namespace) -> int:
    settings = load_yaml(CONFIG_DIR / "settings.yaml")
    interests = load_yaml(CONFIG_DIR / "interests.yaml")
    keywords_cfg = load_yaml(CONFIG_DIR / "keywords.yaml")

    run_id = args.run_id
    now = now_kst()
    now_iso = iso_kst(now)
    today_str = now.date().isoformat()

    topics = load_json(STATE_DIR / "topics.json", {})
    init_seed_topics(interests, keywords_cfg, topics, now_iso)
    proposals = load_json(STATE_DIR / "proposals.json", {})
    events = load_jsonl(STATE_DIR / "events.jsonl")
    events_by_id = {e["event_id"]: e for e in events}
    pending_by_id = {r["id"]: r for r in load_jsonl(STATE_DIR / "pending.jsonl")}

    struct_data = load_json(STATE_DIR / "merges" / f"{run_id}_structural.json", {"clusters": []})
    # Optional semantic merge map: {"cluster_id": "existing_event_id"}
    sem_map = load_json(STATE_DIR / "merges" / f"{run_id}_semantic.json", {})

    updated_topics = set()
    new_events_cnt = 0
    merged_events_cnt = 0

    for cl in struct_data.get("clusters", []):
        cid = cl["cluster_id"]
        c_items = cl["items"]
        # Pick highest-significance item as primary headline/detail
        best = max(c_items, key=lambda x: (float(x.get("significance", 0)), bool(x.get("official", False))))
        item_ids = [x["item_id"] for x in c_items]
        source_ids = sorted({pending_by_id.get(iid, {}).get("source_id", "unknown") for iid in item_ids})
        urls = [pending_by_id.get(iid, {}).get("url", "") for iid in item_ids if pending_by_id.get(iid, {}).get("url")]
        sig = max(float(x.get("significance", 0)) for x in c_items)
        official = any(bool(x.get("official", False)) for x in c_items)
        kws = sorted({k for x in c_items for k in (x.get("keywords_hit") or [])})

        # Track new_entity proposals
        for x in c_items:
            ne = x.get("new_entity")
            if isinstance(ne, dict) and ne.get("key"):
                nk = ne["key"]
                if nk not in topics or topics[nk].get("state") != "removed":
                    p = proposals.setdefault(nk, {"key": nk, "title": ne.get("title", nk), "domain": ne.get("domain", "harnesses"), "days": []})
                    if today_str not in p["days"]:
                        p["days"].append(today_str)

        target_eid = sem_map.get(cid)
        if target_eid and target_eid in events_by_id:
            ev = events_by_id[target_eid]
            ev["item_ids"] = sorted(set(ev.get("item_ids", [])) | set(item_ids))
            ev["source_ids"] = sorted(set(ev.get("source_ids", [])) | set(source_ids))
            ev["urls"] = sorted(set(ev.get("urls", [])) | set(urls))
            ev["sources"] = len(ev["source_ids"])
            ev["significance"] = max(float(ev.get("significance", 0)), sig)
            ev["official"] = bool(ev.get("official", False) or official)
            ev["keywords_hit"] = sorted(set(ev.get("keywords_hit", [])) | set(kws))
            merged_events_cnt += 1
            topic = ev["topic"]
        else:
            eid = hashlib.sha1(f"{run_id}:{cid}:{cl['topic']}:{best.get('headline_ko', '')}".encode("utf-8")).hexdigest()[:12]
            ev = {
                "event_id": eid,
                "topic": cl["topic"],
                "domain": cl["domain"],
                "lab": cl.get("lab"),
                "event_type": cl["event_type"],
                "version": cl.get("version"),
                "significance": sig,
                "official": official,
                "occurred_at": cl["occurred_at"],
                "headline_ko": best.get("headline_ko", ""),
                "detail_ko": best.get("detail_ko", ""),
                "headline_en": best.get("headline_en", ""),
                "detail_en": best.get("detail_en", ""),
                "item_ids": item_ids,
                "source_ids": source_ids,
                "urls": urls,
                "sources": len(source_ids),
                "keywords_hit": kws,
                "run_id": run_id,
            }
            events.append(ev)
            events_by_id[eid] = ev
            new_events_cnt += 1
            topic = ev["topic"]

        if topic in topics and topics[topic].get("state") != "removed":
            topics[topic]["last_update_at"] = now_iso
            topics[topic]["state"] = "active"
            updated_topics.add(topic)

    # Auto-topic promotion from proposals
    lookback = int(settings.get("proposal_lookback_days", 7))
    consec = int(settings.get("proposal_consecutive_days", 2))
    max_per_week = int(settings.get("new_topics_per_week", 5))
    cutoff_date = (now - dt.timedelta(days=lookback)).date()

    # Count auto topics created in the last 7 days
    recent_auto = sum(
        1 for t in topics.values()
        if t.get("origin") == "auto" and parse_dt(t.get("created_at")) and (now - parse_dt(t["created_at"])).days < 7
    )
    promoted: List[str] = []
    for nk, p in list(proposals.items()):
        recent_days = [d for d in p.get("days", []) if dt.date.fromisoformat(d) >= cutoff_date]
        p["days"] = recent_days
        if nk in topics:
            continue
        if has_consecutive_days(recent_days, consec) and recent_auto < max_per_week:
            topics[nk] = {
                "slug": nk,
                "title": p.get("title", nk),
                "domain": p.get("domain", "harnesses"),
                "origin": "auto",
                "state": "active",
                "created_at": now_iso,
                "last_update_at": now_iso,
                "status_ko": "",
            }
            recent_auto += 1
            promoted.append(nk)

    # Lifecycle: archive after 3d, remove auto after 60d
    arch_days = int(settings.get("archive_after_days", 3))
    rem_days = int(settings.get("auto_topic_remove_after_days", 60))
    archived_now: List[str] = []
    removed_now: List[str] = []
    for slug, t in topics.items():
        if t.get("state") == "removed":
            continue
        lu = parse_dt(t.get("last_update_at")) or now
        idle = (now - lu).total_seconds() / 86400.0
        if t.get("origin") == "auto" and idle >= rem_days:
            t["state"] = "removed"
            removed_now.append(slug)
        elif t.get("state") == "active" and idle >= arch_days:
            t["state"] = "archived"
            archived_now.append(slug)

    save_jsonl(STATE_DIR / "events.jsonl", events)
    save_json(STATE_DIR / "topics.json", topics)
    save_json(STATE_DIR / "proposals.json", proposals)

    print(
        json.dumps(
            {
                "new_events": new_events_cnt,
                "merged_events": merged_events_cnt,
                "updated_topics": sorted(updated_topics),
                "promoted_topics": promoted,
                "archived_topics": archived_now,
                "removed_topics": removed_now,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


# ── Command: trends ──────────────────────────────────────────────────────────

def compute_momentum(
    cur_counts: Dict[str, int],
    base_counts: Dict[str, int],
    cfg: Dict[str, Any],
) -> Dict[str, Any]:
    min_excess = float(cfg.get("min_excess", 2))
    lift = float(cfg.get("lift", 0.10))
    min_count = int(cfg.get("min_count", 3))
    new_min = int(cfg.get("new_min", 2))

    cur_total = sum(cur_counts.values())
    base_total = sum(base_counts.values())
    surging, cooling, emerging = [], [], []

    all_topics = set(cur_counts) | set(base_counts)
    for t in all_topics:
        c = cur_counts.get(t, 0)
        b = base_counts.get(t, 0)
        if b == 0 and c >= new_min:
            emerging.append({"topic": t, "actual": c})
            continue
        if c < min_count and b < min_count:
            continue
        if cur_total == 0 or base_total == 0:
            continue
        b_share = b / base_total
        c_share = c / cur_total
        expected = b_share * cur_total
        excess = c - expected
        share_diff = c_share - b_share
        if excess >= min_excess and share_diff >= lift:
            surging.append({"topic": t, "actual": c, "expected": round(expected, 2), "excess": round(excess, 2), "share_diff": round(share_diff, 3)})
        elif excess <= -min_excess and share_diff <= -lift:
            cooling.append({"topic": t, "actual": c, "expected": round(expected, 2), "excess": round(excess, 2), "share_diff": round(share_diff, 3)})

    surging.sort(key=lambda x: x["excess"], reverse=True)
    cooling.sort(key=lambda x: x["excess"])
    emerging.sort(key=lambda x: x["actual"], reverse=True)
    return {"surging": surging, "cooling": cooling, "emerging": emerging}


def cmd_trends(_args: argparse.Namespace) -> int:
    settings = load_yaml(CONFIG_DIR / "settings.yaml")
    recompute_days = int(settings.get("trend_recompute_days", 35))
    mom_cfg = settings.get("momentum") or {}

    now = now_kst()
    cutoff_recompute = (now - dt.timedelta(days=recompute_days)).date()

    # Keep frozen rows older than recompute_days
    csv_path = STATE_DIR / "trend_daily.csv"
    frozen_rows: List[Tuple[str, str, str, int]] = []
    if csv_path.exists():
        with csv_path.open("r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                try:
                    d = dt.date.fromisoformat(row["day"])
                    if d < cutoff_recompute:
                        frozen_rows.append((row["day"], row["topic"], row["domain"], int(row["updates"])))
                except Exception:
                    continue

    events = load_jsonl(STATE_DIR / "events.jsonl")
    daily: Dict[Tuple[str, str, str], int] = {}
    cur_24h: Dict[str, int] = {}
    base_7d: Dict[str, int] = {}
    domain_7d: Dict[str, int] = {}

    for ev in events:
        ev_dt = parse_dt(ev.get("occurred_at"))
        if not ev_dt:
            continue
        day_d = ev_dt.date()
        topic = ev.get("topic", "unassigned")
        domain = ev.get("domain", "harnesses")
        if day_d >= cutoff_recompute:
            key = (day_d.isoformat(), topic, domain)
            daily[key] = daily.get(key, 0) + 1
        age_h = (now - ev_dt).total_seconds() / 3600.0
        if 0 <= age_h <= 24:
            cur_24h[topic] = cur_24h.get(topic, 0) + 1
        elif 24 < age_h <= 24 * 8:
            base_7d[topic] = base_7d.get(topic, 0) + 1
        if 0 <= age_h <= 24 * 7:
            domain_7d[domain] = domain_7d.get(domain, 0) + 1

    all_rows = frozen_rows + [(k[0], k[1], k[2], v) for k, v in sorted(daily.items())]
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["day", "topic", "domain", "updates"])
        w.writerows(all_rows)

    tot_dom = sum(domain_7d.values()) or 1
    domain_share = {k: round(v / tot_dom, 3) for k, v in sorted(domain_7d.items())}
    mom = compute_momentum(cur_24h, base_7d, mom_cfg)
    out = {"momentum_24h_vs_7d": mom, "domain_share_7d": domain_share, "events_7d": sum(domain_7d.values())}
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


# ── Command: finalize ────────────────────────────────────────────────────────

def cmd_finalize(args: argparse.Namespace) -> int:
    run_id = args.run_id
    now_iso = iso_kst(now_kst())
    classified = load_jsonl(STATE_DIR / "classified" / f"{run_id}.jsonl")
    done_ids = {c["item_id"] for c in classified}
    pending = load_jsonl(STATE_DIR / "pending.jsonl")

    remaining = []
    moved = []
    for it in pending:
        if it["id"] in done_ids:
            moved.append(
                {
                    "id": it["id"],
                    "title_simhash": it.get("title_simhash") or title_simhash(it.get("title", "")),
                    "lang": it.get("lang", "en"),
                    "source_id": it.get("source_id", ""),
                    "first_seen": it.get("collected_at", now_iso),
                }
            )
        else:
            remaining.append(it)

    save_jsonl(STATE_DIR / "pending.jsonl", remaining)
    if moved:
        append_jsonl(STATE_DIR / "seen.jsonl", moved)

    rel_cnt = sum(1 for c in classified if c.get("relevant"))
    disc_cnt = len(classified) - rel_cnt
    append_jsonl(
        STATE_DIR / "runs.jsonl",
        [
            {
                "run_id": run_id,
                "finished_at": now_iso,
                "processed": len(done_ids),
                "relevant": rel_cnt,
                "discarded": disc_cnt,
                "remaining_pending": len(remaining),
            }
        ],
    )
    print(json.dumps({"run_id": run_id, "moved_to_seen": len(moved), "remaining_pending": len(remaining)}, ensure_ascii=False))
    return 0


# ── Command: profile ─────────────────────────────────────────────────────────

def cmd_profile(args: argparse.Namespace) -> int:
    settings = load_yaml(CONFIG_DIR / "settings.yaml")
    interests = load_yaml(CONFIG_DIR / "interests.yaml")
    keywords_cfg = load_yaml(CONFIG_DIR / "keywords.yaml")
    src_cfg = load_yaml(CONFIG_DIR / "sources.yaml")
    defaults = src_cfg.get("defaults") or {}
    prof_cfg = settings.get("profile") or {}
    sample_n = int(prof_cfg.get("sample_n", 40))
    active_min = float(prof_cfg.get("active_min", 0.25))
    standby_min = float(prof_cfg.get("standby_min", 0.10))

    session = make_session(settings)
    health_all = load_json(STATE_DIR / "source_health.json", {})
    results = []
    for src in src_cfg.get("sources") or []:
        if src.get("primary") or src.get("status") == "fallback":
            continue
        try:
            items, _ = fetch_source(session, src, {}, settings, defaults, check_only=True)
            items = items[:sample_n]
            if not items:
                continue
            hits = 0
            for it in items:
                km = prefilter_item(it.get("title", ""), it.get("summary", ""), interests, keywords_cfg)
                if km["fixed"] or km["candidates"] or km["direction_signal"] or km["keywords"]:
                    hits += 1
            rate = round(hits / len(items), 3)
            rec_status = "active" if rate >= active_min else ("standby" if rate >= standby_min else "dormant")
            results.append({"id": src["id"], "current": src.get("status"), "recommended": rec_status, "hit_rate": rate, "sample": len(items)})
            health_all.setdefault(src["id"], {})["last_hit_rate"] = rate
            if args.apply:
                src["status"] = rec_status
        except Exception as e:
            results.append({"id": src["id"], "error": str(e)[:100]})
    save_json(STATE_DIR / "source_health.json", health_all)
    if args.apply:
        save_yaml(CONFIG_DIR / "sources.yaml", src_cfg)
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


# ── Command: status ──────────────────────────────────────────────────────────

def cmd_status(_args: argparse.Namespace) -> int:
    src_cfg = load_yaml(CONFIG_DIR / "sources.yaml")
    health = load_json(STATE_DIR / "source_health.json", {})
    pending = load_jsonl(STATE_DIR / "pending.jsonl")
    events = load_jsonl(STATE_DIR / "events.jsonl")
    topics = load_json(STATE_DIR / "topics.json", {})
    runs = load_jsonl(STATE_DIR / "runs.jsonl")

    active_t = sum(1 for t in topics.values() if t.get("state") == "active")
    print(f"Pending: {len(pending)} | Events: {len(events)} | Active Topics: {active_t} | Runs: {len(runs)}")
    if runs:
        print(f"Last run: {runs[-1]['run_id']} ({runs[-1].get('finished_at')})")
    print("\n| Source | Type | Status | Fails | Hit% |")
    print("|---|---|---|---|---|")
    for s in src_cfg.get("sources") or []:
        h = health.get(s["id"], {})
        hr = h.get("last_hit_rate")
        hr_s = f"{hr*100:.0f}%" if isinstance(hr, (int, float)) else ("1차" if s.get("primary") else "-")
        print(f"| {s['id']} | {s['type']} | {s.get('status')} | {h.get('consecutive_failures', 0)} | {hr_s} |")
    return 0


# ── Command: render-page ─────────────────────────────────────────────────────

def md_to_simple_html(md_text: str) -> str:
    lines = md_text.splitlines()
    out: List[str] = []
    in_ul = False
    in_table = False

    def inline_fmt(s: str) -> str:
        s = html.escape(s)
        s = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', s)
        s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
        return s

    for line in lines:
        st = line.strip()
        if not st:
            if in_ul:
                out.append("</ul>")
                in_ul = False
            if in_table:
                out.append("</tbody></table></div>")
                in_table = False
            continue
        if st.startswith("|") and st.endswith("|"):
            cells = [c.strip() for c in st.strip("|").split("|")]
            if all(re.match(r"^-+$", c.replace(":", "")) for c in cells):
                continue
            if not in_table:
                out.append('<div class="tbl-wrap"><table><thead><tr>' + "".join(f"<th>{inline_fmt(c)}</th>" for c in cells) + "</tr></thead><tbody>")
                in_table = True
            else:
                out.append("<tr>" + "".join(f"<td>{inline_fmt(c)}</td>" for c in cells) + "</tr>")
            continue
        if in_table:
            out.append("</tbody></table></div>")
            in_table = False
        if st.startswith("### "):
            if in_ul:
                out.append("</ul>")
                in_ul = False
            out.append(f"<h3>{inline_fmt(st[4:])}</h3>")
        elif st.startswith("## "):
            if in_ul:
                out.append("</ul>")
                in_ul = False
            out.append(f"<h2>{inline_fmt(st[3:])}</h2>")
        elif st.startswith("# "):
            if in_ul:
                out.append("</ul>")
                in_ul = False
            out.append(f"<h1>{inline_fmt(st[2:])}</h1>")
        elif st.startswith("- "):
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{inline_fmt(st[2:])}</li>")
        elif st.startswith("<details>") or st.startswith("</details>"):
            if in_ul:
                out.append("</ul>")
                in_ul = False
            out.append(st)
        else:
            if in_ul:
                out.append("</ul>")
                in_ul = False
            out.append(f"<p>{inline_fmt(st)}</p>")
    if in_ul:
        out.append("</ul>")
    if in_table:
        out.append("</tbody></table></div>")
    return "\n".join(out)


DOMAIN_META = [
    ("harnesses", "로봇 하네스 · 아키텍처", "#2563eb", "#eff6ff"),
    ("embodied_models", "빅테크 · 연구 모델 실험", "#7c3aed", "#f5f3ff"),
    ("hardware_sdk", "로봇 플랫폼 · 중국/글로벌 깃헙 & SDK", "#059669", "#ecfdf5"),
    ("ai_frontier", "프론티어 모델 · 에이전트 (20% 슬라이스)", "#d97706", "#fffbeb"),
]


def _sig_color(sig: float) -> Tuple[str, str]:
    if sig >= 0.85:
        return "#dc2626", "#fef2f2"
    if sig >= 0.75:
        return "#2563eb", "#eff6ff"
    if sig >= 0.60:
        return "#059669", "#ecfdf5"
    return "#6b7280", "#f3f4f6"


def render_newsletter_html(run_id: Optional[str] = None) -> str:
    events_all = load_jsonl(STATE_DIR / "events.jsonl")
    runs = load_jsonl(STATE_DIR / "runs.jsonl")
    if not run_id:
        run_id = runs[-1]["run_id"] if runs else (events_all[-1]["run_id"] if events_all else now_kst().strftime("%Y-%m-%d-pm"))
    run_events = [e for e in events_all if e.get("run_id") == run_id]
    if not run_events and events_all:
        run_events = events_all[-20:]
    run_events.sort(key=lambda e: (float(e.get("significance", 0)), bool(e.get("official", False)), int(e.get("sources", 1))), reverse=True)

    run_rec = next((r for r in reversed(runs) if r.get("run_id") == run_id), None)
    processed = run_rec.get("processed", len(run_events)) if run_rec else len(run_events)
    discarded = run_rec.get("discarded", 0) if run_rec else 0

    # Top 3 highlights
    top3_html = ""
    for ev in run_events[:3]:
        sig = float(ev.get("significance", 0))
        fg, bg = _sig_color(sig)
        url = (ev.get("urls") or ["#"])[0]
        off_badge = '<span style="display:inline-block;padding:2px 6px;border-radius:4px;font-size:11px;font-weight:600;background:#e0f2fe;color:#0369a1;margin-left:6px;">공식</span>' if ev.get("official") else ""
        top3_html += f"""
        <div style="background:#ffffff;border:1px solid #e2e8f0;border-left:4px solid {fg};border-radius:8px;padding:12px 14px;margin-bottom:10px;">
          <div style="margin-bottom:4px;">
            <span style="display:inline-block;padding:2px 7px;border-radius:999px;font-size:11px;font-weight:700;background:{bg};color:{fg};">{sig:.2f}</span>
            <span style="display:inline-block;padding:2px 6px;border-radius:4px;font-size:11px;background:#f1f5f9;color:#475569;margin-left:6px;">{html.escape(str(ev.get('topic', '')))}</span>
            {off_badge}
          </div>
          <div style="font-size:15px;font-weight:700;line-height:1.4;margin-bottom:5px;">
            <a href="{html.escape(url)}" style="color:#0f172a;text-decoration:none;" target="_blank">{html.escape(ev.get('headline_ko', ''))}</a>
          </div>
          <div style="font-size:13.5px;color:#334155;line-height:1.55;">{html.escape(ev.get('detail_ko', ''))}</div>
        </div>"""

    # Domain sections
    sections_html = ""
    for dom_id, dom_name, dom_fg, dom_bg in DOMAIN_META:
        dom_evs = [e for e in run_events if e.get("domain") == dom_id]
        if not dom_evs:
            continue
        cards = ""
        for ev in dom_evs:
            sig = float(ev.get("significance", 0))
            fg, bg = _sig_color(sig)
            urls = ev.get("urls") or []
            primary_url = urls[0] if urls else "#"
            srcs = ", ".join(ev.get("source_ids") or [])
            off_txt = "공식" if ev.get("official") else "비공식"
            kws = "".join(
                f'<span style="display:inline-block;padding:1px 6px;border-radius:4px;font-size:11px;background:#fef3c7;color:#92400e;margin-left:4px;">#{html.escape(k)}</span>'
                for k in (ev.get("keywords_hit") or [])
            )
            extra_links = ""
            if len(urls) > 1:
                extra_links = " · " + " ".join(
                    f'<a href="{html.escape(u)}" style="color:#2563eb;text-decoration:none;" target="_blank">출처{idx+2}</a>'
                    for idx, u in enumerate(urls[1:])
                )
            cards += f"""
            <div style="border-bottom:1px solid #e2e8f0;padding:14px 0;">
              <div style="margin-bottom:5px;">
                <span style="display:inline-block;padding:2px 7px;border-radius:999px;font-size:11px;font-weight:700;background:{bg};color:{fg};">{sig:.2f}</span>
                <span style="display:inline-block;padding:2px 6px;border-radius:4px;font-size:11px;font-weight:600;background:#f1f5f9;color:#334155;margin-left:5px;">{html.escape(str(ev.get('topic', '')))}</span>
                <span style="font-size:11px;color:#64748b;margin-left:6px;">{off_txt} · {html.escape(srcs)}</span>
                {kws}
              </div>
              <div style="font-size:15px;font-weight:700;line-height:1.45;margin-bottom:5px;">
                <a href="{html.escape(primary_url)}" style="color:#0f172a;text-decoration:none;" target="_blank">{html.escape(ev.get('headline_ko', ''))}</a>
              </div>
              <div style="font-size:13.5px;color:#334155;line-height:1.6;margin-bottom:6px;">{html.escape(ev.get('detail_ko', ''))}</div>
              <div style="font-size:12px;color:#64748b;">
                <a href="{html.escape(primary_url)}" style="color:#2563eb;font-weight:600;text-decoration:none;" target="_blank">원문 보기 →</a>{extra_links}
              </div>
            </div>"""
        sections_html += f"""
        <div style="margin-top:24px;">
          <div style="background:{dom_bg};border-left:4px solid {dom_fg};padding:8px 12px;border-radius:6px;margin-bottom:6px;">
            <span style="font-size:15px;font-weight:700;color:{dom_fg};">{html.escape(dom_name)}</span>
            <span style="font-size:12px;color:#64748b;margin-left:8px;">{len(dom_evs)}건</span>
          </div>
          {cards}
        </div>"""

    # Domain share summary
    tot = len(run_events) or 1
    share_pills = " ".join(
        f'<span style="display:inline-block;padding:3px 8px;border-radius:6px;font-size:12px;background:{bg};color:{fg};margin:2px 4px 2px 0;font-weight:600;">{name.split(" · ")[0]} {round(sum(1 for e in run_events if e.get("domain")==did)/tot*100)}%</span>'
        for did, name, fg, bg in DOMAIN_META
        if any(e.get("domain") == did for e in run_events)
    )

    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>RoboSpine Trend Newsletter · {html.escape(run_id)}</title>
</head>
<body style="margin:0;padding:16px;background:#f1f5f9;font-family:-apple-system,BlinkMacSystemFont,'Apple SD Gothic Neo','Malgun Gothic','Segoe UI',Roboto,sans-serif;color:#0f172a;">
  <div style="max-width:680px;margin:0 auto;background:#ffffff;border-radius:14px;overflow:hidden;border:1px solid #e2e8f0;box-shadow:0 2px 8px rgba(15,23,42,0.05);">
    <!-- Header -->
    <div style="background:linear-gradient(135deg,#0f172a 0%,#1e3a8a 100%);padding:22px 24px;color:#ffffff;">
      <div style="font-size:11px;letter-spacing:1.2px;text-transform:uppercase;color:#93c5fd;font-weight:700;margin-bottom:6px;">ROBOSPINE TREND NEWSLETTER</div>
      <div style="font-size:21px;font-weight:800;line-height:1.3;margin-bottom:8px;">로봇 하네스 &amp; 프론티어 AI 브리핑</div>
      <div style="font-size:13px;color:#cbd5e1;">회차: <strong>{html.escape(run_id)}</strong> · 핵심 사건 <strong>{len(run_events)}건</strong> (판정 {processed} · 제외 {discarded})</div>
    </div>

    <!-- Body -->
    <div style="padding:20px 24px;">
      <!-- Share bar -->
      <div style="margin-bottom:18px;">{share_pills}</div>

      <!-- Top 3 -->
      <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:14px 16px;margin-bottom:20px;">
        <div style="font-size:14px;font-weight:800;color:#0f172a;margin-bottom:10px;">🔥 한눈에 보는 오늘의 핵심 TOP 3</div>
        {top3_html}
      </div>

      <!-- Domain Sections -->
      {sections_html}
    </div>

    <!-- Footer -->
    <div style="background:#f8fafc;border-top:1px solid #e2e8f0;padding:14px 24px;font-size:12px;color:#64748b;text-align:center;">
      RoboSpine Trend Monitor · Generated {iso_kst(now_kst())} ·
      <a href="https://github.com/htkim27/trend-monitor/blob/main/trends/latest.md" style="color:#2563eb;text-decoration:none;">GitHub 아카이브 보기</a>
    </div>
  </div>
</body>
</html>
"""


def cmd_render_page(args: argparse.Namespace) -> int:
    run_id = getattr(args, "run_id", None)
    page = render_newsletter_html(run_id=run_id)
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    (SITE_DIR / "index.html").write_text(page, encoding="utf-8")
    print(f"Rendered {SITE_DIR / 'index.html'}")
    return 0


# ── Command: publish-gws ─────────────────────────────────────────────────────

def load_dotenv() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        if k and k not in os.environ:
            os.environ[k] = v


def cmd_publish_gws(args: argparse.Namespace) -> int:
    load_dotenv()
    settings = load_yaml(CONFIG_DIR / "settings.yaml")
    gws = settings.get("google_workspace") or {}
    webhook = os.environ.get("GWS_WEBHOOK_URL") or gws.get("apps_script_webhook_url")
    secret = os.environ.get("GWS_WEBHOOK_SECRET") or gws.get("webhook_secret") or ""
    doc_id = os.environ.get("GWS_DOC_ID") or gws.get("doc_id")
    sheet_id = os.environ.get("GWS_SHEET_ID") or gws.get("sheet_id")
    notify_email = os.environ.get("GWS_NOTIFY_EMAIL") or gws.get("notify_email")
    send_email_env = os.environ.get("GWS_SEND_EMAIL")
    send_email = (send_email_env.lower() == "true") if send_email_env is not None else bool(gws.get("send_email_on_run", False))

    if not webhook:
        print(json.dumps({"status": "skipped", "reason": "google_workspace.apps_script_webhook_url not configured"}, ensure_ascii=False))
        return 0

    latest_md = (TRENDS_DIR / "latest.md").read_text(encoding="utf-8") if (TRENDS_DIR / "latest.md").exists() else ""
    html_email = render_newsletter_html(run_id=args.run_id)
    events = [e for e in load_jsonl(STATE_DIR / "events.jsonl") if e.get("run_id") == args.run_id]
    payload = {
        "secret": secret,
        "run_id": args.run_id,
        "doc_id": doc_id or None,
        "sheet_id": sheet_id or None,
        "notify_email": notify_email or None,
        "send_email": send_email,
        "markdown": latest_md,
        "html_email": html_email,
        "events": events,
    }
    try:
        r = requests.post(webhook, json=payload, timeout=25)
        r.raise_for_status()
        print(json.dumps({"status": "ok", "http": r.status_code, "response": r.text[:300]}, ensure_ascii=False))
        return 0
    except Exception as e:
        print(json.dumps({"status": "error", "error": str(e)}, ensure_ascii=False))
        return 1


# ── Main ─────────────────────────────────────────────────────────────────────

def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description="RoboSpine Trend Monitor CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    sc = sub.add_parser("source-check", help="Verify source URLs with live HTTP requests")
    sc.add_argument("--all", action="store_true")
    sc.add_argument("--source", type=str, default=None)
    sc.set_defaults(func=cmd_source_check)

    col = sub.add_parser("collect", help="Collect new items into state/pending.jsonl")
    col.add_argument("--include-standby", action="store_true")
    col.add_argument("--source", type=str, default=None)
    col.set_defaults(func=cmd_collect)

    pf = sub.add_parser("prefilter", help="Populate keymap hints in pending.jsonl")
    pf.set_defaults(func=cmd_prefilter)

    ms = sub.add_parser("merge-structural", help="Structurally merge classified items")
    ms.add_argument("--run-id", required=True)
    ms.set_defaults(func=cmd_merge_structural)

    acc = sub.add_parser("accumulate", help="Update events, topics, proposals, lifecycle")
    acc.add_argument("--run-id", required=True)
    acc.set_defaults(func=cmd_accumulate)

    tr = sub.add_parser("trends", help="Recompute trend_daily.csv and momentum")
    tr.set_defaults(func=cmd_trends)

    fin = sub.add_parser("finalize", help="Move classified items from pending to seen")
    fin.add_argument("--run-id", required=True)
    fin.set_defaults(func=cmd_finalize)

    pr = sub.add_parser("profile", help="Measure source hit-rates")
    pr.add_argument("--apply", action="store_true")
    pr.set_defaults(func=cmd_profile)

    st = sub.add_parser("status", help="Show pipeline status")
    st.set_defaults(func=cmd_status)

    rp = sub.add_parser("render-page", help="Render mobile-friendly site/index.html")
    rp.set_defaults(func=cmd_render_page)

    gw = sub.add_parser("publish-gws", help="Publish latest run to Google Workspace via Apps Script")
    gw.add_argument("--run-id", required=True)
    gw.set_defaults(func=cmd_publish_gws)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
