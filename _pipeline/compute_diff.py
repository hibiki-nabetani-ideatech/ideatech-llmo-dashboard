#!/usr/bin/env python3
"""
compute_diff.py — Compute week-over-week diff between data_v3.json (current)
and data_v3_prev.json (snapshot), then store the result back into data_v3.json
under the `diff` key for the dashboard's diff tab to render.

Diff coverage:
  - flow.series: site_total / organic / ai_total / ai_ratio  (delta + %)
  - flow.cv_site_total / cv_organic / cv_ai_total            (delta + %)
  - prompts.rows: per-prompt × per-LLM mention status flips (▲↔⚫︎),
                  plus response text diff flags (changed / new / removed)
  - citation_ideatech / citation_risapy: new entries (URLs not in prev)
  - generated_at: ISO timestamp + prev_generated_at if present

Usage:
  python3 compute_diff.py
        — reads data_v3.json (current) and data_v3_prev.json (prev),
          writes diff back into data_v3.json under "diff"
  python3 compute_diff.py --snapshot
        — first copies data_v3.json → data_v3_prev.json (creates a fresh
          baseline) then computes diff (which will be all zeros)
"""

from __future__ import annotations
import json
import os
import sys
import shutil
from datetime import datetime, timezone, timedelta
from typing import Any

ROOT = os.path.dirname(os.path.abspath(__file__))
CUR_PATH = os.path.join(ROOT, 'data_v3.json')
PREV_PATH = os.path.join(ROOT, 'data_v3_prev.json')

YES_MARKS = {'⚫︎', '●', '◉'}


def jst_now_iso() -> str:
    jst = timezone(timedelta(hours=9))
    return datetime.now(jst).isoformat(timespec='seconds')


def safe_float(v) -> float | None:
    try:
        if v is None:
            return None
        return float(v)
    except (TypeError, ValueError):
        return None


def pct(a: float | None, b: float | None) -> float | None:
    """Percentage change (a current / b prev) - 1. None if b is None or 0."""
    if a is None or b is None or b == 0:
        return None
    return (a - b) / b


def last_non_null_idx(arr: list) -> int:
    for i in range(len(arr) - 1, -1, -1):
        if arr[i] is not None:
            return i
    return -1


def diff_series(cur_series: list, prev_series: list, months: list) -> dict:
    """Return monthly diff entries for a numeric series."""
    cur = [safe_float(v) for v in (cur_series or [])]
    prev = [safe_float(v) for v in (prev_series or [])]
    n = max(len(cur), len(prev), len(months))
    cur += [None] * (n - len(cur))
    prev += [None] * (n - len(prev))

    cur_last = last_non_null_idx(cur)
    prev_last = last_non_null_idx(prev)

    # latest month diff (current vs same month last week's snapshot)
    latest = None
    if cur_last >= 0:
        c = cur[cur_last]
        p = prev[cur_last] if cur_last < len(prev) else None
        latest = {
            'month': months[cur_last] if cur_last < len(months) else None,
            'current': c,
            'previous': p,
            'delta': (c - p) if (c is not None and p is not None) else None,
            'pct_change': pct(c, p),
        }

    # YTD totals comparison
    cur_year = months[cur_last][:4] if cur_last >= 0 and cur_last < len(months) else None
    ytd = None
    if cur_year:
        cur_ytd = sum((cur[i] or 0) for i, m in enumerate(months) if m.startswith(cur_year) and cur[i] is not None)
        prev_ytd = sum((prev[i] or 0) for i, m in enumerate(months) if m.startswith(cur_year) and prev[i] is not None)
        ytd = {
            'year': cur_year,
            'current': cur_ytd,
            'previous': prev_ytd,
            'delta': cur_ytd - prev_ytd,
            'pct_change': pct(cur_ytd, prev_ytd),
        }

    # cumulative grand total
    cur_total = sum((v or 0) for v in cur if v is not None)
    prev_total = sum((v or 0) for v in prev if v is not None)
    cumulative = {
        'current': cur_total,
        'previous': prev_total,
        'delta': cur_total - prev_total,
        'pct_change': pct(cur_total, prev_total),
    }

    # last 4 weeks-equivalent (we have monthly granularity → use last 4 months)
    return {
        'latest_month': latest,
        'ytd': ytd,
        'cumulative': cumulative,
    }


def status_label(mark: str) -> str:
    return 'yes' if mark in YES_MARKS else ('no' if mark else 'unknown')


def diff_prompts(cur_p: dict, prev_p: dict) -> dict:
    """Compare 40 prompts × 4 LLMs and detect flips + response changes."""
    cur_rows = cur_p.get('rows') or []
    prev_rows = prev_p.get('rows') or []
    llms = cur_p.get('llms') or []
    prev_by_no = {r.get('no'): r for r in prev_rows}

    flips = []  # status flips (▲ ↔ ⚫︎)
    response_changes = []  # responses where text changed
    new_prompts = []  # prompts that didn't exist before
    for r in cur_rows:
        no = r.get('no')
        prev = prev_by_no.get(no)
        if prev is None:
            new_prompts.append({'no': no, 'prompt': r.get('prompt', ''), 'category': r.get('category', '')})
            continue

        # Status flips per LLM × per brand
        for brand_key in ('ideatech', 'prizma'):
            cur_marks = r.get(brand_key) or [None] * len(llms)
            prev_marks = prev.get(brand_key) or [None] * len(llms)
            for i, llm in enumerate(llms):
                c_mark = cur_marks[i] if i < len(cur_marks) else None
                p_mark = prev_marks[i] if i < len(prev_marks) else None
                c_lbl = status_label(c_mark)
                p_lbl = status_label(p_mark)
                if c_lbl != p_lbl and c_lbl != 'unknown' and p_lbl != 'unknown':
                    flips.append({
                        'no': no,
                        'prompt': r.get('prompt', ''),
                        'category': r.get('category', ''),
                        'brand': brand_key,
                        'llm': llm,
                        'from': p_lbl,
                        'to': c_lbl,
                        'from_mark': p_mark,
                        'to_mark': c_mark,
                    })

        # Response text diffs
        cur_resp = r.get('responses') or []
        prev_resp = prev.get('responses') or []
        for i, llm in enumerate(llms):
            c = (cur_resp[i] if i < len(cur_resp) else '') or ''
            p = (prev_resp[i] if i < len(prev_resp) else '') or ''
            if c != p:
                clen = len(c)
                plen = len(p)
                kind = (
                    'new' if plen == 0 and clen > 0 else
                    'removed' if clen == 0 and plen > 0 else
                    'changed'
                )
                response_changes.append({
                    'no': no,
                    'prompt': r.get('prompt', ''),
                    'llm': llm,
                    'kind': kind,
                    'prev_len': plen,
                    'cur_len': clen,
                    'len_delta': clen - plen,
                    # Keep full text only if reasonably small; otherwise truncate.
                    'prev': p[:4000] if p else '',
                    'cur':  c[:4000] if c else '',
                    'prev_truncated': plen > 4000,
                    'cur_truncated':  clen > 4000,
                })

    # Aggregate counts
    flips_summary = {
        'total': len(flips),
        'gained': sum(1 for f in flips if f['to'] == 'yes' and f['from'] == 'no'),  # ▲ → ⚫︎
        'lost':   sum(1 for f in flips if f['to'] == 'no' and f['from'] == 'yes'),  # ⚫︎ → ▲
        'by_brand': {},
        'by_llm': {},
    }
    for f in flips:
        flips_summary['by_brand'][f['brand']] = flips_summary['by_brand'].get(f['brand'], 0) + 1
        flips_summary['by_llm'][f['llm']] = flips_summary['by_llm'].get(f['llm'], 0) + 1

    return {
        'flips': flips,
        'flips_summary': flips_summary,
        'response_changes': response_changes,
        'response_changes_count': len(response_changes),
        'new_prompts': new_prompts,
    }


def diff_citations(cur_c: dict, prev_c: dict) -> dict:
    """Find new citation rows (URLs not present in prev)."""
    cur_rows = (cur_c or {}).get('rows') or []
    prev_rows = (prev_c or {}).get('rows') or []
    prev_urls = {r.get('url') for r in prev_rows if r.get('url')}
    new_rows = [r for r in cur_rows if r.get('url') and r.get('url') not in prev_urls]

    def dr_int(r):
        try:
            return int(str(r.get('dr') or '').strip())
        except (TypeError, ValueError):
            return -1

    new_high = [r for r in new_rows if dr_int(r) >= 70]
    new_top = [r for r in new_rows if dr_int(r) >= 90]

    return {
        'count_total_now': len(cur_rows),
        'count_total_prev': len(prev_rows),
        'count_new': len(new_rows),
        'count_new_high': len(new_high),
        'count_new_top': len(new_top),
        # Sort new entries by DR desc, then by date desc
        'new_rows': sorted(new_rows, key=lambda r: (-dr_int(r), -(int(str(r.get('no') or 0)) if str(r.get('no') or '0').isdigit() else 0)))[:200],
    }


def compute_diff(cur: dict, prev: dict) -> dict:
    out = {
        'generated_at': jst_now_iso(),
        'prev_generated_at': prev.get('_generated_at') or prev.get('diff', {}).get('generated_at'),
        'has_prev': True,
    }
    # Flow / SS
    flow_c = cur.get('flow') or {}
    flow_p = prev.get('flow') or {}
    months_c = flow_c.get('months') or []
    months_p = flow_p.get('months') or []
    months = months_c if len(months_c) >= len(months_p) else months_p

    series_c = (flow_c.get('series') or {})
    series_p = (flow_p.get('series') or {})
    out['flow'] = {
        'site_total': diff_series(series_c.get('site_total') or [], series_p.get('site_total') or [], months),
        'organic':    diff_series(series_c.get('organic') or [],    series_p.get('organic') or [],    months),
        'ai_total':   diff_series(series_c.get('ai_total') or [],   series_p.get('ai_total') or [],   months),
        'ai_ratio':   diff_series(series_c.get('ai_ratio') or [],   series_p.get('ai_ratio') or [],   months),
    }
    out['cv'] = {
        'cv_site_total': diff_series(flow_c.get('cv_site_total') or [], flow_p.get('cv_site_total') or [], months),
        'cv_organic':    diff_series(flow_c.get('cv_organic') or [],    flow_p.get('cv_organic') or [],    months),
        'cv_ai_total':   diff_series(flow_c.get('cv_ai_total') or [],   flow_p.get('cv_ai_total') or [],   months),
    }

    # Prompts
    out['prompts'] = diff_prompts(cur.get('prompts') or {}, prev.get('prompts') or {})

    # Citations
    out['citation_ideatech'] = diff_citations(cur.get('citation_ideatech'), prev.get('citation_ideatech'))
    out['citation_risapy']   = diff_citations(cur.get('citation_risapy'),   prev.get('citation_risapy'))

    return out


def empty_diff(reason: str = 'first_run') -> dict:
    """Build a no-diff object for the first run when no prev exists."""
    return {
        'generated_at': jst_now_iso(),
        'has_prev': False,
        'reason': reason,
    }


def main():
    snapshot = '--snapshot' in sys.argv

    if not os.path.exists(CUR_PATH):
        print(f'ERR: {CUR_PATH} not found', file=sys.stderr)
        sys.exit(1)

    if snapshot:
        # Save current as prev BEFORE any other work — establishes a baseline
        # for the next run.  Diff computed from the (now identical) prev will
        # be all zeros, which is the correct first-run state.
        shutil.copyfile(CUR_PATH, PREV_PATH)
        print(f'Snapshot: {CUR_PATH} -> {PREV_PATH}')

    with open(CUR_PATH, 'r', encoding='utf-8') as f:
        cur = json.load(f)

    if os.path.exists(PREV_PATH):
        with open(PREV_PATH, 'r', encoding='utf-8') as f:
            prev = json.load(f)
        diff = compute_diff(cur, prev)
    else:
        diff = empty_diff('no_prev_snapshot')

    cur['diff'] = diff
    cur.setdefault('_generated_at', jst_now_iso())

    with open(CUR_PATH, 'w', encoding='utf-8') as f:
        json.dump(cur, f, ensure_ascii=False, separators=(',', ':'))

    # Brief summary
    if diff.get('has_prev'):
        flips = diff['prompts']['flips_summary']
        new_cit_i = diff['citation_ideatech']['count_new']
        new_cit_r = diff['citation_risapy']['count_new']
        print(f'diff: prompts flips={flips["total"]} (gained={flips["gained"]} lost={flips["lost"]}), '
              f'citations new (IDEATECH={new_cit_i}, リサピー={new_cit_r}), '
              f'response_changes={diff["prompts"]["response_changes_count"]}')
    else:
        print(f'diff: no prev snapshot — establishing baseline (reason={diff["reason"]})')


if __name__ == '__main__':
    main()
