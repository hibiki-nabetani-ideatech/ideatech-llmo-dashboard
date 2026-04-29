#!/usr/bin/env python3
"""
fetch_ai_topics.py — Generate the weekly "AI Topics" feed for the dashboard's
⑤ AI Topics tab.

It calls the Anthropic Messages API with the built-in `web_search` tool, asks
Claude to round up notable AI industry news from roughly the past 7-10 days
(OpenAI, Anthropic, Google, Microsoft, Perplexity, Meta, xAI, plus major
Japanese AI vendors), and writes the result into `data_v3.json` under the
`ai_topics` key.

Schema of `data_v3.json["ai_topics"]`:
{
  "generated_at": "<ISO8601 JST>",
  "model": "<model id>",
  "entries": [
    {
      "date": "YYYY-MM-DD",
      "ai": "OpenAI",                       # primary vendor/product
      "topic_tags": ["新機能", "API"],       # 1-3 tags from a fixed vocabulary
      "title": "...",                       # JA, ≤80 chars
      "summary": "...",                     # JA, 2-3 sentences
      "url": "https://...",                 # canonical source URL
      "reactions": {
        "summary": "...",                   # JA, 2-3 sentences
        "sources": [{"label":"X","url":"..."}, ...]
      }
    },
    ...
  ]
}

Behavior:
- If `ANTHROPIC_API_KEY` is missing → exit 0 silently (keep last week's data).
- If API call fails or response can't be parsed → keep last week's data and
  exit 0 with a warning. The pipeline will still finish.
- Only on a clean parse do we overwrite `ai_topics`.

Required env:
  ANTHROPIC_API_KEY

Optional env:
  AI_TOPICS_MODEL          — default 'claude-sonnet-4-5' (broadly-available alias)
  AI_TOPICS_MAX_USES       — web_search max_uses, default 8
  AI_TOPICS_TARGET_COUNT   — desired number of entries, default 12
"""
from __future__ import annotations
import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(ROOT, 'data_v3.json')

ANTHROPIC_URL = 'https://api.anthropic.com/v1/messages'
DEFAULT_MODEL = 'claude-sonnet-4-5'
DEFAULT_MAX_USES = 8
DEFAULT_TARGET = 12

ALLOWED_AIS = [
    'OpenAI', 'Anthropic', 'Google', 'Microsoft', 'Perplexity',
    'Meta', 'xAI', 'Mistral', 'DeepSeek', 'Cohere',
    '国内AI', 'その他',
]
ALLOWED_TAGS = [
    '新機能', 'プロダクト発表', '料金変更', 'パートナーシップ',
    '安全性', '規制・政策', '研究・論文', 'ベンチマーク',
    '人事・組織', '業界動向',
]


SYSTEM_PROMPT = """あなたは日本のB2B監査法人IDEATECH向けに「主要AIプロダクトの週次ニュース」を編集する調査アシスタントです。

【任務】
過去7〜10日間に公開された、AI業界の重要ニュースを {target_count} 件選んでまとめてください。
対象: OpenAI / Anthropic / Google (Gemini, NotebookLM等) / Microsoft (Copilot等) / Perplexity / Meta / xAI (Grok) / Mistral / DeepSeek / Cohere / 国内AI（Felo, ELYZA, Sakana AI等）。
重要度の優先順位: ① プロダクト発表・新機能リリース ② 料金/契約条件の変更 ③ 重要なパートナーシップ ④ 安全性・規制関連 ⑤ 注目論文・ベンチマーク ⑥ 人事・組織の重要動向。

【web_searchツールの使い方】
複数回検索してください。最初は各社の公式ブログ/プレスリリース。次にニュースアグリゲータ（TechCrunch, VentureBeat, The Verge, ITmedia等）。最後に「世間の反応」のためにX（Twitter）議論、Reddit (r/LocalLLaMA, r/singularity, r/OpenAI, r/ClaudeAI等), Hacker News のスレッドを軽く確認。

【出力】
最終回答は **必ず以下のフォーマットの```json コードブロック1つだけ** を返すこと。前置き・後書き・解説は不要。

```json
{{
  "entries": [
    {{
      "date": "YYYY-MM-DD",
      "ai": "OpenAI",
      "topic_tags": ["新機能", "API"],
      "title": "（日本語、80文字以内）",
      "summary": "（日本語、2〜3文）",
      "url": "https://...",
      "reactions": {{
        "summary": "（日本語、2〜3文。XやReddit/HNで何が議論されているか）",
        "sources": [
          {{"label": "X", "url": "https://x.com/..."}},
          {{"label": "Reddit", "url": "https://reddit.com/..."}}
        ]
      }}
    }}
  ]
}}
```

【制約】
- ai は次のいずれか: {allowed_ais}
- topic_tags は次から1〜3個選ぶ: {allowed_tags}
- title / summary / reactions.summary は日本語で記述。
- date は YYYY-MM-DD（ニュースの公開日。不明なら今日からの最新の妥当な推定日）。
- url は実在する一次ソース（公式blog or 大手メディア）。
- reactions.sources は1〜3件、可能なら実在URL。見つからない場合は空配列でOK。
- 同じ会社のニュースに偏らないよう、最低でも5社以上カバーすること。"""


def call_anthropic(api_key: str, model: str, max_uses: int, target_count: int) -> str:
    payload = {
        'model': model,
        'max_tokens': 8000,
        'system': SYSTEM_PROMPT.format(
            target_count=target_count,
            allowed_ais=' / '.join(ALLOWED_AIS),
            allowed_tags=' / '.join(ALLOWED_TAGS),
        ),
        'tools': [
            {'type': 'web_search_20250305', 'name': 'web_search', 'max_uses': max_uses}
        ],
        'messages': [
            {'role': 'user', 'content': f'過去7〜10日のAI業界ニュースを{target_count}件、上記フォーマットのJSONで返してください。'}
        ],
    }
    data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(ANTHROPIC_URL, data=data, method='POST')
    req.add_header('x-api-key', api_key)
    req.add_header('anthropic-version', '2023-06-01')
    req.add_header('content-type', 'application/json')
    with urllib.request.urlopen(req, timeout=180) as resp:
        raw = resp.read().decode('utf-8')
    obj = json.loads(raw)
    # response.content is a list of blocks; concatenate text blocks
    chunks = []
    for block in obj.get('content', []):
        if isinstance(block, dict) and block.get('type') == 'text':
            chunks.append(block.get('text', ''))
    return '\n'.join(chunks)


def extract_json(text: str) -> dict | None:
    """Pull the first ```json ... ``` block (or a bare JSON object) out of the
    model's text reply."""
    if not text:
        return None
    m = re.search(r'```json\s*(\{.*?\})\s*```', text, re.S)
    raw = m.group(1) if m else None
    if raw is None:
        # Fallback: look for the first {...} that parses cleanly
        # Find the largest balanced {...}
        start = text.find('{')
        if start < 0:
            return None
        depth = 0
        for i in range(start, len(text)):
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
                if depth == 0:
                    raw = text[start:i+1]
                    break
        if raw is None:
            return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def sanitize(entries: list) -> list:
    """Coerce/validate each entry to the schema the dashboard expects."""
    out = []
    for e in entries:
        if not isinstance(e, dict):
            continue
        date = (e.get('date') or '').strip()[:10]
        ai = (e.get('ai') or '').strip()
        tags = e.get('topic_tags') or []
        if isinstance(tags, str):
            tags = [tags]
        tags = [str(t).strip() for t in tags if str(t).strip()][:3]
        title = (e.get('title') or '').strip()
        summary = (e.get('summary') or '').strip()
        url = (e.get('url') or '').strip()
        reactions = e.get('reactions') or {}
        if not isinstance(reactions, dict):
            reactions = {}
        r_sum = (reactions.get('summary') or '').strip()
        r_src = reactions.get('sources') or []
        if not isinstance(r_src, list):
            r_src = []
        r_src = [
            {'label': str(s.get('label') or '').strip()[:24],
             'url': str(s.get('url') or '').strip()}
            for s in r_src
            if isinstance(s, dict) and s.get('url')
        ][:4]

        if not (title and url):
            continue  # required fields
        out.append({
            'date': date,
            'ai': ai or 'その他',
            'topic_tags': tags,
            'title': title,
            'summary': summary,
            'url': url,
            'reactions': {'summary': r_sum, 'sources': r_src},
        })
    # newest first
    out.sort(key=lambda x: x.get('date') or '', reverse=True)
    return out


def main() -> int:
    api_key = (os.environ.get('ANTHROPIC_API_KEY') or '').strip()
    if not api_key:
        print('fetch_ai_topics: ANTHROPIC_API_KEY unset — skipping (existing ai_topics retained)')
        return 0

    model = os.environ.get('AI_TOPICS_MODEL') or DEFAULT_MODEL
    try:
        max_uses = int(os.environ.get('AI_TOPICS_MAX_USES') or DEFAULT_MAX_USES)
    except ValueError:
        max_uses = DEFAULT_MAX_USES
    try:
        target = int(os.environ.get('AI_TOPICS_TARGET_COUNT') or DEFAULT_TARGET)
    except ValueError:
        target = DEFAULT_TARGET

    print(f'fetch_ai_topics: calling {model} (web_search max_uses={max_uses}, target={target}) …')
    try:
        text = call_anthropic(api_key, model, max_uses, target)
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        print(f'fetch_ai_topics: WARN HTTP {e.code} from Anthropic API: {body[:300]} — keeping previous entries', file=sys.stderr)
        return 0
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        print(f'fetch_ai_topics: WARN network error: {e} — keeping previous entries', file=sys.stderr)
        return 0

    parsed = extract_json(text)
    if not parsed or not isinstance(parsed, dict) or 'entries' not in parsed:
        print('fetch_ai_topics: WARN could not extract entries[] from model reply — keeping previous entries', file=sys.stderr)
        # Save raw reply for debugging
        with open(os.path.join(ROOT, 'ai_topics_last_raw.txt'), 'w', encoding='utf-8') as f:
            f.write(text or '(empty)')
        return 0

    entries = sanitize(parsed.get('entries') or [])
    if not entries:
        print('fetch_ai_topics: WARN sanitized entries empty — keeping previous entries', file=sys.stderr)
        return 0

    # Load and update data_v3.json in place
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    now_jst = dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).isoformat(timespec='seconds')
    data['ai_topics'] = {
        'generated_at': now_jst,
        'model': model,
        'entries': entries,
    }

    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

    print(f'fetch_ai_topics: wrote {len(entries)} entries → ai_topics (model={model})')
    return 0


if __name__ == '__main__':
    sys.exit(main())
