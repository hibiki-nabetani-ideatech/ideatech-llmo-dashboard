#!/usr/bin/env python3
"""
fetch_ai_topics.py — Generate the weekly "AI Topics" feed for the dashboard's
⑤ AI Topics tab.

Two modes, picked automatically:

  * BACKFILL mode — runs once when `data_v3.json["ai_topics"]["_backfilled"]`
    is not True. Iterates over half-year windows from BACKFILL_START (default
    2024-01) up to the current month, asking the model for ~25 entries per
    window. Saves progress incrementally so a workflow timeout still leaves
    a populated dashboard. Sets `_backfilled: true` once at least one window
    completed.

  * WEEKLY mode — runs every subsequent invocation. Asks for ~12 entries from
    the past 7-10 days and prepends them to the existing list (de-duped by
    URL). Older historical entries are kept indefinitely.

Both modes call the Anthropic Messages API (`web_search_20250305` tool
enabled) and write the result into `data_v3.json` under the `ai_topics` key.

Schema of `data_v3.json["ai_topics"]`:
{
  "generated_at":   "<ISO8601 JST>",
  "model":          "<model id>",
  "_backfilled":    true,                # set after backfill completes
  "_backfill_done_through": "2026-04",   # last fully-fetched window end
  "entries": [
    {
      "date":        "YYYY-MM-DD",
      "ai":          "OpenAI",
      "topic_tags":  ["新機能", "API"],
      "title":       "...",
      "summary":     "...",
      "url":         "https://...",
      "reactions":   {"summary": "...",
                      "sources": [{"label":"X","url":"..."}, ...]}
    },
    ...
  ]
}

Required env:
  ANTHROPIC_API_KEY

Optional env:
  AI_TOPICS_MODEL                — default 'claude-sonnet-4-5'
  AI_TOPICS_MAX_USES             — web_search max_uses for weekly, default 8
  AI_TOPICS_BACKFILL_MAX_USES    — web_search max_uses for backfill, default 12
  AI_TOPICS_TARGET_COUNT         — weekly target, default 12
  AI_TOPICS_BACKFILL_TARGET      — per-window backfill target, default 25
  AI_TOPICS_BACKFILL_START       — backfill start month YYYY-MM, default 2024-01
  AI_TOPICS_FORCE_BACKFILL       — set to '1' to re-run backfill from scratch
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
DEFAULT_BACKFILL_MAX_USES = 12
DEFAULT_TARGET = 12
DEFAULT_BACKFILL_TARGET = 25
DEFAULT_BACKFILL_START = '2024-01'

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


# ---------- prompts ----------

_OUTPUT_SCHEMA = """```json
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
```"""

_CONSTRAINTS = """【制約】
- ai は次のいずれか: {allowed_ais}
- topic_tags は次から1〜3個選ぶ: {allowed_tags}
- title / summary / reactions.summary は日本語で記述。
- date は YYYY-MM-DD（ニュースの公開日）。指定期間内の日付であること。
- url は実在する一次ソース（公式blog or 大手メディア）。
- reactions.sources は1〜3件、可能なら実在URL。見つからない場合は空配列でOK。
- 同じ会社のニュースに偏らないよう、最低でも5社以上カバーすること。"""

WEEKLY_SYSTEM = """あなたは日本のB2B監査法人IDEATECH向けに「主要AIプロダクトの週次ニュース」を編集する調査アシスタントです。

【任務】
過去7〜10日間に公開された、AI業界の重要ニュースを {target_count} 件選んでまとめてください。
対象: OpenAI / Anthropic / Google (Gemini, NotebookLM等) / Microsoft (Copilot等) / Perplexity / Meta / xAI (Grok) / Mistral / DeepSeek / Cohere / 国内AI（Felo, ELYZA, Sakana AI等）。
重要度の優先順位: ① プロダクト発表・新機能リリース ② 料金/契約条件の変更 ③ 重要なパートナーシップ ④ 安全性・規制関連 ⑤ 注目論文・ベンチマーク ⑥ 人事・組織の重要動向。

【web_searchツールの使い方】
複数回検索してください。最初は各社の公式ブログ/プレスリリース。次にニュースアグリゲータ（TechCrunch, VentureBeat, The Verge, ITmedia等）。最後に「世間の反応」のためにX（Twitter）議論、Reddit (r/LocalLLaMA, r/singularity, r/OpenAI, r/ClaudeAI等), Hacker News のスレッドを軽く確認。

【出力】
最終回答は **必ず以下のフォーマットの```json コードブロック1つだけ** を返すこと。前置き・後書き・解説は不要。

""" + _OUTPUT_SCHEMA + """

""" + _CONSTRAINTS

BACKFILL_SYSTEM = """あなたは日本のB2B監査法人IDEATECH向けに「主要AIプロダクトのニュース履歴」を編集する調査アシスタントです。

【任務】
{period_start} 〜 {period_end} の期間に公開された、AI業界の重要ニュースを {target_count} 件選んでまとめてください。
対象: OpenAI / Anthropic / Google (Gemini, NotebookLM等) / Microsoft (Copilot等) / Perplexity / Meta / xAI (Grok) / Mistral / DeepSeek / Cohere / 国内AI（Felo, ELYZA, Sakana AI等）。
重要度の優先順位: ① 大型プロダクト発表（新モデル/新機能リリース） ② 料金/契約条件の変更 ③ 重要なパートナーシップ ④ 安全性・規制関連 ⑤ 注目論文・ベンチマーク ⑥ 人事・組織の重要動向。

【web_searchツールの使い方】
複数回検索してください。期間を絞った検索クエリ（例: "OpenAI announcement {period_start}", "Claude release {period_end}"）を活用。最初は各社の公式ブログ/プレスリリース、次に大手メディア（TechCrunch, The Verge, VentureBeat, ITmedia等）。当時のXやReddit/HNの議論も軽く確認して「世間の反応」を埋めてください。

【出力】
最終回答は **必ず以下のフォーマットの```json コードブロック1つだけ** を返すこと。前置き・後書き・解説は不要。

""" + _OUTPUT_SCHEMA + """

""" + _CONSTRAINTS + """

【追加制約】
- date は必ず {period_start} 〜 {period_end} の範囲内であること。
- 期間が古いほどreactions欄は埋まりにくいですが、できる範囲で残してください。"""


# ---------- API ----------

def _post(api_key: str, payload: dict, timeout: int = 240) -> str:
    data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(ANTHROPIC_URL, data=data, method='POST')
    req.add_header('x-api-key', api_key)
    req.add_header('anthropic-version', '2023-06-01')
    req.add_header('content-type', 'application/json')
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode('utf-8')
    obj = json.loads(raw)
    chunks = []
    for block in obj.get('content', []):
        if isinstance(block, dict) and block.get('type') == 'text':
            chunks.append(block.get('text', ''))
    return '\n'.join(chunks)


def call_weekly(api_key: str, model: str, max_uses: int, target_count: int) -> str:
    payload = {
        'model': model,
        'max_tokens': 8000,
        'system': WEEKLY_SYSTEM.format(
            target_count=target_count,
            allowed_ais=' / '.join(ALLOWED_AIS),
            allowed_tags=' / '.join(ALLOWED_TAGS),
        ),
        'tools': [{'type': 'web_search_20250305', 'name': 'web_search', 'max_uses': max_uses}],
        'messages': [{'role': 'user', 'content': f'過去7〜10日のAI業界ニュースを{target_count}件、上記フォーマットのJSONで返してください。'}],
    }
    return _post(api_key, payload)


def call_backfill_window(api_key: str, model: str, max_uses: int, target_count: int,
                         period_start: str, period_end: str) -> str:
    payload = {
        'model': model,
        'max_tokens': 12000,
        'system': BACKFILL_SYSTEM.format(
            target_count=target_count,
            period_start=period_start,
            period_end=period_end,
            allowed_ais=' / '.join(ALLOWED_AIS),
            allowed_tags=' / '.join(ALLOWED_TAGS),
        ),
        'tools': [{'type': 'web_search_20250305', 'name': 'web_search', 'max_uses': max_uses}],
        'messages': [{'role': 'user', 'content': f'{period_start} 〜 {period_end} のAI業界ニュースを{target_count}件、上記フォーマットのJSONで返してください。'}],
    }
    return _post(api_key, payload, timeout=300)


# ---------- parse / sanitize ----------

def extract_json(text: str) -> dict | None:
    if not text:
        return None
    m = re.search(r'```json\s*(\{.*?\})\s*```', text, re.S)
    raw = m.group(1) if m else None
    if raw is None:
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
            continue
        out.append({
            'date': date,
            'ai': ai or 'その他',
            'topic_tags': tags,
            'title': title,
            'summary': summary,
            'url': url,
            'reactions': {'summary': r_sum, 'sources': r_src},
        })
    return out


def merge_dedupe(existing: list, fresh: list) -> list:
    """Combine two entry lists; dedupe by URL (case-insensitive). Newest first."""
    seen = set()
    out = []
    for e in (fresh + existing):  # fresh wins on duplicate URL
        u = (e.get('url') or '').strip().lower()
        if not u or u in seen:
            continue
        seen.add(u)
        out.append(e)
    out.sort(key=lambda x: x.get('date') or '', reverse=True)
    return out


# ---------- backfill orchestration ----------

def _parse_yyyy_mm(s: str) -> tuple[int, int]:
    m = re.match(r'^(\d{4})-(\d{1,2})$', (s or '').strip())
    if not m:
        raise ValueError(f'expected YYYY-MM, got {s!r}')
    return int(m.group(1)), int(m.group(2))


def _add_months(year: int, month: int, delta: int) -> tuple[int, int]:
    idx = (year * 12 + (month - 1)) + delta
    return idx // 12, (idx % 12) + 1


def build_backfill_windows(start: str, today: dt.date) -> list[tuple[str, str]]:
    """Half-year windows from `start` to the month containing `today`."""
    sy, sm = _parse_yyyy_mm(start)
    cur_y, cur_m = sy, sm
    today_y, today_m = today.year, today.month
    windows = []
    while (cur_y, cur_m) <= (today_y, today_m):
        # 6-month window: cur ... cur+5 (capped at today)
        end_y, end_m = _add_months(cur_y, cur_m, 5)
        if (end_y, end_m) > (today_y, today_m):
            end_y, end_m = today_y, today_m
        windows.append((f'{cur_y:04d}-{cur_m:02d}', f'{end_y:04d}-{end_m:02d}'))
        cur_y, cur_m = _add_months(end_y, end_m, 1)
    return windows


def _save(data: dict) -> None:
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)


def _now_jst_iso() -> str:
    return dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).isoformat(timespec='seconds')


def _load_data() -> dict:
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


# ---------- main ----------

def run_weekly(data: dict, api_key: str, model: str) -> int:
    try:
        max_uses = int(os.environ.get('AI_TOPICS_MAX_USES') or DEFAULT_MAX_USES)
    except ValueError:
        max_uses = DEFAULT_MAX_USES
    try:
        target = int(os.environ.get('AI_TOPICS_TARGET_COUNT') or DEFAULT_TARGET)
    except ValueError:
        target = DEFAULT_TARGET

    print(f'fetch_ai_topics[weekly]: calling {model} (max_uses={max_uses}, target={target}) …')
    try:
        text = call_weekly(api_key, model, max_uses, target)
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        print(f'fetch_ai_topics[weekly]: WARN HTTP {e.code}: {body[:300]} — keeping previous entries', file=sys.stderr)
        return 0
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        print(f'fetch_ai_topics[weekly]: WARN network error: {e} — keeping previous entries', file=sys.stderr)
        return 0

    parsed = extract_json(text)
    if not parsed or 'entries' not in parsed:
        print('fetch_ai_topics[weekly]: WARN parse failed — keeping previous entries', file=sys.stderr)
        with open(os.path.join(ROOT, 'ai_topics_last_raw.txt'), 'w', encoding='utf-8') as f:
            f.write(text or '(empty)')
        return 0

    fresh = sanitize(parsed.get('entries') or [])
    if not fresh:
        print('fetch_ai_topics[weekly]: WARN sanitized fresh entries empty — keeping previous', file=sys.stderr)
        return 0

    existing = (data.get('ai_topics') or {}).get('entries') or []
    combined = merge_dedupe(existing, fresh)
    data['ai_topics'] = {
        **(data.get('ai_topics') or {}),
        'generated_at': _now_jst_iso(),
        'model': model,
        'entries': combined,
    }
    _save(data)
    print(f'fetch_ai_topics[weekly]: +{len(fresh)} fresh, total {len(combined)} (after dedupe)')
    return 0


def run_backfill(data: dict, api_key: str, model: str) -> int:
    try:
        max_uses = int(os.environ.get('AI_TOPICS_BACKFILL_MAX_USES') or DEFAULT_BACKFILL_MAX_USES)
    except ValueError:
        max_uses = DEFAULT_BACKFILL_MAX_USES
    try:
        target = int(os.environ.get('AI_TOPICS_BACKFILL_TARGET') or DEFAULT_BACKFILL_TARGET)
    except ValueError:
        target = DEFAULT_BACKFILL_TARGET
    start = os.environ.get('AI_TOPICS_BACKFILL_START') or DEFAULT_BACKFILL_START

    today = dt.date.today()
    windows = build_backfill_windows(start, today)
    state = data.get('ai_topics') or {}
    done_through = state.get('_backfill_done_through')  # last completed window end (YYYY-MM)

    # Skip already-completed windows
    if done_through:
        try:
            dy, dm = _parse_yyyy_mm(done_through)
        except ValueError:
            dy, dm = (0, 0)
        windows = [w for w in windows if _parse_yyyy_mm(w[1]) > (dy, dm)]

    print(f'fetch_ai_topics[backfill]: {len(windows)} window(s) to process: {windows}')
    if not windows:
        # Nothing to do — mark backfill complete
        ai_topics = data.get('ai_topics') or {}
        ai_topics['_backfilled'] = True
        ai_topics['generated_at'] = _now_jst_iso()
        ai_topics['model'] = model
        data['ai_topics'] = ai_topics
        _save(data)
        return 0

    completed_any = False
    for (ws, we) in windows:
        print(f'fetch_ai_topics[backfill]: window {ws} 〜 {we} (target={target}) …')
        try:
            text = call_backfill_window(api_key, model, max_uses, target, ws, we)
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8', errors='replace')
            print(f'fetch_ai_topics[backfill]: WARN HTTP {e.code} in {ws}-{we}: {body[:300]}', file=sys.stderr)
            continue
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            print(f'fetch_ai_topics[backfill]: WARN network error in {ws}-{we}: {e}', file=sys.stderr)
            continue

        parsed = extract_json(text)
        if not parsed or 'entries' not in parsed:
            print(f'fetch_ai_topics[backfill]: WARN parse failed in {ws}-{we}', file=sys.stderr)
            with open(os.path.join(ROOT, f'ai_topics_backfill_raw_{ws}.txt'), 'w', encoding='utf-8') as f:
                f.write(text or '(empty)')
            continue

        fresh = sanitize(parsed.get('entries') or [])
        if not fresh:
            print(f'fetch_ai_topics[backfill]: WARN no entries in {ws}-{we}', file=sys.stderr)
            continue

        # Save incrementally so a workflow timeout still preserves progress
        existing = (data.get('ai_topics') or {}).get('entries') or []
        combined = merge_dedupe(existing, fresh)
        data['ai_topics'] = {
            **(data.get('ai_topics') or {}),
            'generated_at': _now_jst_iso(),
            'model': model,
            'entries': combined,
            '_backfill_done_through': we,
        }
        _save(data)
        completed_any = True
        print(f'fetch_ai_topics[backfill]:   +{len(fresh)} entries from {ws}-{we}, total {len(combined)}')

    # Mark fully complete if we processed all originally-pending windows
    if completed_any:
        ai_topics = data.get('ai_topics') or {}
        last_we = windows[-1][1] if windows else None
        # Check if we got to the last requested window's end
        if ai_topics.get('_backfill_done_through') == last_we:
            ai_topics['_backfilled'] = True
            data['ai_topics'] = ai_topics
            _save(data)
            print('fetch_ai_topics[backfill]: ✓ backfill complete; weekly mode active from next run')
        else:
            print(f'fetch_ai_topics[backfill]: partial completion (through {ai_topics.get("_backfill_done_through")}); next run will resume')
    return 0


def main() -> int:
    api_key = (os.environ.get('ANTHROPIC_API_KEY') or '').strip()
    if not api_key:
        print('fetch_ai_topics: ANTHROPIC_API_KEY unset — skipping (existing ai_topics retained)')
        return 0

    model = os.environ.get('AI_TOPICS_MODEL') or DEFAULT_MODEL
    data = _load_data()
    state = data.get('ai_topics') or {}
    force = os.environ.get('AI_TOPICS_FORCE_BACKFILL', '').strip() == '1'
    needs_backfill = force or not state.get('_backfilled')

    if needs_backfill:
        if force:
            print('fetch_ai_topics: AI_TOPICS_FORCE_BACKFILL=1 — running backfill from scratch')
            # Clear progress markers but preserve existing entries (will be deduped)
            state.pop('_backfilled', None)
            state.pop('_backfill_done_through', None)
            data['ai_topics'] = state
        return run_backfill(data, api_key, model)
    else:
        return run_weekly(data, api_key, model)


if __name__ == '__main__':
    sys.exit(main())
