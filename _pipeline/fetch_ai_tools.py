#!/usr/bin/env python3
"""
fetch_ai_tools.py — Pull monthly organic-traffic history for major AI tools
from the ahrefs Site Explorer API and save it into data_v3.json's `ai_tools`
key for the ⑤ 主要AIツール tab.

Endpoint:
  GET https://api.ahrefs.com/v3/site-explorer/metrics-history
  Authorization: Bearer <AHREFS_API_TOKEN>

Country: defaults to JP (日本国内) — the dashboard targets Japan-specific AI
adoption trends. Override via AI_TOOLS_COUNTRY.

NOTE: ahrefs metrics-history with `country` filter rejects windows >~12 months
with an empty error. We split each domain's request into 6-month chunks and
merge them, deduping by month.

Required env:
  AHREFS_API_TOKEN

Optional env:
  AI_TOOLS_FROM     — start date (YYYY-MM-DD), default 2024-06-01 (JP data
                      starts here)
  AI_TOOLS_TO       — end date   (YYYY-MM-DD), default today
  AI_TOOLS_COUNTRY  — ISO 3166-1 alpha-2 code, default 'JP'. Use '' for global.

Schema written to data_v3.json["ai_tools"]:
{
  "generated_at": "<ISO8601 JST>",
  "date_range": {"from": "...", "to": "..."},
  "domains": [
    {
      "ai":     "OpenAI",
      "label":  "ChatGPT",
      "domain": "chatgpt.com",
      "color":  "#10a37f",
      "metrics": [
        {"date": "2024-01", "org_traffic": 5729, "paid_traffic": 0},
        ...
      ]
    },
    ...
  ]
}

Behavior:
- AHREFS_API_TOKEN missing → exit 0 silently (keeps prior ai_tools).
- A single domain failing → log warning, keep prior data for that domain.
- All domains failing → keep prior ai_tools entirely.
"""
from __future__ import annotations
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(ROOT, 'data_v3.json')
API_URL = 'https://api.ahrefs.com/v3/site-explorer/metrics-history'

DEFAULT_FROM = '2024-06-01'  # JP traffic data starts ~mid-2024
DEFAULT_COUNTRY = 'JP'
WINDOW_MONTHS = 6  # split queries into 6-month chunks (>12 months errors out for country-filtered queries)

# AI domains to track. (ai, label, domain, color)
# colors picked to match the brand-tint CSS in build_html_v3.py
TARGETS = [
    ('OpenAI',     'ChatGPT',    'chatgpt.com',              '#10a37f'),
    ('Anthropic',  'Claude',     'claude.ai',                '#d97706'),
    ('Google',     'Gemini',     'gemini.google.com',        '#4285f4'),
    ('Microsoft',  'Copilot',    'copilot.microsoft.com',    '#0078d4'),
    ('Perplexity', 'Perplexity', 'perplexity.ai',            '#20c997'),
    ('DeepSeek',   'DeepSeek',   'chat.deepseek.com',        '#5b6cff'),
    ('xAI',        'Grok',       'grok.com',                 '#212121'),
]


def _add_months(yyyy_mm_dd: str, n: int) -> str:
    """Add n months to a YYYY-MM-DD date string (day always becomes 01)."""
    y, m, _ = (int(x) for x in yyyy_mm_dd.split('-'))
    idx = (y * 12 + (m - 1)) + n
    ny, nm = idx // 12, (idx % 12) + 1
    return f'{ny:04d}-{nm:02d}-01'


def _chunk_windows(date_from: str, date_to: str, months: int) -> list[tuple[str, str]]:
    """Yield (from, to) windows of ~`months` length covering [date_from, date_to]."""
    windows = []
    cursor = date_from
    while cursor <= date_to:
        end = _add_months(cursor, months - 1)
        if end > date_to:
            end = date_to
        windows.append((cursor, end))
        cursor = _add_months(end, 1)
    return windows


def _fetch_one_window(token: str, target: str, country: str, date_from: str, date_to: str) -> list[dict] | None:
    params = {
        'target': target,
        'mode': 'subdomains',
        'date_from': date_from,
        'date_to': date_to,
        'history_grouping': 'monthly',
        'select': 'date,org_traffic,paid_traffic',
        'output': 'json',
    }
    if country:
        params['country'] = country
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
        # Empty/no-data windows return HTTP error with `{"error":""}` — treat as 0 rows
        if e.code in (400, 404, 422):
            return []
        print(f'fetch_ai_tools: WARN HTTP {e.code} for {target} {date_from}..{date_to}: {body[:200]}', file=sys.stderr)
        return None
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        print(f'fetch_ai_tools: WARN network error for {target}: {e}', file=sys.stderr)
        return None
    try:
        d = json.loads(raw)
    except json.JSONDecodeError:
        print(f'fetch_ai_tools: WARN non-JSON reply for {target}: {raw[:200]}', file=sys.stderr)
        return None
    metrics = d.get('metrics')
    if not isinstance(metrics, list):
        return []
    return metrics


def fetch_history(token: str, target: str, country: str, date_from: str, date_to: str) -> list[dict] | None:
    """Fetch the full date range by splitting into 6-month chunks (country-filtered
    queries reject windows >~12 months). Returns merged, deduped, sorted metrics."""
    windows = _chunk_windows(date_from, date_to, WINDOW_MONTHS)
    by_date: dict[str, dict] = {}
    any_success = False
    for ws, we in windows:
        chunk = _fetch_one_window(token, target, country, ws, we)
        if chunk is None:
            continue  # network/parse error — skip but don't abort the domain
        any_success = True
        for m in chunk:
            date = (m.get('date') or '')[:7]
            if not date:
                continue
            by_date[date] = {
                'date': date,
                'org_traffic': int(m.get('org_traffic') or 0),
                'paid_traffic': int(m.get('paid_traffic') or 0),
            }
    if not any_success:
        return None
    return sorted(by_date.values(), key=lambda r: r['date'])


def main() -> int:
    token = (os.environ.get('AHREFS_API_TOKEN') or '').strip()
    if not token:
        print('fetch_ai_tools: AHREFS_API_TOKEN unset — skipping (existing ai_tools retained)')
        return 0

    date_to = os.environ.get('AI_TOOLS_TO') or dt.date.today().strftime('%Y-%m-%d')

    # Two scopes — both start from 2024-06 so the time axis is identical
    # (ahrefs JP history begins ~mid-2024 anyway).
    SCOPES = [
        ('jp',     '日本国内',     'JP', os.environ.get('AI_TOOLS_FROM_JP')     or '2024-06-01'),
        ('global', 'グローバル',   '',   os.environ.get('AI_TOOLS_FROM_GLOBAL') or '2024-06-01'),
    ]

    # Load existing data
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    existing = data.get('ai_tools') or {}
    prev_scopes = (existing.get('scopes') or {})

    out_scopes = {}
    for scope_id, scope_label, country, date_from in SCOPES:
        country_label = f'country={country}' if country else 'global'
        prev = (prev_scopes.get(scope_id) or {}).get('domains') or []
        prev_by_domain = {d.get('domain'): d for d in prev if d.get('domain')}

        domains_out = []
        for ai, label, domain, color in TARGETS:
            print(f'fetch_ai_tools[{scope_id}]: {label} ({domain}) {date_from} … {date_to} [{country_label}]')
            metrics = fetch_history(token, domain, country, date_from, date_to)
            if metrics is None:
                old = prev_by_domain.get(domain)
                if old:
                    print(f'  → keeping previous {len(old.get("metrics") or [])} months')
                    domains_out.append(old)
                else:
                    print(f'  → no prior data; skipping')
                continue
            domains_out.append({
                'ai': ai, 'label': label, 'domain': domain, 'color': color,
                'metrics': metrics,
            })
            if metrics:
                latest = metrics[-1]
                print(f'  → {len(metrics)} months, latest {latest["date"]}: org={latest["org_traffic"]:,}')
            else:
                print(f'  → 0 months in range')

        out_scopes[scope_id] = {
            'label': scope_label,
            'country': country or None,
            'date_range': {'from': date_from, 'to': date_to},
            'domains': domains_out,
        }

    if not out_scopes:
        print('fetch_ai_tools: WARN no scopes produced — keeping prior ai_tools entirely', file=sys.stderr)
        return 0

    now_jst = dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).isoformat(timespec='seconds')
    data['ai_tools'] = {
        'generated_at': now_jst,
        'scopes': out_scopes,
    }
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
    print(f'fetch_ai_tools: wrote {len(domains_out)} domain(s) to ai_tools')
    return 0


if __name__ == '__main__':
    sys.exit(main())
