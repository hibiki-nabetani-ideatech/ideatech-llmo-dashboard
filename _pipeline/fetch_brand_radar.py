#!/usr/bin/env python3
"""
fetch_brand_radar.py — Pull Brand Radar AI Responses from the ahrefs HTTP API
and save them to /tmp/br/br_<llm>.json so merge_brand_radar.py can consume them.

This replaces the MCP-based fetch used by Cowork-side automation: the
GitHub Actions runner has no MCP, so it talks to the public ahrefs API
directly.

Endpoint (per https://docs.ahrefs.com/api/reference/brand-radar/get-ai-responses):
  GET https://api.ahrefs.com/v3/brand-radar/ai-responses
  Authorization: Bearer <AHREFS_API_TOKEN>

Required env:
  AHREFS_API_TOKEN

Optional env:
  BR_REPORT_ID         — default 019d39ec-9007-757f-98af-6b7f59a96c23
  BR_DATA_SOURCES      — comma-separated, default 'chatgpt'
                         (others currently fail with "Missing addon" on this plan;
                         add as the plan expands.)
  BR_COUNTRY           — default 'JP'
  BR_LIMIT             — default 1000  (covers all 40 prompts comfortably)
  BR_OUT_DIR           — default '/tmp/br'

The output file shape matches what merge_brand_radar.py accepts:
  { "ai_responses": [ {country, data_source, question, response, links, ...}, ... ] }
"""
from __future__ import annotations
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

API_URL = 'https://api.ahrefs.com/v3/brand-radar/ai-responses'

DEFAULT_REPORT_ID = '019d39ec-9007-757f-98af-6b7f59a96c23'
DEFAULT_DATA_SOURCES = 'chatgpt'
DEFAULT_COUNTRY = 'JP'
DEFAULT_LIMIT = 1000
DEFAULT_OUT_DIR = '/tmp/br'

SELECT_FIELDS = 'country,data_source,question,response,links,search_queries,volume'


def fetch_one(token: str, data_source: str, report_id: str, country: str, limit: int) -> dict:
    params = {
        'report_id': report_id,
        'data_source': data_source,
        'country': country,
        'select': SELECT_FIELDS,
        'limit': str(limit),
        'output': 'json',
    }
    qs = urllib.parse.urlencode(params)
    url = f'{API_URL}?{qs}'
    req = urllib.request.Request(url, method='GET')
    req.add_header('Authorization', f'Bearer {token}')
    req.add_header('Accept', 'application/json')
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        raise SystemExit(
            f'ahrefs API HTTP {e.code} for data_source={data_source}: {body[:500]}'
        )
    try:
        d = json.loads(raw)
    except json.JSONDecodeError as e:
        raise SystemExit(f'ahrefs API returned non-JSON for {data_source}: {raw[:200]}')
    if not isinstance(d, dict) or 'ai_responses' not in d:
        raise SystemExit(
            f'ahrefs API response missing ai_responses for {data_source}: keys={list(d.keys()) if isinstance(d, dict) else type(d)}'
        )
    return d


def main():
    token = os.environ.get('AHREFS_API_TOKEN', '').strip()
    if not token:
        print('ERR: AHREFS_API_TOKEN env var required', file=sys.stderr)
        sys.exit(2)

    report_id = os.environ.get('BR_REPORT_ID') or DEFAULT_REPORT_ID
    sources = (os.environ.get('BR_DATA_SOURCES') or DEFAULT_DATA_SOURCES).split(',')
    country = os.environ.get('BR_COUNTRY') or DEFAULT_COUNTRY
    try:
        limit = int(os.environ.get('BR_LIMIT') or DEFAULT_LIMIT)
    except ValueError:
        limit = DEFAULT_LIMIT
    out_dir = os.environ.get('BR_OUT_DIR') or DEFAULT_OUT_DIR

    os.makedirs(out_dir, exist_ok=True)

    total_rows = 0
    for src in sources:
        src = src.strip().lower()
        if not src:
            continue
        print(f'… fetching data_source={src}')
        d = fetch_one(token, src, report_id, country, limit)
        rows = d.get('ai_responses') or []
        out_path = os.path.join(out_dir, f'br_{src}.json')
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(d, f, ensure_ascii=False)
        size_kb = os.path.getsize(out_path) / 1024
        print(f'  → {len(rows)} rows, {size_kb:.1f} KB → {out_path}')
        total_rows += len(rows)

    print(f'fetch_brand_radar: total {total_rows} rows across {len(sources)} source(s).')


if __name__ == '__main__':
    main()
