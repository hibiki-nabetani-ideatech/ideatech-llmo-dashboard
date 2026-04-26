#!/usr/bin/env python3
"""
merge_brand_radar.py — Merge raw ahrefs Brand Radar AI Responses into
data_v3.json's prompts section.

Expected input format (one or more files, --in PATH):
{
  "ai_responses": [
    {
      "country": "JP",
      "data_source": "chatgpt"|"gemini"|"copilot"|"perplexity"|"grok",
      "question": "<exact prompt text matching prompts.rows[].prompt>",
      "response": "<full LLM response>",
      "links": [...],
      "search_queries": [...],
      "volume": <int>
    },
    ...
  ]
}

For each (question, data_source) pair, we update:
  - prompts.rows[i].responses[llm_idx]   ← response text
  - prompts.rows[i].ideatech[llm_idx]    ← '⚫︎' if IDEATECH/リサピー mentioned else '▲'
  - prompts.rows[i].prizma[llm_idx]      ← '⚫︎' if PRIZMA mentioned else '▲'
  - prompts.rows[i].links[llm_idx]       ← list of cited URLs (newly added field)
  - prompts.rows[i].volume               ← updated to latest from Brand Radar

The mapping from Brand Radar's lowercase data_source → our display name is fixed.
LLMs not in our 4-LLM matrix (e.g., grok) are silently skipped.

Usage:
  python3 merge_brand_radar.py --in /tmp/br_chatgpt.json --in /tmp/br_gemini.json ...
  python3 merge_brand_radar.py --in /tmp/br_combined.json
  python3 merge_brand_radar.py --in-dir /tmp/br/   # reads *.json in dir
"""

from __future__ import annotations
import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta
from glob import glob
from typing import Any

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(ROOT, 'data_v3.json')

# Brand Radar lowercase identifier → our display name in prompts.llms
LLM_MAP = {
    'chatgpt':    'ChatGPT',
    'gemini':     'Gemini',
    'copilot':    'Copilot',
    'perplexity': 'Perplexity',
    # 'grok' is currently NOT in our 4-LLM matrix; if added later, append here.
}

IDEATECH_RX = re.compile(r'(IDEATECH|アイディアテック|アイデアテック|リサピー|リサピ®|リサピ®|RISA[-_ ]?PY|ｲﾃﾞｱﾃｯｸ)', re.IGNORECASE)
PRIZMA_RX   = re.compile(r'(PRIZMA|プリズマ|prizma)', re.IGNORECASE)

YES_MARK = '⚫︎'
NO_MARK  = '▲'


def jst_now() -> str:
    return datetime.now(timezone(timedelta(hours=9))).isoformat(timespec='seconds')


def normalize_q(q: str) -> str:
    """Normalize whitespace and full-width characters for matching."""
    if not q:
        return ''
    s = q.strip()
    s = re.sub(r'\s+', '', s)  # remove all whitespace
    return s


def load_responses(paths: list[str]) -> list[dict]:
    rows: list[dict] = []
    for p in paths:
        with open(p, 'r', encoding='utf-8') as f:
            try:
                d = json.load(f)
            except json.JSONDecodeError as e:
                print(f'WARN: cannot parse {p}: {e}', file=sys.stderr)
                continue
        # The MCP returns {"ai_responses": [...]}.  Accept either shape.
        ar = d.get('ai_responses') if isinstance(d, dict) else None
        if ar is None and isinstance(d, list):
            ar = d
        if not ar:
            print(f'WARN: no ai_responses in {p}', file=sys.stderr)
            continue
        rows.extend(ar)
    return rows


def merge(data: dict, ai_rows: list[dict]) -> dict:
    p = data.setdefault('prompts', {})
    rows_out = p.get('rows') or []
    llms = p.get('llms') or list(LLM_MAP.values())
    p['llms'] = llms

    # Build lookups
    by_q = {normalize_q(r.get('prompt', '')): r for r in rows_out}
    llm_idx = {name: i for i, name in enumerate(llms)}

    stats = {
        'total_input': len(ai_rows),
        'matched': 0,
        'unmatched': 0,
        'skipped_unknown_llm': 0,
        'updated_pairs': 0,
        'mention_changes': 0,
        'unknown_questions': [],
    }

    for ai in ai_rows:
        ds = (ai.get('data_source') or '').lower()
        if ds not in LLM_MAP:
            stats['skipped_unknown_llm'] += 1
            continue
        display = LLM_MAP[ds]
        if display not in llm_idx:
            stats['skipped_unknown_llm'] += 1
            continue
        i = llm_idx[display]

        q = ai.get('question') or ''
        nq = normalize_q(q)
        target = by_q.get(nq)
        if not target:
            # Try fuzzy: substring match on first 40 chars
            head = nq[:40]
            for k, v in by_q.items():
                if head and head in k:
                    target = v
                    break
        if not target:
            stats['unmatched'] += 1
            if len(stats['unknown_questions']) < 10:
                stats['unknown_questions'].append(q[:80])
            continue
        stats['matched'] += 1

        # Ensure arrays are sized to len(llms)
        for key in ('responses', 'ideatech', 'prizma'):
            arr = target.get(key)
            if not isinstance(arr, list):
                arr = []
            while len(arr) < len(llms):
                arr.append('' if key == 'responses' else None)
            target[key] = arr

        # Cited links (new field)
        links_arr = target.get('links_by_llm')
        if not isinstance(links_arr, list):
            links_arr = [None] * len(llms)
        while len(links_arr) < len(llms):
            links_arr.append(None)
        target['links_by_llm'] = links_arr

        resp = ai.get('response') or ''
        target['responses'][i] = resp

        prev_i_mark = target['ideatech'][i]
        prev_p_mark = target['prizma'][i]
        new_i_mark = YES_MARK if IDEATECH_RX.search(resp) else NO_MARK
        new_p_mark = YES_MARK if PRIZMA_RX.search(resp)   else NO_MARK
        if prev_i_mark != new_i_mark:
            stats['mention_changes'] += 1
        if prev_p_mark != new_p_mark:
            stats['mention_changes'] += 1
        target['ideatech'][i] = new_i_mark
        target['prizma'][i]   = new_p_mark

        # Cited URLs
        links = ai.get('links') or []
        urls = []
        for l in links:
            if isinstance(l, dict):
                u = l.get('url') or l.get('link') or ''
                if u:
                    urls.append(u)
            elif isinstance(l, str):
                urls.append(l)
        target['links_by_llm'][i] = urls

        # Volume (use the max value seen for this question across LLMs)
        v = ai.get('volume')
        if isinstance(v, (int, float)):
            cur_v = target.get('volume')
            if cur_v is None or v > cur_v:
                target['volume'] = int(v)

        stats['updated_pairs'] += 1

    p['_last_brand_radar_sync'] = jst_now()
    return stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='inputs', action='append', default=[], help='Path to a Brand Radar AI Responses JSON file. Can be passed multiple times.')
    ap.add_argument('--in-dir', dest='in_dir', default=None, help='Directory containing *.json files to merge.')
    ap.add_argument('--data', dest='data_path', default=DATA_PATH, help=f'Target data_v3.json (default {DATA_PATH})')
    ap.add_argument('--dry-run', action='store_true', help='Compute stats but do not write data_v3.json')
    args = ap.parse_args()

    paths: list[str] = list(args.inputs)
    if args.in_dir:
        paths.extend(sorted(glob(os.path.join(args.in_dir, '*.json'))))
    if not paths:
        print('ERR: no input files (--in or --in-dir required)', file=sys.stderr)
        sys.exit(2)

    ai_rows = load_responses(paths)
    if not ai_rows:
        print('ERR: no ai_responses rows loaded from any input', file=sys.stderr)
        sys.exit(3)

    with open(args.data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    stats = merge(data, ai_rows)

    if args.dry_run:
        print('DRY RUN — not writing.')
    else:
        with open(args.data_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

    print(f'Inputs: {len(paths)} file(s), {stats["total_input"]} response rows.')
    print(f'Matched/Updated: {stats["matched"]} / {stats["updated_pairs"]} pairs.')
    print(f'Mention mark changes: {stats["mention_changes"]}.')
    print(f'Unmatched questions: {stats["unmatched"]} (sample: {stats["unknown_questions"][:3]})')
    print(f'Skipped (LLM not in matrix): {stats["skipped_unknown_llm"]}')


if __name__ == '__main__':
    main()
