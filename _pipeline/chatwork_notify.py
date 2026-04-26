#!/usr/bin/env python3
"""
chatwork_notify.py — Send weekly LLMO dashboard update notification to ChatWork.

Reads diff figures from data_v3.json's `diff` key, drafts a 2-3 sentence summary
per tab plus an overall headline, and POSTs the message to a ChatWork room via
the official API.

Required env vars (or CLI args):
  CHATWORK_API_TOKEN   — your ChatWork API token
  CHATWORK_ROOM_ID     — destination room ID
  DASHBOARD_URL        — public URL of the dashboard (default: GitHub Pages link)

Usage:
  python3 chatwork_notify.py
  python3 chatwork_notify.py --token XXX --room-id 12345 --url https://...
  python3 chatwork_notify.py --dry-run    # print message without sending
"""

from __future__ import annotations
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(ROOT, 'data_v3.json')
DEFAULT_URL = 'https://hibiki-nabetani-ideatech.github.io/ideatech-llmo-dashboard/#diff'


def fmt_num(n) -> str:
    if n is None:
        return '—'
    try:
        if isinstance(n, float):
            return f'{n:+,.1f}' if n < 0 else f'{n:,.1f}'
        return f'{int(n):,}'
    except (TypeError, ValueError):
        return str(n)


def fmt_signed(n) -> str:
    if n is None:
        return '—'
    try:
        v = float(n)
        if v == 0:
            return '±0'
        sign = '+' if v > 0 else ''
        if v == int(v):
            return f'{sign}{int(v):,}'
        return f'{sign}{v:,.1f}'
    except (TypeError, ValueError):
        return str(n)


def fmt_pct(p) -> str:
    if p is None:
        return '—'
    try:
        return f'{p*100:+.1f}%'
    except (TypeError, ValueError):
        return str(p)


def build_message(data: dict, url: str) -> str:
    diff = data.get('diff') or {}
    if not diff.get('has_prev'):
        return (
            f'[toall]\n'
            f'[info][title]IDEATECH LLMO ダッシュボード 週次更新[/title]'
            f'今週の差分: 初回スナップショット取得済み（前週データなし）。'
            f'来週月曜から週次の流入/CV増分・推奨ステータス変化・新規サイテーションを反映します。\n'
            f'{url}[/info]'
        )

    flow_latest = (diff.get('flow') or {}).get('site_total', {}).get('latest_month') or {}
    flow_ai_latest = (diff.get('flow') or {}).get('ai_total', {}).get('latest_month') or {}
    ai_ratio_latest = (diff.get('flow') or {}).get('ai_ratio', {}).get('latest_month') or {}
    cv_latest = (diff.get('cv') or {}).get('cv_site_total', {}).get('latest_month') or {}
    cv_ai_latest = (diff.get('cv') or {}).get('cv_ai_total', {}).get('latest_month') or {}

    flips = (diff.get('prompts') or {}).get('flips_summary') or {}
    flips_total = flips.get('total') or 0
    flips_gain = flips.get('gained') or 0
    flips_lost = flips.get('lost') or 0

    resp_cnt = (diff.get('prompts') or {}).get('response_changes_count') or 0

    cit_i = diff.get('citation_ideatech') or {}
    cit_r = diff.get('citation_risapy') or {}
    new_i = cit_i.get('count_new') or 0
    new_r = cit_r.get('count_new') or 0
    new_high_i = cit_i.get('count_new_high') or 0
    new_high_r = cit_r.get('count_new_high') or 0

    # Build per-tab summaries
    lines = []
    # ② 流入
    if flow_latest.get('current') is not None:
        m = flow_latest.get('month') or '直近月'
        d = flow_latest.get('delta')
        p = flow_latest.get('pct_change')
        ai_d = flow_ai_latest.get('delta')
        ai_p = flow_ai_latest.get('pct_change')
        flow_line = f'② 流入: {m} サイト全体 {fmt_signed(d)}件（{fmt_pct(p)}）'
        if ai_d is not None:
            flow_line += f' / AI経由 {fmt_signed(ai_d)}件（{fmt_pct(ai_p)}）'
        lines.append(flow_line)

    # ② CV
    if cv_latest.get('current') is not None or cv_ai_latest.get('current') is not None:
        cv_line_parts = []
        if cv_latest.get('current') is not None:
            cv_line_parts.append(f'全体 {fmt_signed(cv_latest.get("delta"))}件（{fmt_pct(cv_latest.get("pct_change"))}）')
        if cv_ai_latest.get('current') is not None:
            cv_line_parts.append(f'AI経由 {fmt_signed(cv_ai_latest.get("delta"))}件（{fmt_pct(cv_ai_latest.get("pct_change"))}）')
        if cv_line_parts:
            lines.append(f'② CV: ' + ' / '.join(cv_line_parts))

    # ③ 推奨ステータス flip
    if flips_total > 0:
        lines.append(f'③ 推奨ステータス変化: {flips_total}件（獲得 {flips_gain} / 喪失 {flips_lost}）')
    else:
        lines.append('③ 推奨ステータス変化: なし')

    # ③ 応答内容差分
    if resp_cnt > 0:
        lines.append(f'③ 応答内容の差分: {resp_cnt}ケース（プロンプト×LLM）')

    # ④ サイテーション
    cit_parts = []
    if new_i > 0:
        cit_parts.append(f'IDEATECH +{new_i}件' + (f'（高DR70+ {new_high_i}件）' if new_high_i else ''))
    if new_r > 0:
        cit_parts.append(f'リサピー +{new_r}件' + (f'（高DR70+ {new_high_r}件）' if new_high_r else ''))
    if cit_parts:
        lines.append(f'④ 新規サイテーション: ' + ' / '.join(cit_parts))
    else:
        lines.append('④ 新規サイテーション: なし')

    # Headline — mirror the dashboard 概況 logic (build_html_v3.py renderDiff)
    new_cit_tot = new_i + new_r
    summary_parts = []
    if flow_latest.get('current') is not None and flow_latest.get('previous') is not None:
        d = flow_latest.get('delta') or 0
        dir_t = '増加' if d > 0 else ('減少' if d < 0 else '横ばい')
        summary_parts.append(
            f'直近月 {flow_latest.get("month") or "—"} のサイト全体流入は '
            f'{fmt_num(flow_latest.get("current"))}件'
            f'（前週スナップショット比 {fmt_signed(flow_latest.get("delta"))}件 / '
            f'{fmt_pct(flow_latest.get("pct_change"))}）で{dir_t}'
        )
    if flow_ai_latest.get('current') is not None or flow_ai_latest.get('previous') is not None:
        ad = flow_ai_latest.get('delta') or 0
        ai_dir = '増加' if ad > 0 else ('減少' if ad < 0 else '横ばい')
        ratio_str = ''
        if ai_ratio_latest.get('current') is not None:
            ratio_str = f'／AI経由比率 {fmt_pct(ai_ratio_latest.get("current"))}'
        summary_parts.append(
            f'うちAI経由流入は {fmt_num(flow_ai_latest.get("current") or 0)}件'
            f'（{fmt_signed(flow_ai_latest.get("delta"))}件 / '
            f'{fmt_pct(flow_ai_latest.get("pct_change"))}）で{ai_dir}{ratio_str}'
        )
    if cv_latest.get('current') is not None or cv_latest.get('previous') is not None:
        summary_parts.append(
            f'同月CVは {fmt_num(cv_latest.get("current") or 0)}件'
            f'（{fmt_signed(cv_latest.get("delta"))}件）'
        )
    if cv_ai_latest.get('current') is not None or cv_ai_latest.get('previous') is not None:
        summary_parts.append(
            f'うちAI経由CVは {fmt_num(cv_ai_latest.get("current") or 0)}件'
            f'（{fmt_signed(cv_ai_latest.get("delta"))}件）'
        )
    if flips_total > 0:
        summary_parts.append(f'推奨ステータスは {flips_total}件 flip（獲得 {flips_gain} / 喪失 {flips_lost}）')
    else:
        summary_parts.append('推奨ステータスの変化はなし')
    if new_cit_tot > 0:
        summary_parts.append(f'新規サイテーション {new_cit_tot}件（IDEATECH {new_i} / リサピー {new_r}）')
    else:
        summary_parts.append('新規サイテーションはなし')
    if resp_cnt > 0:
        summary_parts.append(f'応答内容の差分 {resp_cnt}ケースを③タブに格納')

    headline = '。'.join(summary_parts) + '。' if summary_parts else '前週から目立った変化はありませんでした。'

    body = '\n'.join(lines)

    msg = (
        f'[toall]\n'
        f'[info][title]IDEATECH LLMO ダッシュボード 週次更新[/title]'
        f'■ 今週のサマリ\n{headline}\n\n'
        f'■ タブ別の主な変化\n{body}\n\n'
        f'■ ダッシュボード（前週比 差分タブ）\n{url}[/info]'
    )
    return msg


def post_to_chatwork(token: str, room_id: str, body: str) -> dict:
    url = f'https://api.chatwork.com/v2/rooms/{room_id}/messages'
    data = urllib.parse.urlencode({'body': body, 'self_unread': '0'}).encode('utf-8')
    req = urllib.request.Request(url, data=data, method='POST')
    req.add_header('X-ChatWorkToken', token)
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    with urllib.request.urlopen(req, timeout=20) as resp:
        raw = resp.read().decode('utf-8')
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {'raw': raw, 'status': resp.status}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--token', default=os.environ.get('CHATWORK_API_TOKEN', ''))
    ap.add_argument('--room-id', dest='room_id', default=os.environ.get('CHATWORK_ROOM_ID', ''))
    ap.add_argument('--url', default=os.environ.get('DASHBOARD_URL', DEFAULT_URL))
    ap.add_argument('--data', default=DATA_PATH)
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    with open(args.data, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Always link to the diff section, even if the env var was set without an anchor.
    # Note: the dashboard's tab router reads location.hash and looks up #sec-${hash},
    # so the correct fragment is "#diff" (NOT "#sec-diff").
    url = args.url or DEFAULT_URL
    if '#' not in url:
        url = url.rstrip('/') + '/#diff'
    elif url.endswith('#sec-diff'):
        # Auto-correct legacy/typo anchor.
        url = url[:-len('#sec-diff')] + '#diff'

    msg = build_message(data, url)

    if args.dry_run:
        print('--- DRY RUN: would send the following body ---')
        print(msg)
        print('--- end ---')
        return

    if not args.token or not args.room_id:
        print('ERR: --token and --room-id (or env CHATWORK_API_TOKEN / CHATWORK_ROOM_ID) required.', file=sys.stderr)
        sys.exit(2)

    res = post_to_chatwork(args.token, args.room_id, msg)
    print(json.dumps(res, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
