#!/usr/bin/env python3
"""
fetch_ai_tools.py — Pull monthly organic-traffic history for major AI tools
from the ahrefs Site Explorer API and save it into data_v3.json's `ai_tools`
key for the ⑤ 主要AIツール tab.

Endpoint:
  GET https://api.ahrefs.com/v3/site-explorer/metrics-history
  Authorization: Bearer <AHREFS_API_TOKEN>

Required env:
  AHREFS_API_TOKEN

Optional env:
  AI_TOOLS_FROM   — start date (YYYY-MM-DD), default 2024-01-01
  AI_TOOLS_TO     — end date   (YYYY-MM-DD), default today

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

DEFAULT_FROM = '2024-01-01'

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


def fetch_history(token: str, target: str, date_from: str, date_to: str) -> list[dict] | None:
    params = {
        'target': target,
        'mode': 'subdomains',
        'date_from': date_from,
        'date_to': date_to,
        'history_grouping': 'monthly',
        'select': 'date,org_traffic,paid_traffic',
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
        print(f'fetch_ai_tools: WARN HTTP {e.code} for {target}: {body[:300]}', file=sys.stderr)
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
        print(f'fetch_ai_tools: WARN no metrics array for {target}', file=sys.stderr)
        return None
    # Normalize date "YYYY-MM-01T00:00:00Z" → "YYYY-MM"
    out = []
    for m in metrics:
        date = (m.get('date') or '')[:7]  # YYYY-MM
        if not date:
            continue
        out.append({
            'date': date,
            'org_traffic': int(m.get('org_traffic') or 0),
            'paid_traffic': int(m.get('paid_traffic') or 0),
        })
    out.sort(key=lambda r: r['date'])
    return out


def main() -> int:
    token = (os.environ.get('AHREFS_API_TOKEN') or '').strip()
    if not token:
        print('fetch_ai_tools: AHREFS_API_TOKEN unset — skipping (existing ai_tools retained)')
        return 0

    date_from = os.environ.get('AI_TOOLS_FROM') or DEFAULT_FROM
    date_to = os.environ.get('AI_TOOLS_TO') or dt.date.today().strftime('%Y-%m-%d')

    # Load existing data
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    prev = (data.get('ai_tools') or {}).get('domains') or []
    prev_by_domain = {d.get('domain'): d for d in prev if d.get('domain')}

    domains_out = []
    for ai, label, domain, color in TARGETS:
        print(f'fetch_ai_tools: {label} ({domain}) {date_from} … {date_to}')
        metrics = fetch_history(token, domain, date_from, date_to)
        if metrics is None:
            # Keep prior data for this domain if available
            old = prev_by_domain.get(domain)
            if old:
                print(f'  → keeping previous {len(old.get("metrics") or [])} months')
                domains_out.append(old)
            else:
                print(f'  → no prior data; skipping')
            continue
        domains_out.append({
            'ai': ai,
            'label': label,
            'domain': domain,
            'color': color,
            'metrics': metrics,
        })
        if metrics:
            latest = metrics[-1]
            print(f'  → {len(metrics)} months, latest {latest["date"]}: org={latest["org_traffic"]:,}')

    if not domains_out:
        print('fetch_ai_tools: WARN all domains failed — keeping prior ai_tools entirely', file=sys.stderr)
        return 0

    now_jst = dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).isoformat(timespec='seconds')
    data['ai_tools'] = {
        'generated_at': now_jst,
        'date_range': {'from': date_from, 'to': date_to},
        'domains': domains_out,
    }
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
    print(f'fetch_ai_tools: wrote {len(domains_out)} domain(s) to ai_tools')
    return 0


if __name__ == '__main__':
    sys.exit(main())
