#!/usr/bin/env python3
"""V3 IDEATECH LLMO Dashboard HTML builder — Digital Agency guideline style."""
import argparse
import json
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_AP = argparse.ArgumentParser()
_AP.add_argument('--data', default=os.path.join(_HERE, 'data_v3.json'),
                 help='Path to data_v3.json (default: alongside this script)')
_AP.add_argument('--out', default=os.path.join(_HERE, '..', 'index.html'),
                 help='Output HTML path (default: ../index.html — repo root)')
_ARGS, _ = _AP.parse_known_args()

with open(_ARGS.data, 'r', encoding='utf-8') as f:
    DATA = json.load(f)

DATA_JSON = json.dumps(DATA, ensure_ascii=False, separators=(',', ':'))

HTML = r"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow,noarchive,noimageindex">
<meta name="googlebot" content="noindex,nofollow,noarchive,noimageindex">
<title>IDEATECH LLMO Dashboard</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>
:root{
  --bg:#f5f6f8;
  --panel:#ffffff;
  --ink:#212121;
  --ink2:#595959;
  --ink3:#8a8d93;
  --line:#d9d9d9;
  --line-soft:#ededed;
  --grid:#ededed;
  --cell-bg:#fafafa;
  --blue:#0017c1;
  --blue-soft:#e8eaf6;
  --blue-mid:#7986cb;
  --up:#0a8054;
  --down:#c0392b;
  --warn:#b86a00;
  /* Categorical (blue scale) */
  --cat-1:#0017c1;
  --cat-2:#3949ab;
  --cat-3:#7986cb;
  --cat-4:#a3b1d4;
  /* LLM brand (used only inside ③ prompts) */
  --chatgpt:#10a37f;
  --gemini:#4285f4;
  --copilot:#0078d4;
  --perplex:#20c997;
}
*{box-sizing:border-box}
html,body{margin:0;padding:0;background:var(--bg);color:var(--ink);font-family:-apple-system,"Hiragino Kaku Gothic ProN","Yu Gothic UI",Meiryo,sans-serif;font-size:13.5px;line-height:1.7;-webkit-font-smoothing:antialiased}
a{color:var(--blue);text-decoration:none}
a:hover{text-decoration:underline}

/* ===== Layout ===== */
.app{display:flex;min-height:100vh}
.sidebar{width:248px;flex-shrink:0;background:#fff;border-right:1px solid var(--line);position:sticky;top:0;align-self:flex-start;height:100vh;overflow-y:auto}
.sidebar .brand{padding:22px 22px 18px;border-bottom:1px solid var(--line-soft)}
.sidebar .brand .b-title{font-weight:700;font-size:15px;color:var(--ink);letter-spacing:.01em}
.sidebar .brand .b-sub{display:block;color:var(--ink2);font-weight:400;font-size:11px;margin-top:3px}
.nav-group{padding:14px 12px 8px;border-bottom:1px solid var(--line-soft)}
.nav-group:last-child{border-bottom:0}
.nav-group-title{font-size:10.5px;color:var(--ink3);letter-spacing:.06em;padding:0 10px 6px;font-weight:700;text-transform:uppercase}
.nav-btn{display:flex;align-items:center;gap:8px;width:100%;text-align:left;padding:8px 12px;margin:1px 0;border:0;background:transparent;color:var(--ink);font:inherit;border-radius:4px;cursor:pointer;font-size:13px}
.nav-btn:hover{background:var(--cell-bg)}
.nav-btn.active{background:var(--blue);color:#fff;font-weight:600}
.nav-btn .nav-num{display:inline-flex;align-items:center;justify-content:center;width:18px;height:18px;border-radius:50%;background:var(--blue-soft);color:var(--blue);font-size:10px;font-weight:700;flex-shrink:0}
.nav-btn.active .nav-num{background:rgba(255,255,255,.25);color:#fff}
main{flex:1;min-width:0;padding:0;background:var(--bg)}

/* ===== Page header ===== */
.page-header{background:#fff;border-bottom:1px solid var(--line);padding:22px 32px 18px}
.page-header h1{font-size:20px;margin:0 0 4px;font-weight:700;letter-spacing:-.01em}
.page-header .sub{color:var(--ink2);font-size:12.5px}
.page-header .as-of{display:inline-block;margin-left:12px;background:var(--blue-soft);color:var(--blue);font-size:11px;font-weight:600;padding:2px 8px;border-radius:4px}

/* ===== Sections ===== */
.section{display:none;padding:24px 32px 60px;max-width:1280px}
.section.active{display:block}

/* Section hero (answer-first header) */
.sec-hero{background:#fff;border:1px solid var(--line);border-left:4px solid var(--blue);border-radius:4px;padding:18px 22px;margin-bottom:18px}
.sec-hero .crumb{font-size:11px;color:var(--ink2);letter-spacing:.04em;margin-bottom:4px}
.sec-hero .crumb b{color:var(--ink);font-weight:600}
.sec-hero h2{margin:0 0 6px;font-size:20px;font-weight:700;line-height:1.45;color:var(--ink);letter-spacing:-.01em}
.sec-hero h2 .answer{color:var(--blue)}
.sec-hero h2 .sub-h{display:block;font-weight:500;font-size:14px;color:var(--ink2);margin-top:4px}
.sec-hero .lead{font-size:12.5px;color:var(--ink2);margin:8px 0 0;border-left:3px solid var(--blue-soft);padding:2px 0 2px 10px;line-height:1.6}
/* Tab-level summary (2-3 sentences) shown right under sec-hero */
.tab-summary{background:#fff;border:1px solid var(--line);border-left:4px solid var(--cat-3);border-radius:4px;padding:12px 16px;margin:-6px 0 18px;font-size:12.5px;line-height:1.75;color:var(--ink)}
.tab-summary .ts-label{display:inline-block;font-size:10.5px;font-weight:700;color:#fff;background:var(--cat-3);padding:2px 8px;border-radius:3px;margin-right:8px;letter-spacing:.04em;vertical-align:1px}
.tab-summary b{color:var(--ink);font-weight:700}
.tab-summary .hl-num{color:var(--blue);font-weight:700;font-variant-numeric:tabular-nums}

/* ===== Card ===== */
.card{background:var(--panel);border:1px solid var(--line);border-radius:4px;padding:18px 20px;margin-bottom:14px}
.card h3{font-size:14px;margin:0 0 4px;font-weight:700;color:var(--ink);display:inline-block;padding-bottom:6px;border-bottom:2px solid var(--blue)}
.card .h3-sub{font-size:11.5px;color:var(--ink2);margin:2px 0 12px}
.card h4{font-size:12.5px;margin:14px 0 6px;font-weight:600;color:var(--ink)}

/* ===== KPI ===== */
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px;margin-bottom:14px}
.kpi{background:var(--cell-bg);border:1px solid var(--line);border-radius:4px;padding:14px 16px}
.kpi.primary{background:#fff;border-left:3px solid var(--blue)}
.kpi .label{font-size:11px;color:var(--ink2);font-weight:500;line-height:1.4}
.kpi .value{font-size:24px;font-weight:700;margin-top:4px;letter-spacing:-.02em;line-height:1.2}
.kpi .value .unit{font-size:12px;color:var(--ink2);font-weight:500;margin-left:2px}
.kpi .delta{font-size:11px;margin-top:6px;display:flex;align-items:center;gap:5px;line-height:1.3}
.delta-up{color:var(--up)}
.delta-down{color:var(--down)}
.delta-flat{color:var(--ink3)}
.delta-arrow{display:inline-block;width:0;height:0;flex-shrink:0}
.delta-up .delta-arrow{border-left:4px solid transparent;border-right:4px solid transparent;border-bottom:6px solid var(--up)}
.delta-down .delta-arrow{border-left:4px solid transparent;border-right:4px solid transparent;border-top:6px solid var(--down)}

/* ===== Tables ===== */
table{width:100%;border-collapse:collapse;font-size:12px}
th,td{border-bottom:1px solid var(--line-soft);padding:6px 10px;text-align:left;vertical-align:top;line-height:1.45}
th{background:var(--cell-bg);font-weight:600;color:var(--ink2);font-size:11px;white-space:nowrap;border-bottom:1px solid var(--line);letter-spacing:.02em}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
.table-wrap{overflow-x:auto;border:1px solid var(--line);border-radius:4px}
.table-wrap table{font-size:12px}
.table-wrap th{position:sticky;top:0;z-index:1}

/* ===== Time-series tables (SS/CV summary & group breakdown) — fix row heights for 36-month timeline ===== */
/* Common: tighter padding, middle-aligned, consistent line-height */
#tbl-series-ss th, #tbl-series-cv th, #tbl-flow-groups th, #tbl-cv-groups th,
#tbl-series-ss td, #tbl-series-cv td, #tbl-flow-groups td, #tbl-cv-groups td{padding:5px 8px;line-height:1.35;vertical-align:middle}
/* Numeric month columns: prevent wrap, consistent width */
#tbl-series-ss td.num, #tbl-series-cv td.num,
#tbl-flow-groups td.num, #tbl-cv-groups td.num{min-width:46px;white-space:nowrap}
/* SS/CV summary: item name column — allow up to 2 lines, force enough width */
#tbl-series-ss tbody td:first-child,
#tbl-series-cv tbody td:first-child,
#tbl-series-ss thead th:first-child,
#tbl-series-cv thead th:first-child{
  min-width:160px;max-width:200px;
  white-space:normal;word-break:keep-all;overflow-wrap:break-word;
  line-height:1.3;
}
/* Group breakdown: category cell (colspan=2) — keep label visible (allows the inserted <br>） to wrap to 2 lines) */
#tbl-flow-groups td.cat-cell, #tbl-cv-groups td.cat-cell{
  white-space:normal;word-break:keep-all;line-height:1.3;
  min-width:240px;
}
/* Group breakdown: LLM name column — short ASCII, 1 line */
#tbl-flow-groups td.llm-name, #tbl-cv-groups td.llm-name{white-space:nowrap;min-width:100px}
/* Group breakdown: indent (empty first td of LLM rows) */
#tbl-flow-groups tbody td:first-child:empty,
#tbl-cv-groups tbody td:first-child:empty{min-width:120px;padding:0}
/* Year boundary divider (column where year changes) */
#tbl-series-ss .year-start, #tbl-series-cv .year-start,
#tbl-flow-groups .year-start, #tbl-cv-groups .year-start{
  border-left:2px solid #b9c0d4;
}
#tbl-series-ss thead th.year-start, #tbl-series-cv thead th.year-start,
#tbl-flow-groups thead th.year-start, #tbl-cv-groups thead th.year-start{
  border-left:2px solid #8a93b0;
  background:#eef0f6;
}

/* ===== Charts ===== */
.chart-wrap{height:280px;position:relative}
.chart-wrap.sm{height:220px}
.chart-wrap.lg{height:340px}
.chart-note{font-size:11.5px;color:var(--ink2);margin:0 0 10px;line-height:1.5}
.chart-legend{display:flex;flex-wrap:wrap;gap:14px;font-size:11px;color:var(--ink2);margin-top:10px}
.chart-legend .li{display:inline-flex;align-items:center;gap:6px}
.legend-dot{display:inline-block;width:14px;height:3px;border-radius:2px;background:var(--blue)}
.legend-dot.muted{background:#bdbdbd}
.legend-dot.dashed{background:transparent;border-top:2px dashed #999;height:0;width:14px}

/* ===== Diagnostic ===== */
.diag-cat{display:inline-flex;align-items:center;justify-content:center;min-width:24px;height:24px;padding:0 4px;border-radius:4px;background:var(--blue-soft);color:var(--blue);font-weight:700;font-size:11px;margin-right:6px}
.diag-cat.A{background:#e3f2fd;color:#1565c0}
.diag-cat.B{background:#f3e5f5;color:#7b1fa2}
.diag-cat.C{background:#e0f7fa;color:#00838f}
.diag-cat.D{background:#fce4ec;color:#ad1457}
.score-pill{display:inline-block;padding:2px 8px;border-radius:4px;font-weight:700;font-size:11px;min-width:22px;text-align:center}
.score-5{background:#e8f5e9;color:#2e7d32}
.score-4{background:#e3f2fd;color:#1565c0}
.score-3{background:#fff8e1;color:#a36b00}
.score-2{background:#fff3e0;color:#bf5500}
.score-1{background:#ffebee;color:#b3261e}

/* ===== Layout helpers ===== */
.row2col{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.row3col{display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px}
@media (max-width: 980px){.row2col,.row3col{grid-template-columns:1fr}}
.small{font-size:11.5px;color:var(--ink2)}
.muted-text{color:var(--ink2)}

/* ===== Pager / Search ===== */
.toolbar{display:flex;gap:10px;align-items:center;margin-bottom:12px;flex-wrap:wrap}
input[type="text"].search,select.search{border:1px solid var(--line);border-radius:4px;padding:7px 12px;font:inherit;font-size:12.5px;width:280px;max-width:100%;color:var(--ink);background:#fff}
input[type="text"].search:focus,select.search:focus{outline:none;border-color:var(--blue);box-shadow:0 0 0 2px var(--blue-soft)}
.pager{display:flex;gap:8px;align-items:center;margin-top:12px;font-size:12px;color:var(--ink2);flex-wrap:wrap}
.pager button{border:1px solid var(--line);background:#fff;padding:5px 12px;border-radius:4px;cursor:pointer;font:inherit;font-size:12px;color:var(--ink)}
.pager button:hover:not(:disabled){background:var(--blue-soft);border-color:var(--blue);color:var(--blue)}
.pager button:disabled{opacity:.4;cursor:not-allowed}

/* ===== Diff tab (week-over-week) ===== */
.nav-btn-diff{background:linear-gradient(90deg,#fff7e0 0%,#fff 100%)}
.nav-btn-diff .nav-num{background:#ffb300;color:#5a3c00}
.nav-btn-diff.active{background:#f57c00;color:#fff}
.nav-btn-diff.active .nav-num{background:rgba(255,255,255,.3);color:#fff}
.diff-hero{border-left-color:#f57c00}
.diff-hero .crumb b{color:#e65100}
.empty-note{padding:18px;text-align:center;color:var(--ink2);background:var(--cell-bg);border:1px dashed var(--line);border-radius:4px;font-size:12px}
.diff-toolbar{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px}
.diff-toolbar button{border:1px solid var(--line);background:#fff;padding:5px 12px;border-radius:14px;cursor:pointer;font:inherit;font-size:11.5px;color:var(--ink2);white-space:nowrap}
.diff-toolbar button:hover{border-color:var(--blue);color:var(--blue);background:var(--blue-soft)}
.diff-toolbar button.is-active{background:var(--blue);color:#fff;border-color:var(--blue);font-weight:600}
.diff-tabs{display:flex;gap:6px;margin:8px 0 12px;border-bottom:1px solid var(--line);padding-bottom:0}
.diff-cit-tab{border:1px solid var(--line);border-bottom:none;background:#f6f7fa;padding:6px 16px;border-radius:4px 4px 0 0;cursor:pointer;font:inherit;font-size:12px;color:var(--ink2)}
.diff-cit-tab .cnt{display:inline-block;margin-left:6px;padding:1px 7px;border-radius:9px;background:var(--cell-bg);color:var(--ink);font-weight:700;font-size:10.5px;font-variant-numeric:tabular-nums}
.diff-cit-tab.is-active{background:#fff;color:var(--ink);font-weight:600;border-color:var(--line) var(--line) #fff;position:relative;top:1px}
.diff-cit-tab.is-active .cnt{background:var(--blue-soft);color:var(--blue)}
.diff-pill{display:inline-block;padding:1px 9px;border-radius:10px;font-size:11px;font-weight:700;font-variant-numeric:tabular-nums}
.diff-pill.up{background:#e8f5e9;color:#1b5e20}
.diff-pill.down{background:#fde0e0;color:#b71c1c}
.diff-pill.flat{background:#f5f5f5;color:#9e9e9e}
.diff-pill.gain{background:#fff3cd;color:#664d03;box-shadow:inset 0 0 0 1px #ffd54f}
.diff-pill.lost{background:#fce4ec;color:#880e4f;box-shadow:inset 0 0 0 1px #f48fb1}
.diff-arrow{display:inline-block;font-size:11px;color:var(--ink2);margin:0 4px}
.diff-mark{display:inline-block;width:18px;text-align:center;font-weight:700}
.diff-mark.r2{color:var(--up)}
.diff-mark.r1{color:var(--warn)}
.diff-resp-card{border:1px solid var(--line);border-radius:4px;margin:8px 0;background:#fff}
.diff-resp-head{padding:10px 14px;display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap;border-bottom:1px solid var(--line-soft);background:var(--cell-bg)}
.diff-resp-meta{font-size:11.5px;color:var(--ink2);display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.diff-resp-body{padding:12px 14px}
.diff-resp-body details{margin:6px 0}
.diff-text-add{background:#d1f0d7;color:#155724;padding:0 2px;border-radius:2px}
.diff-text-del{background:#f8d7da;color:#721c24;padding:0 2px;border-radius:2px;text-decoration:line-through;text-decoration-color:rgba(114,28,36,.5)}
.diff-text-block{font-size:12px;line-height:1.65;background:var(--cell-bg);padding:10px 12px;border-radius:4px;border:1px solid var(--line-soft);white-space:pre-wrap;word-break:break-word;max-height:340px;overflow:auto}
table#tbl-diff-flow th,table#tbl-diff-flow td{vertical-align:middle}
table#tbl-diff-flow .col-metric{font-weight:600}
table#tbl-diff-flow .col-bucket{color:var(--ink2);font-size:11px}
table#tbl-diff-flips .col-prompt{max-width:380px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
table#tbl-diff-flips .col-prompt:hover{white-space:normal;overflow:visible}
table#tbl-diff-flips .col-prompt a{color:inherit;text-decoration:none}
table#tbl-diff-flips .col-prompt a:hover{color:var(--blue);text-decoration:underline}

/* ===== Citation DR pills / row highlight / filter tabs ===== */
.dr-pill{display:inline-block;padding:1px 8px;border-radius:10px;font-size:11px;font-weight:700;font-variant-numeric:tabular-nums;min-width:30px;text-align:center;line-height:1.6}
.dr-pill.dr-top{background:#ffe082;color:#7a4f00;box-shadow:inset 0 0 0 1px #f1b100}
.dr-pill.dr-high{background:#bbdefb;color:#0d47a1;box-shadow:inset 0 0 0 1px #64b5f6}
.dr-pill.dr-mid{background:#e3f2fd;color:#1565c0}
.dr-pill.dr-low{background:#f5f5f5;color:#757575}
.dr-pill.dr-zero{background:#fff;color:#bdbdbd;box-shadow:inset 0 0 0 1px #e0e0e0}
tr.dr-row-top td{background:#fffbe6 !important}
tr.dr-row-top td:first-child{border-left:3px solid #f1b100}
tr.dr-row-high td{background:#f5faff !important}
tr.dr-row-high td:first-child{border-left:3px solid #64b5f6}
.dr-tabs{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px}
.dr-tab{border:1px solid var(--line);background:#fff;padding:5px 12px;border-radius:14px;cursor:pointer;font:inherit;font-size:11.5px;color:var(--ink2);white-space:nowrap}
.dr-tab:hover{border-color:var(--blue);color:var(--blue);background:var(--blue-soft)}
.dr-tab.is-active{background:var(--blue);color:#fff;border-color:var(--blue);font-weight:600}

/* ===== AI Topics (⑤) ===== */
.topics-toolbar{display:flex;flex-direction:column;gap:10px;margin-bottom:14px}
.topics-filters{display:flex;flex-wrap:wrap;gap:14px}
.topics-filter-group{display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.topics-filter-group .flbl{font-size:11px;color:var(--ink3);font-weight:700;text-transform:uppercase;letter-spacing:.05em;padding-right:4px}
.topics-search-wrap{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.topics-list{display:flex;flex-direction:column;gap:12px}
.topic-card{background:#fff;border:1px solid var(--line);border-radius:6px;padding:14px 16px 12px;display:flex;flex-direction:column;gap:8px;transition:box-shadow .15s}
.topic-card:hover{box-shadow:0 1px 6px rgba(0,0,0,.05);border-color:var(--blue-mid)}
.topic-card .tc-meta{display:flex;align-items:center;flex-wrap:wrap;gap:8px;font-size:11.5px;color:var(--ink2)}
.topic-card .tc-date{color:var(--ink3);font-variant-numeric:tabular-nums}
.topic-card .tc-ai{display:inline-block;padding:2px 9px;border-radius:10px;font-size:11px;font-weight:700;background:var(--blue-soft);color:var(--blue);letter-spacing:.01em}
.topic-card .tc-tag{display:inline-block;padding:2px 8px;border-radius:10px;font-size:10.5px;font-weight:600;background:#f0f1f5;color:var(--ink2);border:1px solid var(--line-soft)}
.topic-card .tc-title{font-size:14.5px;font-weight:700;line-height:1.5;color:var(--ink)}
.topic-card .tc-title a{color:var(--ink)}
.topic-card .tc-title a:hover{color:var(--blue);text-decoration:underline}
.topic-card .tc-summary{font-size:13px;color:var(--ink2);line-height:1.7}
.topic-card .tc-source{font-size:11.5px}
.topic-card .tc-reactions{margin-top:6px;background:var(--cell-bg);border:1px solid var(--line-soft);border-radius:5px;padding:10px 12px;display:flex;flex-direction:column;gap:6px}
.topic-card .tc-reactions .tc-r-h{font-size:11px;font-weight:700;color:var(--ink3);letter-spacing:.05em;text-transform:uppercase;display:flex;align-items:center;gap:6px}
.topic-card .tc-reactions .tc-r-h::before{content:"";display:inline-block;width:4px;height:14px;background:var(--blue);border-radius:2px}
.topic-card .tc-reactions .tc-r-s{font-size:12.5px;color:var(--ink2);line-height:1.7}
.topic-card .tc-reactions .tc-r-l{display:flex;flex-wrap:wrap;gap:8px;font-size:11.5px}
.topic-card .tc-reactions .tc-r-l a{display:inline-flex;align-items:center;gap:4px;padding:2px 8px;border-radius:10px;background:#fff;border:1px solid var(--line);color:var(--blue);text-decoration:none}
.topic-card .tc-reactions .tc-r-l a:hover{background:var(--blue);color:#fff;border-color:var(--blue)}
/* AI brand tints */
.tc-ai.ai-OpenAI{background:#dff5ec;color:#0a8054}
.tc-ai.ai-Anthropic{background:#fde9da;color:#a05a1f}
.tc-ai.ai-Google{background:#dbe8fc;color:#1a56c0}
.tc-ai.ai-Microsoft{background:#cfe5fa;color:#005a9e}
.tc-ai.ai-Perplexity{background:#d8f5e8;color:#0d8060}
.tc-ai.ai-Meta{background:#dde5fc;color:#1c3aa9}
.tc-ai.ai-xAI{background:#e2e2e2;color:#212121}
.topics-empty-search{padding:18px;text-align:center;color:var(--ink2);background:var(--cell-bg);border:1px dashed var(--line);border-radius:4px;font-size:12px}

/* ===== Details (response viewer) ===== */
details{border:1px solid var(--line);border-radius:4px;padding:0;margin:6px 0;background:#fff}
details>summary{cursor:pointer;padding:9px 14px;font-weight:600;font-size:12px;color:var(--ink);list-style:none;display:flex;align-items:center;justify-content:space-between;gap:10px}
details>summary::-webkit-details-marker{display:none}
details>summary::after{content:'▶';color:var(--ink2);font-size:9px;transition:transform .15s}
details[open]>summary::after{transform:rotate(90deg)}
details[open]>summary{border-bottom:1px solid var(--line-soft);background:var(--cell-bg)}
.detail-body{padding:14px 18px;font-size:12.5px;color:var(--ink);max-height:520px;overflow:auto;line-height:1.75;background:#fff}
.detail-body h1,.detail-body h2,.detail-body h3,.detail-body h4{font-weight:700;margin:12px 0 5px;line-height:1.35}
.detail-body h1{font-size:15px;border-bottom:1px solid var(--line-soft);padding-bottom:4px}
.detail-body h2{font-size:14px;color:var(--blue)}
.detail-body h3{font-size:13px}
.detail-body h4{font-size:12.5px;color:var(--ink2)}
.detail-body ul,.detail-body ol{margin:4px 0 4px 22px;padding:0}
.detail-body li{margin:2px 0}
.detail-body hr{border:0;border-top:1px dashed var(--line);margin:10px 0}
.detail-body code{background:var(--cell-bg);padding:1px 5px;border-radius:3px;font-size:11.5px;border:1px solid var(--line-soft)}

/* ===== Prompt cards (③) — LLM brand colors only here ===== */
.prompt-card{padding:14px 16px}
.prompt-header{display:flex;align-items:flex-start;gap:12px;padding:0 0 10px;border-bottom:1px solid var(--line-soft);margin-bottom:10px}
.prompt-header .no-badge{display:inline-flex;width:34px;height:34px;align-items:center;justify-content:center;border-radius:4px;background:var(--blue);color:#fff;font-weight:700;flex-shrink:0;font-size:13px}
.prompt-header .prompt-text{font-weight:600;font-size:13.5px;color:var(--ink);line-height:1.5}
.prompt-header .meta{color:var(--ink2);font-size:11px;margin-top:3px}
.mention-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:6px;margin:6px 0 0}
.mention-cell{border:1px solid var(--line-soft);border-radius:4px;padding:7px 10px;background:var(--cell-bg);display:flex;justify-content:space-between;align-items:center;font-size:11px}
.mention-cell .brand-name{color:var(--ink2);font-weight:500}
.mark-reco{display:inline-block;width:18px;text-align:center;font-weight:700;font-size:13px}
.mark-reco.r2{color:var(--up)}
.mark-reco.r1{color:var(--warn)}
.mark-reco.r0{color:var(--ink3)}
.llm-tag{display:inline-block;padding:2px 8px;border-radius:3px;font-size:10.5px;font-weight:700;color:#fff;margin-right:6px;letter-spacing:.02em}
.llm-tag.chatgpt{background:var(--chatgpt)}
.llm-tag.gemini{background:var(--gemini)}
.llm-tag.copilot{background:var(--copilot)}
.llm-tag.perplexity{background:var(--perplex)}
.dl-footnote{font-size:11px;color:var(--ink2);margin-top:10px;padding-top:10px;border-top:1px dashed var(--line-soft)}
.dl-footnote div{margin-top:2px}
/* Brand mention highlights inside response detail-body */
.detail-body mark.hl-brand{background:#fff59d;color:#5d4e00;padding:1px 4px;border-radius:3px;font-weight:700;box-shadow:inset 0 -1px 0 #f9a825}
.detail-body mark.hl-competitor{background:#e1bee7;color:#4a148c;padding:1px 4px;border-radius:3px;font-weight:600}
.mention-badge{display:inline-block;margin-left:8px;padding:1px 8px;border-radius:10px;background:#fff59d;color:#7a5c00;font-size:10.5px;font-weight:700;letter-spacing:.02em}

/* ===== Matrix view ===== */
.matrix-wrap{max-height:none;border:1px solid var(--line);border-radius:4px;overflow:auto}
.matrix-wrap table{border-collapse:separate;border-spacing:0;font-size:11.5px;min-width:1100px}
.matrix-wrap th, .matrix-wrap td{padding:6px 8px;border:0;border-bottom:1px solid var(--line-soft);background:#fff}
.matrix-wrap thead th{position:sticky;top:0;background:var(--cell-bg);z-index:3;font-size:10.5px;color:var(--ink2);font-weight:600;border-bottom:1px solid var(--line)}
.matrix-wrap thead tr.h-group th{background:#eef0f6;color:var(--ink);font-weight:700;font-size:11px;text-align:center;letter-spacing:.02em;border-bottom:1px solid var(--line)}
.matrix-wrap thead tr.h-group th.idea-grp{background:var(--blue-soft);color:var(--blue)}
.matrix-wrap thead tr.h-group th.prz-grp{background:#fdebec;color:#b3261e}
.matrix-wrap th.col-no, .matrix-wrap td.col-no{position:sticky;left:0;z-index:2;background:#fff;text-align:right;width:36px;font-variant-numeric:tabular-nums;border-right:1px solid var(--line-soft)}
.matrix-wrap thead th.col-no{z-index:4;background:var(--cell-bg)}
.matrix-wrap th.col-cat, .matrix-wrap td.col-cat{position:sticky;left:36px;z-index:2;background:#fff;width:110px;font-size:10.5px;color:var(--ink2);border-right:1px solid var(--line-soft)}
.matrix-wrap thead th.col-cat{z-index:4;background:var(--cell-bg)}
.matrix-wrap th.col-prompt, .matrix-wrap td.col-prompt{position:sticky;left:146px;z-index:2;background:#fff;min-width:280px;max-width:340px;font-size:12px;color:var(--ink);border-right:2px solid var(--line)}
.matrix-wrap thead th.col-prompt{z-index:4;background:var(--cell-bg)}
.matrix-wrap td.col-prompt{cursor:default}
.matrix-wrap td.col-prompt .p-text{display:block;line-height:1.45;max-height:3em;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}
.matrix-wrap td.col-prompt:hover .p-text{max-height:none;-webkit-line-clamp:unset}
.matrix-wrap td.col-cat .p-text{display:block;line-height:1.35;max-height:2.7em;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}
.matrix-wrap td.col-cat:hover .p-text{max-height:none;-webkit-line-clamp:unset}
/* Unified row height + middle alignment for matrix rows */
.matrix-wrap tbody td{height:54px;vertical-align:middle}
.matrix-wrap td.col-no{vertical-align:middle}
.matrix-wrap td.col-cat,.matrix-wrap td.col-prompt{vertical-align:middle}
/* Category block divider (top border on first row of each new category) */
.matrix-wrap tbody tr.cat-block-start td{border-top:2px solid #b9c0d4}
.matrix-wrap tbody tr.cat-block-start td.col-no,
.matrix-wrap tbody tr.cat-block-start td.col-cat,
.matrix-wrap tbody tr.cat-block-start td.col-prompt{border-top:2px solid #b9c0d4}
/* Prompt link → response card */
.matrix-wrap a.prompt-link{color:inherit;text-decoration:none;display:block}
.matrix-wrap a.prompt-link:hover{color:var(--blue);text-decoration:underline}
.matrix-wrap a.prompt-link::after{content:' ▶';font-size:9px;color:var(--blue);opacity:.55;margin-left:4px;vertical-align:middle}
.matrix-wrap td.cell-mark{text-align:center;font-size:14px;line-height:1;width:64px;font-weight:700}
.matrix-wrap td.cell-mark.r2{color:var(--up);background:#f3faf6}
.matrix-wrap td.cell-mark.r1{color:var(--warn);background:#fff8ef}
.matrix-wrap td.cell-mark.r0{color:var(--ink3);background:#fff}
.matrix-wrap td.col-divider, .matrix-wrap th.col-divider{border-left:2px solid var(--line)}
.matrix-wrap tbody tr:hover td{background:#f6f7fb}
.matrix-wrap tbody tr:hover td.col-no, .matrix-wrap tbody tr:hover td.col-cat, .matrix-wrap tbody tr:hover td.col-prompt{background:#f6f7fb}
.matrix-wrap tfoot td{position:sticky;bottom:0;background:var(--cell-bg);font-weight:700;border-top:2px solid var(--line);font-size:11px;color:var(--ink);z-index:2}
.matrix-wrap tfoot td.col-prompt{background:var(--cell-bg);border-right:2px solid var(--line)}
.matrix-wrap tfoot td.cell-mark{font-size:11.5px;color:var(--ink);background:var(--cell-bg)}
.matrix-legend{display:flex;gap:14px;font-size:11px;color:var(--ink2);margin:0 0 10px;flex-wrap:wrap}
.matrix-legend .li{display:inline-flex;align-items:center;gap:5px}
.legend-mark{display:inline-block;width:18px;text-align:center;font-weight:700}
.legend-mark.r2{color:var(--up)}
.legend-mark.r1{color:var(--warn)}
.legend-mark.r0{color:var(--ink3)}

/* ===== Hamburger menu (mobile) ===== */
.hamburger{display:none;position:fixed;top:12px;left:12px;z-index:200;width:40px;height:40px;border-radius:6px;background:#fff;border:1px solid var(--line);box-shadow:0 2px 8px rgba(0,0,0,.12);cursor:pointer;align-items:center;justify-content:center;padding:0}
.hamburger span{display:block;width:18px;height:2px;background:var(--ink);position:relative;border-radius:2px}
.hamburger span::before,.hamburger span::after{content:'';position:absolute;left:0;width:18px;height:2px;background:var(--ink);border-radius:2px}
.hamburger span::before{top:-6px}
.hamburger span::after{top:6px}
.scrim{display:none;position:fixed;inset:0;background:rgba(0,0,0,.4);z-index:150}
.scrim.show{display:block}

/* ===== Responsive (tablet) ===== */
@media (max-width: 1024px){
  .section{padding:18px 20px 60px}
  .page-header{padding:18px 20px 14px}
  .sidebar{width:220px}
  .matrix-wrap table{min-width:920px}
}

/* ===== Responsive (mobile, ≤768px) ===== */
@media (max-width: 768px){
  html,body{font-size:13px}
  .app{display:block}
  .hamburger{display:flex}
  .sidebar{position:fixed;top:0;left:0;height:100vh;width:260px;max-width:80vw;transform:translateX(-100%);transition:transform .2s ease;z-index:160;box-shadow:0 0 16px rgba(0,0,0,.08)}
  .sidebar.open{transform:translateX(0)}
  main{padding-top:0}
  .page-header{padding:14px 16px 12px 60px}
  .page-header h1{font-size:17px;line-height:1.35}
  .page-header .as-of{display:inline-block;margin-left:8px;font-size:10.5px}
  .page-header .sub{font-size:11.5px;line-height:1.4}
  .section{padding:14px 14px 60px;max-width:100%}

  .sec-hero{padding:14px 14px;margin-bottom:12px}
  .sec-hero h2{font-size:16px;line-height:1.4}
  .sec-hero h2 .sub-h{font-size:12.5px}
  .sec-hero .lead{font-size:11.5px;padding-left:8px}

  .card{padding:14px 14px;margin-bottom:10px}
  .card h3{font-size:13px}
  .card .h3-sub{font-size:11px;margin-bottom:10px}

  .kpis{grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:8px}
  .kpi{padding:10px 12px}
  .kpi .label{font-size:10.5px}
  .kpi .value{font-size:20px}

  .row2col,.row3col{grid-template-columns:1fr;gap:10px}

  .chart-wrap{height:240px}
  .chart-wrap.lg{height:280px}
  .chart-wrap.sm{height:200px}

  /* Tables: keep horizontal scroll, but reduce padding */
  table{font-size:11.5px}
  th,td{padding:6px 8px}
  /* Make sticky table headers normal on mobile (avoid overlap with hamburger) */
  .table-wrap th{position:static}

  /* Matrix view — keep horizontal scroll, slim column widths */
  .matrix-wrap table{min-width:780px;font-size:11px}
  .matrix-wrap th.col-no, .matrix-wrap td.col-no{width:30px}
  .matrix-wrap th.col-cat, .matrix-wrap td.col-cat{width:80px;font-size:10px}
  .matrix-wrap th.col-prompt, .matrix-wrap td.col-prompt{left:110px;min-width:200px;max-width:240px;font-size:11.5px}
  .matrix-wrap td.cell-mark{width:46px;font-size:13px}

  /* Toolbar / search */
  input[type="text"].search,select.search{width:100%}
  .toolbar{gap:6px}

  /* Diag rubric tables — keep readable */
  #tbl-rubric th, #tbl-rubric td{padding:6px 8px;font-size:11px}

  /* Detail body */
  .detail-body{padding:12px 14px;font-size:12px}
  .detail-body h1{font-size:14px}
  .detail-body h2{font-size:13px}
  .detail-body h3{font-size:12.5px}

  /* Prompt cards */
  .prompt-card{padding:12px 12px}
  .prompt-header{gap:8px}
  .prompt-header .no-badge{width:28px;height:28px;font-size:12px}
  .prompt-header .prompt-text{font-size:12.5px}
  .mention-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:5px}
  .mention-cell{font-size:10.5px;padding:5px 8px}

  /* Pager */
  .pager{font-size:11.5px;gap:6px}
  .pager button{padding:4px 10px;font-size:11.5px}
}

/* ===== Small phones (≤380px) ===== */
@media (max-width: 380px){
  .page-header h1{font-size:15.5px}
  .sec-hero h2{font-size:15px}
  .kpi .value{font-size:18px}
  .matrix-wrap td.col-prompt{left:96px;min-width:180px;max-width:200px}
  .matrix-wrap th.col-cat, .matrix-wrap td.col-cat{width:60px}
}
</style>
</head>
<body>
<button class="hamburger" id="hamburger" aria-label="メニューを開く"><span></span></button>
<div class="scrim" id="scrim"></div>
<div class="app">
  <aside class="sidebar" id="sidebar">
    <div class="brand">
      <div class="b-title">IDEATECH LLMO</div>
      <span class="b-sub">Monthly Monitor Dashboard</span>
    </div>

    <div class="nav-group">
      <div class="nav-group-title">★ 週次サマリ</div>
      <button class="nav-btn nav-btn-diff" data-section="diff"><span class="nav-num">★</span>前週比 差分</button>
    </div>
    <div class="nav-group">
      <div class="nav-group-title">① 基礎診断</div>
      <button class="nav-btn" data-section="rubric"><span class="nav-num">1</span>評点定義</button>
      <button class="nav-btn" data-section="diag"><span class="nav-num">1</span>IDEATECH公式サイト</button>
    </div>
    <div class="nav-group">
      <div class="nav-group-title">② 結果指標 (SS・CV)</div>
      <button class="nav-btn" data-section="flow-ss"><span class="nav-num">2</span>流入指標 (SS)</button>
      <button class="nav-btn" data-section="flow-cv"><span class="nav-num">2</span>コンバージョン (CV)</button>
    </div>
    <div class="nav-group">
      <div class="nav-group-title">③ 結果指標 (推奨状況)</div>
      <button class="nav-btn" data-section="prompts-matrix"><span class="nav-num">3</span>推奨状況 一覧表</button>
      <button class="nav-btn" data-section="prompts"><span class="nav-num">3</span>調査PR関連プロンプト</button>
    </div>
    <div class="nav-group">
      <div class="nav-group-title">④ 中間指標 (サイテーション)</div>
      <button class="nav-btn" data-section="cit-ideatech"><span class="nav-num">4</span>IDEATECH</button>
      <button class="nav-btn" data-section="cit-risapy"><span class="nav-num">4</span>リサピー</button>
    </div>
    <div class="nav-group">
      <div class="nav-group-title">⑤ AI Topics</div>
      <button class="nav-btn" data-section="topics"><span class="nav-num">5</span>主要AIニュース</button>
    </div>
  </aside>

  <main>
    <div class="page-header">
      <h1>IDEATECH LLMO ダッシュボード<span class="as-of" id="asof-tag"></span></h1>
    </div>

    <!-- ★ 前週比 差分タブ -->
    <section id="sec-diff" class="section">
      <div class="sec-hero diff-hero">
        <div class="crumb">★ 週次サマリ｜<b>前週比 差分</b><span id="diff-asof"></span></div>
        <h2>今週の変化サマリ<span class="sub-h" id="diff-headline">— データ取得中</span></h2>
        <p class="lead" id="diff-lead"></p>
      </div>
      <div class="tab-summary" id="diff-summary"></div>
      <div class="kpis" id="diff-kpis"></div>

      <div class="card">
        <h3>① 流入 / CV の前週比</h3>
        <div class="h3-sub">直近月の数値・年累計（YTD）・全期間累計の3階層で前週スナップショットと比較</div>
        <div class="table-wrap"><table id="tbl-diff-flow"></table></div>
      </div>

      <div class="card">
        <h3>② 推奨ステータスの変化（▲↔⚫︎）</h3>
        <div class="h3-sub">プロンプト × LLM 単位で、前週から言及ステータスが変わった行を抽出</div>
        <div class="diff-toolbar" id="diff-flips-toolbar"></div>
        <div class="table-wrap"><table id="tbl-diff-flips"></table></div>
        <div id="diff-flips-empty" class="empty-note" style="display:none">前週から推奨ステータスの変化はありませんでした。</div>
      </div>

      <div class="card">
        <h3>③ 応答内容の差分</h3>
        <div class="h3-sub">同一プロンプト × 同一LLM で応答テキストが変わったケースを文字数差・追加箇所・削除箇所で表示</div>
        <div class="diff-toolbar" id="diff-resp-toolbar"></div>
        <div id="diff-resp-list"></div>
        <div id="diff-resp-empty" class="empty-note" style="display:none">前週から応答内容の差分はありませんでした。</div>
      </div>

      <div class="card">
        <h3>④ 新規サイテーション一覧</h3>
        <div class="h3-sub">前週スナップショットに含まれていなかった ahrefs 言及のみ。DR順で並べ、高DRはハイライト</div>
        <div class="diff-tabs">
          <button class="diff-cit-tab is-active" data-target="ideatech">IDEATECH <span class="cnt" id="diff-cit-cnt-ideatech">0</span></button>
          <button class="diff-cit-tab" data-target="risapy">リサピー <span class="cnt" id="diff-cit-cnt-risapy">0</span></button>
        </div>
        <div class="table-wrap"><table id="tbl-diff-cit"></table></div>
        <div id="diff-cit-empty" class="empty-note" style="display:none">新規サイテーションはありませんでした。</div>
      </div>
    </section>

    <!-- ① 基礎診断 -->
    <section id="sec-diag" class="section">
      <div class="sec-hero">
        <div class="crumb">① 基礎診断｜シート：<b>IDEATECH公式サイト</b></div>
        <h2 id="diag-title">基礎診断スコア</h2>
        <p class="lead" id="diag-lead"></p>
      </div>
      <div class="tab-summary" id="diag-summary"></div>
      <div class="kpis" id="diag-kpis"></div>
      <div class="card">
        <h3>カテゴリ別 平均スコア</h3>
        <div class="h3-sub">A〜D の 4 カテゴリ平均（5点満点）。レーダーが外側に大きいほど高評価</div>
        <div class="row2col">
          <div class="chart-wrap sm"><canvas id="chart-diag-radar"></canvas></div>
          <div id="diag-cat-desc"></div>
        </div>
      </div>
      <div class="card">
        <h3>20項目 詳細</h3>
        <div class="h3-sub">各項目の評価点と理由。低スコア（1〜2点）が改善優先</div>
        <div class="table-wrap"><table id="tbl-diag"></table></div>
      </div>
    </section>

    <!-- ① 基礎診断｜評点定義 -->
    <section id="sec-rubric" class="section">
      <div class="sec-hero">
        <div class="crumb">① 基礎診断｜<b>評点定義</b></div>
        <h2>20項目の評点定義<span class="sub-h">— 5点 / 3点 / 1点 と確認方法の一覧</span></h2>
        <p class="lead">各診断項目を共通基準で採点するための評価軸と確認方法。スコアの根拠を辿る／次回診断時の参照に使用してください。</p>
      </div>
      <div class="card">
        <h3>カテゴリ説明</h3>
        <div class="h3-sub">A〜Dの4カテゴリ — それぞれが LLMO の異なる側面を担う</div>
        <div class="table-wrap"><table id="tbl-rubric-groups"></table></div>
      </div>
      <div class="card">
        <h3>20項目 評点定義</h3>
        <div class="h3-sub">No.1〜20 を群（A/B/C/D）でグループ化。各行に確認方法と 5/3/1 点の定義を併記</div>
        <div class="table-wrap"><table id="tbl-rubric"></table></div>
      </div>
    </section>

    <!-- ②-A 流入指標 (SS) -->
    <section id="sec-flow-ss" class="section">
      <div class="sec-hero">
        <div class="crumb">② 結果指標 (SS・CV)｜シート：<b>2025年1月以降</b>｜<b>流入指標 (SS)</b></div>
        <h2 id="flow-ss-title">流入指標</h2>
        <p class="lead" id="flow-ss-lead"></p>
      </div>
      <div class="tab-summary" id="flow-ss-summary"></div>
      <div id="flow-ss-forecast-banner"></div>
      <div class="kpis" id="flow-ss-kpis"></div>
      <div class="card">
        <h3>サイト全体流入数の月次推移</h3>
        <div class="h3-sub" id="flow-ss-chart-note"></div>
        <div class="chart-wrap"><canvas id="chart-site-total"></canvas></div>
        <div class="chart-legend">
          <span class="li"><span class="legend-dot"></span>サイト全体流入数（強調）</span>
          <span class="li"><span class="legend-dot muted"></span>オーガニック流入・AI経由流入（参考）</span>
          <span class="li"><span class="legend-dot dashed"></span>期間平均（基準線）</span>
          <span class="li"><span class="legend-dot" style="background:var(--cat-3)"></span>AI経由比率（右軸）</span>
        </div>
      </div>
      <div class="card">
        <h3>AI経由流入数の月次推移</h3>
        <div class="h3-sub" id="flow-ss-ai-chart-note">AI経由流入のみを抽出した月次推移ライン（積み上げ棒とは別軸で詳細を確認）</div>
        <div class="chart-wrap"><canvas id="chart-ai-total"></canvas></div>
        <div class="chart-legend">
          <span class="li"><span class="legend-dot" style="background:var(--cat-2)"></span>AI経由流入数（実績）</span>
          <span class="li"><span class="legend-dot dashed"></span>期間平均（基準線）</span>
          <span class="li" id="flow-ss-ai-fc-legend" style="display:none"><span class="legend-dot" style="background:#7986cb;opacity:.5"></span>当月着地予測</span>
        </div>
      </div>
      <div class="card">
        <h3>AI経由流入：LLMカテゴリ別 (スタック)</h3>
        <div class="h3-sub">大手汎用LLM／AI検索特化／その他カテゴリの月次合計を積み上げ</div>
        <div class="chart-wrap"><canvas id="chart-flow-groups"></canvas></div>
      </div>
      <div class="card">
        <h3>SS サマリ系列テーブル</h3>
        <div class="h3-sub">サイト全体／オーガニック／AI経由 の月次推移と合計</div>
        <div class="table-wrap"><table id="tbl-series-ss"></table></div>
      </div>
      <div class="card">
        <h3>AI経由流入：カテゴリ × LLM 詳細内訳</h3>
        <div class="table-wrap"><table id="tbl-flow-groups"></table></div>
      </div>
    </section>

    <!-- ②-B コンバージョン (CV) -->
    <section id="sec-flow-cv" class="section">
      <div class="sec-hero">
        <div class="crumb">② 結果指標 (SS・CV)｜シート：<b>2025年1月以降</b>｜<b>コンバージョン (CV)</b></div>
        <h2 id="flow-cv-title">コンバージョン (CV)</h2>
        <p class="lead" id="flow-cv-lead"></p>
      </div>
      <div class="tab-summary" id="flow-cv-summary"></div>
      <div id="flow-cv-forecast-banner"></div>
      <div class="kpis" id="flow-cv-kpis"></div>
      <div class="card">
        <h3>サイト全体CVの月次推移</h3>
        <div class="h3-sub" id="flow-cv-site-chart-note"></div>
        <div class="chart-wrap"><canvas id="chart-cv-site"></canvas></div>
        <div class="chart-legend">
          <span class="li"><span class="legend-dot"></span>サイト全体CV件数（強調）</span>
          <span class="li" style="opacity:.6"><span class="legend-dot" style="background:#9e9e9e"></span>オーガニックCV（参考）</span>
          <span class="li" style="opacity:.6"><span class="legend-dot" style="background:#cfcfcf"></span>AI経由CV（参考）</span>
          <span class="li"><span class="legend-dot dashed"></span>期間平均（基準線）</span>
          <span class="li" id="flow-cv-site-fc-legend" style="display:none"><span class="legend-dot" style="background:#7986cb;opacity:.5"></span>当月着地予測</span>
        </div>
        <div class="h3-sub" style="margin-top:6px;font-size:11px;color:#888">データ元：HubSpot（当月新規リード作成数）</div>
      </div>
      <div class="card">
        <h3>AI経由 CV の月次推移</h3>
        <div class="h3-sub" id="flow-cv-chart-note"></div>
        <div class="chart-wrap"><canvas id="chart-cv-line"></canvas></div>
        <div class="chart-legend">
          <span class="li"><span class="legend-dot"></span>AI経由CV件数（強調）</span>
          <span class="li"><span class="legend-dot dashed"></span>期間平均（基準線）</span>
        </div>
      </div>
      <div class="card">
        <h3>AI経由CV：LLMカテゴリ別 (スタック)</h3>
        <div class="h3-sub">どのLLMカテゴリ経由でCVが発生したかを月次で積み上げ表示</div>
        <div class="chart-wrap sm"><canvas id="chart-cv-groups"></canvas></div>
      </div>
      <div class="card">
        <h3>CV サマリ系列テーブル</h3>
        <div class="h3-sub">AI経由CV月次値・累計</div>
        <div class="table-wrap"><table id="tbl-series-cv"></table></div>
      </div>
      <div class="card">
        <h3>AI経由CV：カテゴリ × LLM 詳細内訳</h3>
        <div class="table-wrap"><table id="tbl-cv-groups"></table></div>
      </div>
    </section>

    <!-- ③ 推奨状況 一覧表 (matrix) -->
    <section id="sec-prompts-matrix" class="section">
      <div class="sec-hero">
        <div class="crumb">③ 結果指標 (推奨状況)｜シート：<b>調査PR関連プロンプト</b><span id="matrix-survey-date"></span></div>
        <h2 id="matrix-title">推奨状況 一覧</h2>
        <p class="lead" id="matrix-lead"></p>
      </div>
      <div class="tab-summary" id="matrix-summary"></div>
      <div class="kpis" id="matrix-kpis"></div>
      <div class="card">
        <h3>40プロンプト × 4LLM ⚫︎/▲ マトリクス</h3>
        <div class="h3-sub">⚫︎ = 言及あり／▲ = 言及なし。IDEATECH／リサピー と 競合 PRIZMA を左右に並べて比較</div>
        <div class="toolbar">
          <input type="text" class="search" id="matrix-search" placeholder="プロンプト／分類で検索">
          <select id="matrix-cat" class="search" style="width:auto"></select>
          <span class="small" id="matrix-count"></span>
          <a href="#prompts" class="small" style="margin-left:auto">▶ 応答全文を見る</a>
        </div>
        <div class="matrix-legend">
          <span class="li"><span class="legend-mark r2">⚫︎</span>言及あり（LLM の応答内に言及が含まれる）</span>
          <span class="li"><span class="legend-mark r1">▲</span>言及なし（LLM の応答内に言及が含まれない）</span>
          <span class="li" style="margin-left:auto">※ 左 36+110+280px は固定列。横スクロールで全LLM × 2社が確認できます</span>
        </div>
        <div class="table-wrap matrix-wrap"><table id="tbl-matrix"></table></div>
      </div>
    </section>

    <!-- ③ 調査PR関連プロンプト -->
    <section id="sec-prompts" class="section">
      <div class="sec-hero">
        <div class="crumb">③ 結果指標 (推奨状況)｜シート：<b>調査PR関連プロンプト</b><span id="prompts-survey-date"></span></div>
        <h2 id="prompts-title">プロンプト推奨状況</h2>
        <p class="lead" id="prompts-lead"></p>
      </div>
      <div class="tab-summary" id="prompts-summary"></div>
      <div class="kpis" id="prompts-kpis"></div>
      <div class="card">
        <h3>40プロンプト × 4LLM 応答全文</h3>
        <div class="h3-sub">⚫︎ = 言及あり／▲ = 言及なし。プロンプトを開くと各LLMの応答全文が確認できます</div>
        <div class="toolbar">
          <input type="text" class="search" id="prompts-search" placeholder="プロンプト／分類で検索">
          <select id="prompts-cat" class="search" style="width:auto"></select>
          <span class="small" id="prompts-count"></span>
        </div>
        <div id="prompts-list"></div>
        <div class="dl-footnote" id="prompts-notes"></div>
      </div>
    </section>

    <!-- ④ サイテーション IDEATECH -->
    <section id="sec-cit-ideatech" class="section">
      <div class="sec-hero">
        <div class="crumb">④ 中間指標 (サイテーション)｜シート：<b>IDEATECH</b></div>
        <h2 id="cit-ideatech-title">サイテーション総数</h2>
        <p class="lead" id="cit-ideatech-lead"></p>
      </div>
      <div class="tab-summary" id="cit-ideatech-summary"></div>
      <div class="kpis" id="cit-ideatech-kpis"></div>
      <div class="card">
        <h3>サイテーション一覧</h3>
        <div class="h3-sub">DR（ahrefs Domain Rating）でフィルタ／タイトル／URL／公開日 を 100件ずつページ送り</div>
        <div id="cit-ideatech-filter" class="dr-tabs"></div>
        <div class="toolbar">
          <input type="text" class="search" id="cit-ideatech-search" placeholder="タイトル／URLで検索">
          <span class="small" id="cit-ideatech-count"></span>
        </div>
        <div class="table-wrap" style="max-height:560px"><table id="tbl-cit-ideatech"></table></div>
        <div class="pager" id="pager-cit-ideatech"></div>
      </div>
    </section>

    <!-- ④ サイテーション リサピー -->
    <section id="sec-cit-risapy" class="section">
      <div class="sec-hero">
        <div class="crumb">④ 中間指標 (サイテーション)｜シート：<b>リサピー</b></div>
        <h2 id="cit-risapy-title">サイテーション総数</h2>
        <p class="lead" id="cit-risapy-lead"></p>
      </div>
      <div class="tab-summary" id="cit-risapy-summary"></div>
      <div class="kpis" id="cit-risapy-kpis"></div>
      <div class="card">
        <h3>サイテーション一覧</h3>
        <div class="h3-sub">DR（ahrefs Domain Rating）でフィルタ／タイトル／URL／公開日 を 100件ずつページ送り</div>
        <div id="cit-risapy-filter" class="dr-tabs"></div>
        <div class="toolbar">
          <input type="text" class="search" id="cit-risapy-search" placeholder="タイトル／URLで検索">
          <span class="small" id="cit-risapy-count"></span>
        </div>
        <div class="table-wrap" style="max-height:560px"><table id="tbl-cit-risapy"></table></div>
        <div class="pager" id="pager-cit-risapy"></div>
      </div>
    </section>

    <!-- ⑤ AI Topics -->
    <section id="sec-topics" class="section">
      <div class="sec-hero">
        <div class="crumb">⑤ AI Topics｜<b>主要AIニュース（自動収集）</b></div>
        <h2>主要AIプロダクトの週次アップデート<span class="sub-h" id="topics-asof"></span></h2>
        <p class="lead">過去7〜10日間の主要AI（OpenAI / Anthropic / Google / Microsoft / Perplexity / 国内AI 等）のプロダクト発表・新機能・業界動向を自動収集し、世間の反応を要約しています。</p>
      </div>
      <div class="tab-summary" id="topics-summary"></div>
      <div class="card">
        <div class="topics-toolbar">
          <div class="topics-filters">
            <div class="topics-filter-group" id="topics-filter-year"></div>
            <div class="topics-filter-group" id="topics-filter-ai"></div>
            <div class="topics-filter-group" id="topics-filter-tag"></div>
          </div>
          <div class="topics-search-wrap">
            <input type="text" class="search" id="topics-search" placeholder="タイトル／サマリ／反応で検索">
            <span class="small" id="topics-count"></span>
          </div>
        </div>
        <div id="topics-list" class="topics-list"></div>
        <div id="topics-empty" class="empty-note" style="display:none">表示できるニュースがありません。週次パイプライン実行後に反映されます。</div>
      </div>
    </section>
  </main>
</div>

<script>
const DATA = __DATA_PLACEHOLDER__;

const $ = (s,root=document)=>(typeof root==='string'?document.querySelector(root):root).querySelector(s);
const $$ = (s,root=document)=>[...(typeof root==='string'?document.querySelector(root):root).querySelectorAll(s)];
const sum = a => a.reduce((x,y)=>x+(Number(y)||0),0);
const avg = a => a.length? sum(a)/a.length : 0;
const fmt = n => (n==null || isNaN(n)) ? '' : (Number.isInteger(n) ? n.toLocaleString('ja-JP') : Number(n).toLocaleString('ja-JP',{maximumFractionDigits:2}));
const pct = n => (n==null || isNaN(n)) ? '' : (n*100).toFixed(2)+'%';
const esc = s => (s==null?'':String(s)).replace(/[&<>"']/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

Chart.defaults.font.family = '-apple-system,"Hiragino Kaku Gothic ProN","Yu Gothic UI",Meiryo,sans-serif';
Chart.defaults.font.size = 11;
Chart.defaults.color = '#595959';
Chart.defaults.borderColor = '#ededed';

/* Year divider plugin — draws a vertical dashed line + year label at year boundaries.
   Detects boundary by year prefix change in label (e.g. "24/12" → "25/1"). */
const yearDividerPlugin = {
  id: 'yearDivider',
  afterDraw(chart){
    const {ctx, chartArea, scales, data} = chart;
    const xScale = scales.x;
    if(!xScale || !chartArea) return;
    const labels = data.labels;
    if(!labels || labels.length < 2) return;
    const getYr = l => {
      const s = String(l);
      // Format is "YY/M" (e.g. "24/12") — first 2 chars = 2-digit year
      const m = s.match(/^(\d{2,4})/);
      return m ? m[1] : s;
    };
    ctx.save();
    for(let i=1; i<labels.length; i++){
      if(getYr(labels[i]) !== getYr(labels[i-1])){
        const xCur = xScale.getPixelForValue(i);
        const xPrev = xScale.getPixelForValue(i-1);
        const x = (xCur + xPrev) / 2;
        ctx.strokeStyle = 'rgba(120,120,120,0.45)';
        ctx.lineWidth = 1;
        ctx.setLineDash([4,3]);
        ctx.beginPath();
        ctx.moveTo(x, chartArea.top);
        ctx.lineTo(x, chartArea.bottom);
        ctx.stroke();
        // Year label at top-left of new year region
        ctx.setLineDash([]);
        ctx.fillStyle = 'rgba(80,80,80,0.78)';
        ctx.font = 'bold 10px -apple-system,"Hiragino Kaku Gothic ProN",sans-serif';
        ctx.textAlign = 'left';
        ctx.textBaseline = 'top';
        const yr = getYr(labels[i]);
        const yrLabel = (yr.length===2 ? '20'+yr : yr) + '年';
        ctx.fillText(yrLabel, x + 3, chartArea.top + 2);
      }
    }
    ctx.restore();
  }
};
Chart.register(yearDividerPlugin);

const COLORS = {
  primary: '#0017c1',
  primarySoft: 'rgba(0,23,193,.08)',
  muted: '#bdbdbd',
  mutedLight: '#dcdcdc',
  ref: '#666',
  cat: ['#0017c1','#3949ab','#7986cb','#a3b1d4'],
};

/* ===== KPI / Delta helpers ===== */
function deltaHTML(curr, prev, opts={}){
  if(curr==null || prev==null || prev===0) return '<div class="delta delta-flat">前期比較なし</div>';
  const diff = curr - prev;
  const ratio = diff/Math.abs(prev);
  const dir = Math.abs(ratio) < 0.005 ? 'flat' : (diff>0 ? 'up' : 'down');
  const sign = diff>0 ? '+' : '';
  const fmtD = opts.isPct
    ? `${sign}${(diff*100).toFixed(2)}pt`
    : `${sign}${fmt(diff)}`;
  const fmtR = `${sign}${(ratio*100).toFixed(1)}%`;
  const label = opts.isPct
    ? `前月比 ${fmtD}（${dir==='flat'?'横ばい':'前月差'}）`
    : `前月比 ${fmtR}（${fmtD}）`;
  return `<div class="delta delta-${dir}"><span class="delta-arrow"></span>${esc(label)}</div>`;
}

function kpiBox(label, value, unit, deltaH, primary){
  const cls = primary ? 'kpi primary' : 'kpi';
  const u = unit ? `<span class="unit">${esc(unit)}</span>` : '';
  return `<div class="${cls}">
    <div class="label">${esc(label)}</div>
    <div class="value">${esc(value)}${u}</div>
    ${deltaH||''}
  </div>`;
}

/* ===== Hamburger / mobile drawer ===== */
const sidebarEl = $('#sidebar');
const scrimEl = $('#scrim');
const hamEl = $('#hamburger');
function openSidebar(){ sidebarEl.classList.add('open'); scrimEl.classList.add('show'); }
function closeSidebar(){ sidebarEl.classList.remove('open'); scrimEl.classList.remove('show'); }
if(hamEl) hamEl.addEventListener('click', openSidebar);
if(scrimEl) scrimEl.addEventListener('click', closeSidebar);

/* ===== Navigation ===== */
const navBtns = $$('.nav-btn');
function showSection(id){
  $$('.section').forEach(s=>s.classList.remove('active'));
  const t = $(`#sec-${id}`);
  if(t) t.classList.add('active');
  navBtns.forEach(b=>b.classList.toggle('active', b.dataset.section===id));
  if(location.hash!=='#'+id) history.replaceState(null,'','#'+id);
  closeSidebar();
  window.scrollTo({top:0,behavior:'instant'});
}
navBtns.forEach(b=>b.addEventListener('click',()=>showSection(b.dataset.section)));
const initial = (location.hash||'#diag').slice(1);
showSection(navBtns.some(b=>b.dataset.section===initial)?initial:'diag');

/* As-of badge */
(function(){
  const months = (DATA.flow && DATA.flow.months)||[];
  const series = DATA.flow && DATA.flow.series && DATA.flow.series.site_total || [];
  let lastIdx = -1;
  for(let i=months.length-1;i>=0;i--){
    if(months[i] && series[i]!=null){ lastIdx=i; break; }
  }
  if(lastIdx>=0){
    const m = months[lastIdx];
    const t = $('#asof-tag');
    if(t) t.textContent = ' as of '+m.replace('-','/');
  }
})();

/* Initial section: default to diag, but route old #flow hash to flow-ss */
(function(){
  const h = (location.hash||'').slice(1);
  if(h === 'flow'){
    showSection('flow-ss');
  }
})();

/* =========================================================== */
/* ① 基礎診断                                                  */
/* =========================================================== */
function renderDiag(){
  const D = DATA.diag;
  const cats = {};
  D.forEach(r=>{
    const g = r.group || (cats._last ? cats._last : 'A');
    cats._last = g;
    if(!cats[g]) cats[g] = {label:r.category, desc:r.category_desc, items:[]};
    if(r.category) cats[g].label = r.category;
    if(r.category_desc) cats[g].desc = r.category_desc;
    cats[g].items.push(r);
  });
  delete cats._last;

  const catLetters = Object.keys(cats);
  const catLabels = catLetters.map(l => (cats[l].label||'').replace(/\n/g,' / '));
  const catScore = catLetters.map(l => sum(cats[l].items.map(x=>x.score)));
  const catFull = catLetters.map(l => cats[l].items.length * 5);
  const catAvg = catLetters.map(l => avg(cats[l].items.map(x=>x.score)));
  const totalScore = sum(D.map(x=>x.score));
  const fullScore = D.length * 5;

  /* Hero — answer-first */
  let lowestIdx = 0;
  let lowestRatio = 1;
  catLetters.forEach((l,i)=>{
    if(catFull[i] && (catScore[i]/catFull[i]) < lowestRatio){ lowestRatio = catScore[i]/catFull[i]; lowestIdx = i; }
  });
  const lowL = catLetters[lowestIdx];
  const lowLabel = catLabels[lowestIdx];
  const lowVerdict = totalScore/fullScore >= 0.85 ? '高水準（85%以上）' : (totalScore/fullScore >= 0.7 ? '良好（70%以上）' : '改善余地あり');
  $('#diag-title').innerHTML = `基礎診断スコアは <span class="answer">${totalScore} / ${fullScore}点</span>（${(totalScore/fullScore*100).toFixed(0)}%・${lowVerdict}）<span class="sub-h">— ${esc(lowL)}群「${esc(lowLabel)}」が改善余地（${catScore[lowestIdx]}/${catFull[lowestIdx]}点）</span>`;
  $('#diag-lead').textContent = `20項目のうち低スコア項目（1〜2点）は${D.filter(r=>r.score!=null && r.score<=2).length}件。次アクションは${esc(lowL)}群の見直しから着手するのが効率的。`;

  /* KPI cards */
  $('#diag-kpis').innerHTML = [
    kpiBox('総合スコア', `${totalScore} / ${fullScore}`, '点', `<div class="delta delta-flat">満点比 ${(totalScore/fullScore*100).toFixed(1)}%</div>`, true),
    ...catLetters.map((l,i)=>{
      const ratio = catFull[i]?(catScore[i]/catFull[i]):0;
      const dir = ratio>=0.85?'up':(ratio>=0.7?'flat':'down');
      const arr = ratio>=0.85?'<span class="delta-arrow"></span>':'';
      return kpiBox(`${l}群：${catLabels[i].slice(0,14)}`, `${catScore[i]} / ${catFull[i]}`, '点',
        `<div class="delta delta-${dir}">${arr}達成率 ${(ratio*100).toFixed(0)}%（${cats[l].items.length}項目）</div>`);
    }),
  ].join('');

  /* Radar */
  new Chart($('#chart-diag-radar'),{
    type:'radar',
    data:{labels:catLabels, datasets:[{
      label:'カテゴリ平均', data:catAvg, fill:true,
      backgroundColor:'rgba(0,23,193,.12)', borderColor:COLORS.primary,
      pointBackgroundColor:COLORS.primary, borderWidth:2, pointRadius:3
    }]},
    options:{responsive:true, maintainAspectRatio:false,
      scales:{r:{min:0,max:5,ticks:{stepSize:1, color:'#595959'}, grid:{color:'#ededed'}, angleLines:{color:'#ededed'}, pointLabels:{font:{size:11}}}},
      plugins:{legend:{display:false}, tooltip:{backgroundColor:'#212121'}}
    }
  });

  $('#diag-cat-desc').innerHTML = catLetters.map((l,i)=>`
    <div style="margin-bottom:12px;padding:10px 12px;background:var(--cell-bg);border-radius:4px;border-left:3px solid var(--blue)">
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">
        <span class="diag-cat ${l}">${l}</span>
        <b style="font-size:13px">${esc(catLabels[i])}</b>
        <span class="score-pill score-${Math.round(catAvg[i])}">${catScore[i]}/${catFull[i]}</span>
      </div>
      <div class="small">${esc(cats[l].desc||'')}</div>
    </div>
  `).join('');

  /* 20-item table — grouped by category */
  let html = '<tr>'
    + '<th style="width:48px">No.</th>'
    + '<th style="width:64px">群</th>'
    + '<th style="width:16%">診断項目</th>'
    + '<th>評価ポイント</th>'
    + '<th class="num" style="width:70px">評価点</th>'
    + '<th>理由</th>'
    + '</tr>';
  catLetters.forEach((l,i)=>{
    const items = cats[l].items;
    const ratio = catFull[i]?(catScore[i]/catFull[i]):0;
    const ratioPct = (ratio*100).toFixed(0);
    html += `<tr style="background:var(--cell-bg)"><td colspan="6" style="padding:10px 12px;border-top:2px solid var(--line)">
      <span class="diag-cat ${l}">${l}</span>
      <b style="font-size:13px">${esc(catLabels[i])}</b>
      <span class="score-pill score-${Math.round(catAvg[i])}" style="margin-left:10px">${catScore[i]}/${catFull[i]}点（${ratioPct}%）</span>
      <span class="small" style="margin-left:8px">${esc(cats[l].desc||'')}</span>
    </td></tr>`;
    items.forEach(r=>{
      const sc = Number(r.score)||0;
      html += `<tr>
        <td class="num">${esc(r.no)}</td>
        <td><span class="diag-cat ${r.group||l}">${esc(r.group||l)}</span></td>
        <td><b>${esc(r.item)}</b></td>
        <td class="small">${esc(r.point)}</td>
        <td class="num"><span class="score-pill score-${sc}">${sc}</span></td>
        <td class="small" style="white-space:pre-wrap">${esc(r.reason)}</td>
      </tr>`;
    });
  });
  $('#tbl-diag').innerHTML = html;
}
renderDiag();

/* =========================================================== */
/* ① 基礎診断｜評点定義                                        */
/* =========================================================== */
function renderRubric(){
  const R = DATA.rubric;
  if(!R || !R.groups || !R.items){ return; }

  /* カテゴリ説明テーブル */
  let gh = '<tr><th style="width:80px">群</th><th style="width:32%">カテゴリ名</th><th>説明</th><th class="num" style="width:90px">項目数</th></tr>';
  R.groups.forEach(g=>{
    const cnt = R.items.filter(it=>it.group===g.code).length;
    gh += `<tr>
      <td><span class="diag-cat ${g.code}">${esc(g.code)}</span></td>
      <td><b>${esc(g.name)}</b></td>
      <td class="small">${esc(g.desc||'')}</td>
      <td class="num">${cnt}</td>
    </tr>`;
  });
  $('#tbl-rubric-groups').innerHTML = gh;

  /* 20項目評点定義テーブル */
  let html = '<tr>'
    + '<th style="width:48px">No.</th>'
    + '<th style="width:64px">群</th>'
    + '<th style="width:14%">診断項目</th>'
    + '<th>評価ポイント</th>'
    + '<th>確認方法</th>'
    + '<th style="width:18%;background:#e8f5e9">5点</th>'
    + '<th style="width:14%;background:#fff8e1">3点</th>'
    + '<th style="width:14%;background:#ffebee">1点</th>'
    + '</tr>';
  // 群ごとに区切り行
  const grouped = {};
  R.items.forEach(it=>{ (grouped[it.group] = grouped[it.group] || []).push(it); });
  R.groups.forEach(g=>{
    const list = grouped[g.code] || [];
    if(list.length===0) return;
    html += `<tr style="background:var(--cell-bg)"><td colspan="8" style="padding:8px 12px">
      <span class="diag-cat ${g.code}">${esc(g.code)}</span>
      <b style="font-size:13px">${esc(g.name)}</b>
      <span class="small" style="margin-left:8px">${esc(g.desc||'')}</span>
    </td></tr>`;
    list.forEach(it=>{
      html += `<tr>
        <td class="num">${esc(it.no)}</td>
        <td><span class="diag-cat ${it.group}">${esc(it.group)}</span></td>
        <td><b>${esc(it.item)}</b></td>
        <td class="small">${esc(it.point||'')}</td>
        <td class="small" style="white-space:pre-wrap">${esc(it.verify||'')}</td>
        <td class="small" style="background:#f1f8f4"><b style="color:#1b5e20">5点：</b>${esc(it.def_5||'')}</td>
        <td class="small" style="background:#fffaf1"><b style="color:#ef6c00">3点：</b>${esc(it.def_3||'')}</td>
        <td class="small" style="background:#fdf1f3"><b style="color:#c62828">1点：</b>${esc(it.def_1||'')}</td>
      </tr>`;
    });
  });
  $('#tbl-rubric').innerHTML = html;
}
renderRubric();

/* =========================================================== */
/* ② 結果指標 (SS・CV)                                         */
/* =========================================================== */
/* Shared flow preprocessing */
const FLOW = (function(){
  const F = DATA.flow;
  const months = F.months;
  const S = F.series;
  const cvSiteRaw = F.cv_site_total || months.map(()=>null);
  const cvOrgRaw  = F.cv_organic    || months.map(()=>null);
  const cvAiRaw   = F.cv_ai_total   || months.map(()=>null);
  const validIdx = months.map((m,i)=>m && (S.site_total[i]!=null||S.ai_total[i]!=null||S.ai_ratio[i]!=null||F.cv_total[i]!=null||cvSiteRaw[i]!=null||cvOrgRaw[i]!=null||cvAiRaw[i]!=null) ? i : -1).filter(i=>i>=0);
  const lbl = validIdx.map(i=>months[i].replace(/^(\d{4})-(\d{2})$/, (_,y,m)=>`${y.slice(2)}/${parseInt(m)}`));
  const pick = arr => validIdx.map(i=>arr[i]);
  const siteTotal = pick(S.site_total);
  const organic = pick(S.organic);
  const aiTotal = pick(S.ai_total);
  const aiRatio = pick(S.ai_ratio);
  const cvTotal = pick(F.cv_total);
  /* HubSpot derived: 全体CV / オーガニックCV / AI_REFERRALS CV (新規リード=レコード数) */
  const cvSite    = pick(cvSiteRaw);
  const cvOrg     = pick(cvOrgRaw);
  const cvAi      = pick(cvAiRaw);
  /* Period start (first valid month, used for lead text) */
  const firstMonth = months[validIdx[0]] || '';
  const startHuman = firstMonth ? firstMonth.replace('-','年').replace(/^(\d+)年(\d+)$/,(_,y,m)=>`${y}年${parseInt(m)}月`) : '';
  /* last & previous (based on siteTotal availability) */
  let lastI = siteTotal.length - 1;
  while(lastI>0 && siteTotal[lastI]==null) lastI--;
  const prevI = lastI>0 ? lastI-1 : null;
  const lastMonth = months[validIdx[lastI]] || '';
  const monthHuman = lastMonth ? lastMonth.replace('-','年').replace(/^(\d+)年(\d+)$/,(_,y,m)=>`${y}年${parseInt(m)}月`) : '';

  /* Forecast for in-progress month (when today's YYYY-MM matches lastMonth) */
  const today = new Date();
  const todayYM = `${today.getFullYear()}-${String(today.getMonth()+1).padStart(2,'0')}`;
  const inProgress = (lastMonth === todayYM);
  let daysElapsed = 0, daysInMonth = 0, forecastFactor = 1;
  if(inProgress){
    daysElapsed = today.getDate();
    daysInMonth = new Date(today.getFullYear(), today.getMonth()+1, 0).getDate();
    forecastFactor = daysInMonth / Math.max(1, daysElapsed);
  }
  const fcst = v => (inProgress && v!=null) ? Math.round(v * forecastFactor) : null;
  const fcstSite = fcst(siteTotal[lastI]);
  const fcstOrg  = fcst(organic[lastI]);
  const fcstAi   = fcst(aiTotal[lastI]);
  const fcstCv   = fcst(cvTotal[lastI]);
  const fcstRatio = (inProgress && fcstSite && fcstAi!=null) ? (fcstAi / fcstSite) : null;
  const fcstCvSite = fcst(cvSite[lastI]);
  const fcstCvOrg  = fcst(cvOrg[lastI]);
  const fcstCvAi   = fcst(cvAi[lastI]);

  return {F, months, S, validIdx, lbl, pick, siteTotal, organic, aiTotal, aiRatio, cvTotal,
    cvSite, cvOrg, cvAi,
    lastI, prevI, lastMonth, monthHuman, firstMonth, startHuman,
    inProgress, daysElapsed, daysInMonth, forecastFactor,
    fcstSite, fcstOrg, fcstAi, fcstCv, fcstRatio,
    fcstCvSite, fcstCvOrg, fcstCvAi};
})();

/* Year-start indicator: true at index 0 (so the first month column gets a divider
   between the label column and the data) and at every year boundary thereafter */
function yearStarts(lbl){
  const yr = l => { const m = String(l).match(/^(\d{2,4})/); return m ? m[1] : ''; };
  return lbl.map((l,i) => i===0 || yr(l) !== yr(lbl[i-1]));
}

/* Shared group breakdown table renderer */
function groupTableHTML(groups, lbl, pick){
  const yrs = yearStarts(lbl);
  const yc = i => yrs[i] ? ' year-start' : '';
  let h = `<tr><th>カテゴリ</th><th>LLM</th>${lbl.map((l,i)=>`<th class="num${yc(i)}">${esc(l)}</th>`).join('')}<th class="num">合計</th></tr>`;
  groups.forEach((g)=>{
    const total = pick(g.total);
    /* Insert line break before （ so e.g. 大手汎用LLM<br>（対話型LLM） */
    const lblHtml = esc(g.label).replace(/\n/g,'<br>').replace(/（/g,'<br>（');
    h += `<tr style="background:var(--cell-bg)"><td colspan="2" class="cat-cell"><b>${lblHtml}</b></td>${total.map((v,i)=>`<td class="num${yc(i)}"><b>${fmt(v)}</b></td>`).join('')}<td class="num"><b>${fmt(sum(total))}</b></td></tr>`;
    g.llms.forEach(l=>{
      const data = pick(l.data);
      h += `<tr><td></td><td class="llm-name">${esc(l.name)}</td>${data.map((v,i)=>`<td class="num${yc(i)}">${fmt(v)}</td>`).join('')}<td class="num">${fmt(sum(data))}</td></tr>`;
    });
  });
  return h;
}

/* ② SS（流入）タブ */
function renderFlowSS(){
  const {F, lbl, pick, siteTotal, organic, aiTotal, aiRatio, lastI, prevI, monthHuman, startHuman, validIdx,
         inProgress, daysElapsed, daysInMonth, forecastFactor,
         fcstSite, fcstOrg, fcstAi, fcstRatio} = FLOW;
  const lastSite = siteTotal[lastI];
  const prevSite = prevI!=null ? siteTotal[prevI] : null;
  const lastAi = aiTotal[lastI];
  const prevAi = prevI!=null ? aiTotal[prevI] : null;
  const lastOrg = organic[lastI];
  const prevOrg = prevI!=null ? organic[prevI] : null;
  const lastRatio = aiRatio[lastI];
  const prevRatio = prevI!=null ? aiRatio[prevI] : null;
  const siteAvg = avg(siteTotal.filter(x=>x!=null));
  const aiAvg = avg(aiTotal.filter(x=>x!=null));

  /* In-progress month forecast banner */
  if(inProgress){
    $('#flow-ss-forecast-banner').innerHTML = `
      <div style="background:#fff8e1;border:1px solid #ffd54f;border-left:4px solid #f57c00;border-radius:4px;padding:12px 16px;margin-bottom:14px;font-size:12.5px;color:var(--ink)">
        <b style="color:#bf5500">⏳ ${monthHuman}は途中（${daysElapsed}/${daysInMonth}日経過）</b>
        <div class="small" style="margin-top:4px;color:var(--ink2)">
          実績値（${daysElapsed}日分）から日数比例（×${forecastFactor.toFixed(2)}）で <b>当月着地予測</b> を算出。前月比は予測ベースで参考表示。
        </div>
      </div>`;
  } else {
    $('#flow-ss-forecast-banner').innerHTML = '';
  }

  /* Hero */
  let trend = '';
  const heroSiteVal = inProgress ? fcstSite : lastSite;
  const heroSiteLabel = inProgress ? '着地予測' : '実績';
  if(prevSite!=null && heroSiteVal!=null){
    const ratio = (heroSiteVal-prevSite)/prevSite;
    const sign = ratio>0?'+':'';
    trend = `<span class="answer">前月比 ${sign}${(ratio*100).toFixed(1)}%${inProgress?'（予測）':''}</span>`;
  }
  const heroRatio = inProgress ? fcstRatio : lastRatio;
  const heroRatioLabel = inProgress ? '着地予測比率' : 'AI 経由比率';
  $('#flow-ss-title').innerHTML = `${monthHuman}のサイト流入${inProgress?'(着地予測)':''}は ${fmt(heroSiteVal)} 件、${trend}<span class="sub-h">— ${heroRatioLabel} ${pct(heroRatio)}（前月差 ${prevRatio!=null&&heroRatio!=null?((heroRatio-prevRatio)*100>=0?'+':'')+((heroRatio-prevRatio)*100).toFixed(2)+'pt':'—'}）</span>`;
  $('#flow-ss-lead').textContent = `期間：${startHuman}〜${monthHuman}（${validIdx.length}か月分）。期間平均の月間流入は ${fmt(Math.round(siteAvg))} 件。${inProgress?`なお ${monthHuman}実績は ${fmt(lastSite)} 件（${daysElapsed}/${daysInMonth}日時点）。`:''}`;

  $('#flow-ss-chart-note').textContent = `期間平均（${fmt(Math.round(siteAvg))}件）を基準線として表示。サイト全体流入を強調色（青）、参考値（オーガニック・AI経由）はグレー。${inProgress?'【'+monthHuman+'は着地予測を点線で延伸】':''}`;
  $('#flow-ss-ai-chart-note').textContent = `AI経由流入のみを抽出した月次推移。期間平均は ${fmt(Math.round(aiAvg))} 件/月。${inProgress?'当月（'+monthHuman+'）は実績＋着地予測（'+fmt(fcstAi)+'件）の予測点も表示。':''}`;
  if(inProgress){ const lg=$('#flow-ss-ai-fc-legend'); if(lg) lg.style.display='inline-flex'; }

  /* KPI — 4枚（CVは別タブ）— 進行中月は着地予測と前月比 */
  const kpiSite = inProgress
    ? kpiBox('サイト全体流入（着地予測）', fmt(fcstSite), '件',
        `<div class="delta delta-flat">実績 ${fmt(lastSite)}件 → 予測 ${fmt(fcstSite)}件</div>${deltaHTML(fcstSite, prevSite)}`, true)
    : kpiBox('サイト全体流入', fmt(lastSite), '件', deltaHTML(lastSite, prevSite), true);
  const kpiOrg = inProgress
    ? kpiBox('オーガニック流入（着地予測）', fmt(fcstOrg), '件',
        `<div class="delta delta-flat">実績 ${fmt(lastOrg)}件</div>${deltaHTML(fcstOrg, prevOrg)}`)
    : kpiBox('オーガニック流入', fmt(lastOrg), '件', deltaHTML(lastOrg, prevOrg));
  const kpiAi = inProgress
    ? kpiBox('AI経由流入（着地予測）', fmt(fcstAi), '件',
        `<div class="delta delta-flat">実績 ${fmt(lastAi)}件</div>${deltaHTML(fcstAi, prevAi)}`)
    : kpiBox('AI経由流入', fmt(lastAi), '件', deltaHTML(lastAi, prevAi));
  const kpiRatio = inProgress
    ? kpiBox('AI経由比率（着地予測）', fcstRatio!=null?(fcstRatio*100).toFixed(2):'—', '%',
        `<div class="delta delta-flat">実績比率 ${lastRatio!=null?(lastRatio*100).toFixed(2):'—'}%</div>${deltaHTML(fcstRatio, prevRatio, {isPct:true})}`)
    : kpiBox('AI経由比率', lastRatio!=null?(lastRatio*100).toFixed(2):'—', '%', deltaHTML(lastRatio, prevRatio, {isPct:true}));
  $('#flow-ss-kpis').innerHTML = [kpiSite, kpiOrg, kpiAi, kpiRatio].join('');

  /* Forecast overlay arrays (only last point has value, marker only) */
  const fcstSiteArr = siteTotal.map((_,i)=> (inProgress && i===lastI) ? fcstSite : null);
  const fcstAiArr   = aiTotal.map((_,i)=> (inProgress && i===lastI) ? fcstAi : null);

  /* Site total chart */
  new Chart($('#chart-site-total'),{
    type:'line',
    data:{labels:lbl, datasets:[
      {label:'オーガニック流入数', data:organic, borderColor:COLORS.muted, backgroundColor:'transparent', borderWidth:1.5, tension:.25, pointRadius:0, yAxisID:'y'},
      {label:'AI経由流入数', data:aiTotal, borderColor:COLORS.mutedLight, backgroundColor:'transparent', borderWidth:1.5, tension:.25, pointRadius:0, yAxisID:'y'},
      {label:'サイト全体流入数', data:siteTotal, borderColor:COLORS.primary, backgroundColor:COLORS.primarySoft, fill:true, borderWidth:2.5, tension:.25, pointRadius:0, pointBackgroundColor:COLORS.primary, pointHoverRadius:4, yAxisID:'y'},
      {label:'当月着地予測', data:fcstSiteArr, borderColor:COLORS.primary, backgroundColor:'transparent', borderWidth:0, pointRadius:6, pointStyle:'rectRot', pointBackgroundColor:'rgba(0,23,193,.4)', pointBorderColor:COLORS.primary, pointBorderWidth:1.5, yAxisID:'y', showLine:false, spanGaps:false},
      {label:'期間平均', data:siteTotal.map(()=>siteAvg), borderColor:COLORS.ref, backgroundColor:'transparent', borderDash:[5,4], borderWidth:1, pointRadius:0, yAxisID:'y'},
      {label:'AI経由比率', data:aiRatio.map(v=>v==null?null:v*100), borderColor:'#7986cb', backgroundColor:'transparent', borderWidth:1.5, tension:.25, pointRadius:0, borderDash:[2,2], yAxisID:'y2', spanGaps:true},
    ]},
    options:{responsive:true, maintainAspectRatio:false,
      interaction:{mode:'index', intersect:false},
      scales:{
        x:{grid:{color:'#ededed'}, ticks:{color:'#595959'}},
        y:{beginAtZero:true, position:'left', grid:{color:'#ededed'}, ticks:{color:'#595959'}, title:{display:true, text:'流入数（件）', color:'#595959', font:{size:10}}},
        y2:{beginAtZero:true, position:'right', grid:{drawOnChartArea:false}, ticks:{color:'#595959', callback:v=>v+'%'}, title:{display:true, text:'AI経由比率 (%)', color:'#595959', font:{size:10}}}
      },
      plugins:{legend:{display:false}, tooltip:{backgroundColor:'#212121', titleFont:{size:11}, bodyFont:{size:11}}}
    }
  });

  /* AI-only line chart (NEW) */
  new Chart($('#chart-ai-total'),{
    type:'line',
    data:{labels:lbl, datasets:[
      {label:'AI経由流入数', data:aiTotal, borderColor:COLORS.cat[1]||'#3949ab', backgroundColor:'rgba(57,73,171,.10)', fill:true, borderWidth:2.5, tension:.25, pointRadius:3, pointBackgroundColor:COLORS.cat[1]||'#3949ab', pointHoverRadius:5},
      {label:'当月着地予測', data:fcstAiArr, borderColor:'#7986cb', backgroundColor:'transparent', borderWidth:0, pointRadius:7, pointStyle:'rectRot', pointBackgroundColor:'rgba(121,134,203,.5)', pointBorderColor:'#3949ab', pointBorderWidth:1.5, showLine:false},
      {label:'期間平均', data:aiTotal.map(()=>aiAvg), borderColor:COLORS.ref, backgroundColor:'transparent', borderDash:[5,4], borderWidth:1, pointRadius:0},
    ]},
    options:{responsive:true, maintainAspectRatio:false,
      interaction:{mode:'index', intersect:false},
      scales:{
        x:{grid:{color:'#ededed'}, ticks:{color:'#595959'}},
        y:{beginAtZero:true, grid:{color:'#ededed'}, ticks:{color:'#595959'}, title:{display:true, text:'AI経由流入数（件）', color:'#595959', font:{size:10}}}
      },
      plugins:{legend:{display:false}, tooltip:{backgroundColor:'#212121', titleFont:{size:11}, bodyFont:{size:11}}}
    }
  });

  /* Flow groups stacked */
  const flowDatasets = F.flow_groups.map((g,i)=>({
    label: g.label.replace(/\n/g,' / '),
    data: pick(g.total),
    backgroundColor: COLORS.cat[i % COLORS.cat.length],
    borderColor:'#fff', borderWidth:1, stack:'flow'
  }));
  new Chart($('#chart-flow-groups'),{
    type:'bar',
    data:{labels:lbl, datasets:flowDatasets},
    options:{responsive:true, maintainAspectRatio:false,
      scales:{y:{stacked:true,beginAtZero:true,grid:{color:'#ededed'},ticks:{color:'#595959'}},x:{stacked:true,grid:{display:false},ticks:{color:'#595959'}}},
      plugins:{legend:{position:'bottom', labels:{boxWidth:12, color:'#595959'}}, tooltip:{backgroundColor:'#212121'}}
    }
  });

  /* SS summary table（CVを除く） */
  const ssYrs = yearStarts(lbl);
  const ssYc = i => ssYrs[i] ? ' year-start' : '';
  let st = `<tr><th>項目</th>${lbl.map((l,i)=>`<th class="num${ssYc(i)}">${esc(l)}</th>`).join('')}<th class="num">合計</th></tr>`;
  const seriesRows = [
    ['サイト全体流入数', siteTotal, fmt],
    ['オーガニック流入数', organic, fmt],
    ['AI経由流入数', aiTotal, fmt],
    ['AI経由比率', aiRatio, v=>v==null?'':pct(v)],
  ];
  seriesRows.forEach(([name, arr, fn])=>{
    const total = name==='AI経由比率' ? '' : fmt(sum(arr));
    st += `<tr><td><b>${esc(name)}</b></td>${arr.map((v,i)=>`<td class="num${ssYc(i)}">${fn(v)}</td>`).join('')}<td class="num"><b>${total}</b></td></tr>`;
  });
  $('#tbl-series-ss').innerHTML = st;

  /* Group breakdown */
  $('#tbl-flow-groups').innerHTML = groupTableHTML(F.flow_groups, lbl, pick);
}

/* ② CV（コンバージョン）タブ */
function renderFlowCV(){
  const {F, lbl, pick, aiTotal, cvTotal, cvSite, cvOrg, cvAi, lastI, prevI, monthHuman, startHuman, validIdx,
         inProgress, daysElapsed, daysInMonth,
         fcstCvSite, fcstCvOrg, fcstCvAi} = FLOW;
  const lastCv = cvTotal[lastI];
  const prevCv = prevI!=null ? cvTotal[prevI] : null;
  const lastSite = cvSite[lastI], prevSite = prevI!=null?cvSite[prevI]:null;
  const lastOrg  = cvOrg[lastI],  prevOrg  = prevI!=null?cvOrg[prevI]:null;
  const lastAi   = cvAi[lastI],   prevAi   = prevI!=null?cvAi[prevI]:null;
  const cvSum = sum(cvTotal);
  /* Find max month for AI-CV (LLM-tracked) */
  let maxV = -1, maxIdx = -1;
  cvTotal.forEach((v,i)=>{ if(v!=null && v>maxV){ maxV=v; maxIdx=i; } });
  const maxLbl = maxIdx>=0 ? lbl[maxIdx] : '—';
  /* AI流入CV率 (累計ベース, HubSpot基準) */
  const siteSum = sum(cvSite), orgSum = sum(cvOrg), aiCvSum = sum(cvAi);
  const aiCvRatio = siteSum>0 ? aiCvSum/siteSum : null;
  const lastAiRatio = (lastSite && lastAi!=null) ? lastAi/lastSite : null;
  const prevAiRatio = (prevSite && prevAi!=null) ? prevAi/prevSite : null;

  /* Forecast banner (in-progress month) */
  if(inProgress){
    $('#flow-cv-forecast-banner').innerHTML = `
      <div class="card" style="background:#fff8e1;border:1px solid #ffe082;padding:10px 12px;margin-bottom:8px">
        <span style="font-weight:600;color:#b08800">⚠️ ${monthHuman} は進行中（${daysElapsed}/${daysInMonth}日）</span>
        — 当月CVは <b>実績</b> と <b>着地予測</b>（実績 × ${(daysInMonth/Math.max(1,daysElapsed)).toFixed(2)}）の両方を表示しています。
      </div>`;
    const lg = $('#flow-cv-site-fc-legend'); if(lg) lg.style.display='inline-flex';
  } else {
    $('#flow-cv-forecast-banner').innerHTML = '';
  }

  /* Hero — answer-first (HubSpot Total CV) */
  const heroSiteVal = inProgress ? fcstCvSite : lastSite;
  let trend = '';
  if(prevSite!=null && heroSiteVal!=null){
    const diff = heroSiteVal - prevSite;
    const sign = diff>0?'+':'';
    const pctTxt = prevSite>0 ? ` (${sign}${(diff/prevSite*100).toFixed(1)}%)` : '';
    trend = `<span class="answer">前月差 ${sign}${fmt(diff)} 件${pctTxt}</span>`;
  }
  const heroAiRatio = inProgress && fcstCvSite ? (fcstCvAi||0)/fcstCvSite : lastAiRatio;
  const ratioTxt = heroAiRatio!=null ? `${(heroAiRatio*100).toFixed(2)}%` : '—';
  $('#flow-cv-title').innerHTML = `${monthHuman}の<b>サイト全体CV</b>は ${fmt(heroSiteVal)} 件${inProgress?'（着地予測）':''}、${trend}<span class="sub-h">— うち AI経由 ${fmt(inProgress?fcstCvAi:lastAi)} 件（${ratioTxt}）</span>`;
  $('#flow-cv-lead').textContent = `期間：${startHuman}〜${monthHuman}（${validIdx.length}か月分）。期間累計：全体 ${fmt(siteSum)} 件 / オーガニック ${fmt(orgSum)} 件 / AI経由 ${fmt(aiCvSum)} 件（HubSpot基準・新規リード）。${inProgress?`当月（${monthHuman}）実績は ${fmt(lastSite)} 件（${daysElapsed}/${daysInMonth}日時点）。`:''}`;

  $('#flow-cv-site-chart-note').textContent = `期間平均（${fmt(Math.round(siteSum/Math.max(1,validIdx.length)))}件/月）を基準線に表示。サイト全体CVを強調色（青）、オーガニック・AI経由CVは参考値（グレー）。${inProgress?'【'+monthHuman+'は着地予測点を菱形で表示】':''}`;
  $('#flow-cv-chart-note').textContent = `月次AI経由CV件数（GA4×LLM分類ベース）。点線は期間平均（${(cvSum/Math.max(1,validIdx.length)).toFixed(2)}件/月）。`;

  /* KPI — 4枚 (Total / Organic / AI / AI Ratio) — SSと統一 */
  const kpiSite = inProgress
    ? kpiBox('サイト全体CV（着地予測）', fmt(fcstCvSite), '件',
        `<div class="delta delta-flat">実績 ${fmt(lastSite)}件 → 予測 ${fmt(fcstCvSite)}件</div>${deltaHTML(fcstCvSite, prevSite)}`, true)
    : kpiBox('当月 サイト全体CV', fmt(lastSite), '件', deltaHTML(lastSite, prevSite), true);
  const kpiOrg = inProgress
    ? kpiBox('オーガニックCV（着地予測）', fmt(fcstCvOrg), '件',
        `<div class="delta delta-flat">実績 ${fmt(lastOrg)}件</div>${deltaHTML(fcstCvOrg, prevOrg)}`)
    : kpiBox('当月 オーガニックCV', fmt(lastOrg), '件', deltaHTML(lastOrg, prevOrg));
  const kpiAi = inProgress
    ? kpiBox('AI経由CV（着地予測）', fmt(fcstCvAi), '件',
        `<div class="delta delta-flat">実績 ${fmt(lastAi)}件</div>${deltaHTML(fcstCvAi, prevAi)}`)
    : kpiBox('当月 AI経由CV', fmt(lastAi), '件', deltaHTML(lastAi, prevAi));
  let kpiRatio;
  if(inProgress && fcstCvSite){
    const r = (fcstCvAi||0)/fcstCvSite;
    const dpt = (prevAiRatio!=null) ? ((r-prevAiRatio)*100) : null;
    const dHtml = dpt!=null ? `<div class="delta ${dpt>=0?'delta-up':'delta-down'}">${dpt>=0?'+':''}${dpt.toFixed(2)}pt</div>` : '<div class="delta delta-flat">—</div>';
    kpiRatio = kpiBox('AI経由CV比率（予測）', (r*100).toFixed(2), '%', `<div class="delta delta-flat">予測ベース</div>${dHtml}`);
  } else {
    const r = lastAiRatio;
    const dpt = (prevAiRatio!=null && r!=null) ? ((r-prevAiRatio)*100) : null;
    const dHtml = dpt!=null ? `<div class="delta ${dpt>=0?'delta-up':'delta-down'}">${dpt>=0?'+':''}${dpt.toFixed(2)}pt</div>` : '<div class="delta delta-flat">—</div>';
    kpiRatio = kpiBox('当月 AI経由CV比率', r!=null?(r*100).toFixed(2):'—', '%', dHtml);
  }
  $('#flow-cv-kpis').innerHTML = [kpiSite, kpiOrg, kpiAi, kpiRatio].join('');

  /* Total CV chart (Site強調 + Organic/AI参考 + 期間平均 + 着地予測点) */
  const siteAvg = siteSum / Math.max(1, validIdx.length);
  const fcstSiteArr = cvSite.map((_,i)=> (inProgress && i===lastI) ? fcstCvSite : null);
  new Chart($('#chart-cv-site'),{
    type:'line',
    data:{labels:lbl, datasets:[
      {label:'サイト全体CV', data:cvSite, borderColor:COLORS.primary, backgroundColor:'rgba(0,23,193,0.06)', borderWidth:2.5, pointRadius:3, pointBackgroundColor:COLORS.primary, fill:true, tension:0.25, order:2},
      {label:'オーガニックCV', data:cvOrg, borderColor:'#9e9e9e', backgroundColor:'transparent', borderWidth:1.2, pointRadius:2, pointBackgroundColor:'#9e9e9e', tension:0.25, order:3},
      {label:'AI経由CV', data:cvAi, borderColor:'#cfcfcf', backgroundColor:'transparent', borderWidth:1, pointRadius:2, pointBackgroundColor:'#cfcfcf', borderDash:[3,3], tension:0.25, order:4},
      {label:'期間平均', data:cvSite.map(()=>siteAvg), borderColor:COLORS.ref, backgroundColor:'transparent', borderDash:[5,4], borderWidth:1, pointRadius:0, order:1},
      {label:'当月着地予測', data:fcstSiteArr, borderColor:COLORS.primary, backgroundColor:'transparent', borderWidth:0, pointRadius:6, pointStyle:'rectRot', pointBackgroundColor:'rgba(0,23,193,.4)', pointBorderColor:COLORS.primary, pointBorderWidth:1.5, showLine:false, spanGaps:false},
    ]},
    options:{responsive:true, maintainAspectRatio:false,
      interaction:{mode:'index', intersect:false},
      scales:{
        x:{grid:{display:false}, ticks:{color:'#595959'}},
        y:{beginAtZero:true, grid:{color:'#ededed'}, ticks:{color:'#595959'}, title:{display:true, text:'CV件数 (新規リード)', color:'#595959', font:{size:10}}}
      },
      plugins:{legend:{display:false}, tooltip:{backgroundColor:'#212121'}}
    }
  });

  /* AI-CV bar chart with reference line (existing chart) */
  const cvAvg = cvSum / Math.max(1, validIdx.length);
  new Chart($('#chart-cv-line'),{
    type:'bar',
    data:{labels:lbl, datasets:[
      {type:'bar', label:'AI経由CV件数', data:cvTotal, backgroundColor:COLORS.primary, borderColor:COLORS.primary, borderWidth:0, order:2},
      {type:'line', label:'期間平均', data:cvTotal.map(()=>cvAvg), borderColor:COLORS.ref, backgroundColor:'transparent', borderDash:[5,4], borderWidth:1, pointRadius:0, order:1},
    ]},
    options:{responsive:true, maintainAspectRatio:false,
      interaction:{mode:'index', intersect:false},
      scales:{
        x:{grid:{display:false}, ticks:{color:'#595959'}},
        y:{beginAtZero:true, grid:{color:'#ededed'}, ticks:{color:'#595959', stepSize:1}, title:{display:true, text:'CV件数', color:'#595959', font:{size:10}}}
      },
      plugins:{legend:{display:false}, tooltip:{backgroundColor:'#212121'}}
    }
  });

  /* CV groups stacked */
  const cvDatasets = F.cv_groups.map((g,i)=>({
    label: g.label.replace(/\n/g,' / '),
    data: pick(g.total),
    backgroundColor: COLORS.cat[i % COLORS.cat.length],
    borderColor:'#fff', borderWidth:1, stack:'cv'
  }));
  new Chart($('#chart-cv-groups'),{
    type:'bar',
    data:{labels:lbl, datasets:cvDatasets},
    options:{responsive:true, maintainAspectRatio:false,
      scales:{y:{stacked:true,beginAtZero:true,grid:{color:'#ededed'},ticks:{color:'#595959',stepSize:1}},x:{stacked:true,grid:{display:false},ticks:{color:'#595959'}}},
      plugins:{legend:{position:'bottom', labels:{boxWidth:12, color:'#595959'}}, tooltip:{backgroundColor:'#212121'}}
    }
  });

  /* CV summary table（HubSpot基準・月次＋累計行） */
  const aiSum = sum(aiTotal);
  let cum = 0;
  const cumArr = cvTotal.map(v=>{ cum += (v||0); return cum; });
  const ratioArr = cvSite.map((s,i)=>{
    const a = cvAi[i];
    return (s && a!=null) ? (a/s*100) : null;
  });
  const cvYrs = yearStarts(lbl);
  const cvYc = i => cvYrs[i] ? ' year-start' : '';
  let ct = `<tr><th>項目</th>${lbl.map((l,i)=>`<th class="num${cvYc(i)}">${esc(l)}</th>`).join('')}<th class="num">合計</th></tr>`;
  ct += `<tr><td><b>サイト全体CV</b></td>${cvSite.map((v,i)=>`<td class="num${cvYc(i)}">${fmt(v)}</td>`).join('')}<td class="num"><b>${fmt(siteSum)}</b></td></tr>`;
  ct += `<tr><td><b>オーガニックCV</b></td>${cvOrg.map((v,i)=>`<td class="num${cvYc(i)}">${fmt(v)}</td>`).join('')}<td class="num"><b>${fmt(orgSum)}</b></td></tr>`;
  ct += `<tr><td><b>AI経由CV</b></td>${cvAi.map((v,i)=>`<td class="num${cvYc(i)}">${fmt(v)}</td>`).join('')}<td class="num"><b>${fmt(aiCvSum)}</b></td></tr>`;
  ct += `<tr><td><b>AI経由CV比率</b></td>${ratioArr.map((v,i)=>`<td class="num${cvYc(i)}">${v!=null?v.toFixed(2)+'%':'—'}</td>`).join('')}<td class="num"><b>${siteSum>0?(aiCvSum/siteSum*100).toFixed(2)+'%':'—'}</b></td></tr>`;
  $('#tbl-series-cv').innerHTML = ct;

  /* CV groups breakdown */
  $('#tbl-cv-groups').innerHTML = groupTableHTML(F.cv_groups, lbl, pick);
}
renderFlowSS();
renderFlowCV();

/* =========================================================== */
/* ③ 調査PR関連プロンプト                                      */
/* =========================================================== */
function renderMD(text){
  if(!text) return '';
  /* Pre-clean: collapse 3+ blank lines to 2 (paragraph break) */
  let raw = String(text).replace(/[ \t]+\n/g,'\n').replace(/\n{3,}/g,'\n\n').trim();
  let html = esc(raw);
  html = html.replace(/^\*\s*\*\s*\*/gm, '<hr>');
  html = html.replace(/^---+$/gm, '<hr>');
  html = html.replace(/^#{4}\s+(.+)$/gm, '<h4>$1</h4>');
  html = html.replace(/^#{3}\s+(.+)$/gm, '<h3>$1</h3>');
  html = html.replace(/^#{2}\s+(.+)$/gm, '<h2>$1</h2>');
  html = html.replace(/^#\s+(.+)$/gm, '<h1>$1</h1>');
  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
  const lines = html.split('\n');
  const out = [];
  let inUL = false;
  for(const ln of lines){
    const m = ln.match(/^(\s*)[\*\-]\s+(.*)$/);
    if(m && !ln.includes('<hr>')){
      if(!inUL){ out.push('<ul>'); inUL=true; }
      out.push('<li>'+m[2]+'</li>');
    } else {
      if(inUL){ out.push('</ul>'); inUL=false; }
      out.push(ln);
    }
  }
  if(inUL) out.push('</ul>');
  let s = out.join('\n');
  /* Strip newlines hugging block-level tags (no extra blank lines around <h*> / <ul> / <hr>) */
  s = s.replace(/\n*(<\/?(?:h[1-6]|ul|ol|li|hr|blockquote)[^>]*>)\n*/g, '$1');
  /* Collapse paragraph breaks to a single <br><br>, then single newlines to <br> */
  s = s.replace(/\n{2,}/g, '<br><br>');
  s = s.replace(/\n/g, '<br>');
  /* Defensive: never more than two <br> in a row */
  s = s.replace(/(<br\s*\/?>\s*){3,}/g, '<br><br>');
  /* Trim stray <br> at start/end */
  s = s.replace(/^(\s*<br\s*\/?>\s*)+/i, '').replace(/(\s*<br\s*\/?>\s*)+$/i, '');
  return s;
}

/* Highlight brand mentions ("IDEATECH" / "リサピー" / "アイデアテック" / "PRIZMA")
   in already-rendered HTML. Splits by tags so we never wrap inside attributes. */
function highlightBrands(html){
  if(!html) return html;
  const parts = String(html).split(/(<[^>]*>)/);
  const reBrand = /(IDEATECH|アイデアテック|リサピー)/gi;
  const reCompetitor = /(PRIZMA|プリズマ)/gi;
  return parts.map((p,i)=>{
    if(i % 2 === 1) return p; /* tag — leave untouched */
    return p
      .replace(reBrand, '<mark class="hl-brand">$1</mark>')
      .replace(reCompetitor, '<mark class="hl-competitor">$1</mark>');
  }).join('');
}

/* =========================================================== */
/* ③-A 推奨状況 一覧表 (matrix)                                */
/* =========================================================== */
function renderPromptsMatrix(){
  const P = DATA.prompts;
  if(P.survey_date){
    $('#matrix-survey-date').innerHTML = `｜調査日：<b>${esc(P.survey_date)}</b>`;
  }
  const llms = P.llms;

  function classify(v){
    if(v==='⚫︎'||v==='●'||v==='◉') return 'r2';
    if(v==='▲') return 'r1';
    return 'r0';
  }
  function symChar(cls){ return cls==='r2'?'⚫︎':(cls==='r1'?'▲':'‐'); }

  /* Hero / KPI */
  const totalCells = P.rows.length * llms.length;
  const idxCounts = {r2:[0,0,0,0], r1:[0,0,0,0], r0:[0,0,0,0]};
  const przCounts = {r2:[0,0,0,0], r1:[0,0,0,0], r0:[0,0,0,0]};
  P.rows.forEach(r=>{
    llms.forEach((_,i)=>{
      idxCounts[classify(r.ideatech[i])][i]++;
      przCounts[classify(r.prizma[i])][i]++;
    });
  });
  const idxR2 = sum(idxCounts.r2);
  const idxR1 = sum(idxCounts.r1);
  const przR2 = sum(przCounts.r2);
  const przR1 = sum(przCounts.r1);

  $('#matrix-title').innerHTML = `IDEATECH／リサピー の言及率（⚫︎）は <span class="answer">${idxR2} / ${totalCells}（${(idxR2/totalCells*100).toFixed(1)}%）</span><span class="sub-h">— 競合 PRIZMA は ${przR2} / ${totalCells}（${(przR2/totalCells*100).toFixed(1)}%）。差分 ${idxR2-przR2>=0?'+':''}${idxR2-przR2}件</span>`;
  $('#matrix-lead').textContent = `40プロンプト × 4LLM = 160セル のうち、IDEATECH／リサピー の言及ありは ${idxR2}件、言及なしは ${idxR1}件。LLM別の強弱が一目で分かるよう左固定の3列（No./分類/プロンプト）と横スクロールで全LLMを並べています。`;

  $('#matrix-kpis').innerHTML = [
    kpiBox('IDEATECH 言及あり ⚫︎', `${idxR2} / ${totalCells}`, '件', `<div class="delta delta-flat">言及率 ${(idxR2/totalCells*100).toFixed(1)}%</div>`, true),
    kpiBox('IDEATECH 言及なし ▲', `${idxR1} / ${totalCells}`, '件', `<div class="delta delta-flat">非言及率 ${(idxR1/totalCells*100).toFixed(1)}%</div>`),
    kpiBox('PRIZMA 言及あり ⚫︎', `${przR2} / ${totalCells}`, '件', `<div class="delta delta-flat">言及率 ${(przR2/totalCells*100).toFixed(1)}%</div>`),
    kpiBox('PRIZMA 言及なし ▲', `${przR1} / ${totalCells}`, '件', `<div class="delta delta-flat">非言及率 ${(przR1/totalCells*100).toFixed(1)}%</div>`),
  ].join('');

  /* Categories filter */
  const cats = [...new Set(P.rows.map(r=>r.category))].filter(Boolean);
  const sel = $('#matrix-cat');
  sel.innerHTML = '<option value="">全分類</option>' + cats.map(c=>`<option value="${esc(c)}">${esc(c.replace(/\s*\/?\s*\n\s*\/?\s*/g,' / ').trim())}</option>`).join('');

  const tbl = $('#tbl-matrix');
  const searchEl = $('#matrix-search');
  const countEl = $('#matrix-count');

  function paint(){
    const q = (searchEl.value||'').trim().toLowerCase();
    const selected = sel.value;
    const filtered = P.rows.filter(r=>{
      const text = ((r.prompt||'')+' '+(r.category||'')).toLowerCase();
      return (!q || text.includes(q)) && (!selected || r.category===selected);
    });

    let html = '<thead>';
    /* Group header row */
    html += '<tr class="h-group">'+
      '<th class="col-no"></th>'+
      '<th class="col-cat"></th>'+
      '<th class="col-prompt"></th>'+
      `<th class="idea-grp col-divider" colspan="${llms.length}">IDEATECH／リサピー 言及</th>`+
      `<th class="prz-grp col-divider" colspan="${llms.length}">競合①：PRIZMA 言及</th>`+
    '</tr>';
    /* Sub header */
    html += '<tr>'+
      '<th class="col-no">No.</th>'+
      '<th class="col-cat">分類</th>'+
      '<th class="col-prompt">プロンプト</th>'+
      llms.map((l,i)=>`<th class="cell-mark${i===0?' col-divider':''}">${esc(l)}</th>`).join('')+
      llms.map((l,i)=>`<th class="cell-mark${i===0?' col-divider':''}">${esc(l)}</th>`).join('')+
    '</tr>';
    html += '</thead><tbody>';

    filtered.forEach((r, idx)=>{
      /* Normalize category: split on \n optionally surrounded by / */
      const catFlat = (r.category||'').replace(/\s*\/?\s*\n\s*\/?\s*/g, ' / ').trim();
      const catHtml = esc(r.category||'').replace(/\s*\/?\s*\n\s*\/?\s*/g, '<br>');
      const promptText = r.prompt || '';
      const prevCat = idx>0 ? (filtered[idx-1].category||'') : null;
      const isCatStart = idx>0 && (r.category||'') !== prevCat;
      const trCls = isCatStart ? ' class="cat-block-start"' : '';
      html += `<tr${trCls}>
        <td class="col-no">${r.no}</td>
        <td class="col-cat" title="${esc(catFlat)}"><span class="p-text">${catHtml}</span></td>
        <td class="col-prompt" title="${esc(promptText)}"><a class="prompt-link" href="#prompt-${r.no}"><span class="p-text">${esc(promptText)}</span></a></td>
        ${llms.map((_,i)=>{const c=classify(r.ideatech[i]);return `<td class="cell-mark ${c}${i===0?' col-divider':''}">${symChar(c)}</td>`}).join('')}
        ${llms.map((_,i)=>{const c=classify(r.prizma[i]);return `<td class="cell-mark ${c}${i===0?' col-divider':''}">${symChar(c)}</td>`}).join('')}
      </tr>`;
    });

    /* Footer with per-LLM totals (within filtered set) */
    const fIdx = {r2:[0,0,0,0], r1:[0,0,0,0]};
    const fPrz = {r2:[0,0,0,0], r1:[0,0,0,0]};
    filtered.forEach(r=>{
      llms.forEach((_,i)=>{
        const ci = classify(r.ideatech[i]);
        if(ci==='r2') fIdx.r2[i]++; else if(ci==='r1') fIdx.r1[i]++;
        const cp = classify(r.prizma[i]);
        if(cp==='r2') fPrz.r2[i]++; else if(cp==='r1') fPrz.r1[i]++;
      });
    });
    const denom = filtered.length;
    html += `</tbody><tfoot>
      <tr>
        <td class="col-no" colspan="2"></td>
        <td class="col-prompt"><b>⚫︎ 言及あり（${denom}件中）</b></td>
        ${llms.map((_,i)=>`<td class="cell-mark${i===0?' col-divider':''}">${fIdx.r2[i]}</td>`).join('')}
        ${llms.map((_,i)=>`<td class="cell-mark${i===0?' col-divider':''}">${fPrz.r2[i]}</td>`).join('')}
      </tr>
      <tr>
        <td class="col-no" colspan="2"></td>
        <td class="col-prompt"><b>▲ 言及なし（${denom}件中）</b></td>
        ${llms.map((_,i)=>`<td class="cell-mark${i===0?' col-divider':''}">${fIdx.r1[i]}</td>`).join('')}
        ${llms.map((_,i)=>`<td class="cell-mark${i===0?' col-divider':''}">${fPrz.r1[i]}</td>`).join('')}
      </tr>
    </tfoot>`;

    tbl.innerHTML = html;
    countEl.textContent = `表示中 ${filtered.length} / 全 ${P.rows.length} 件`;
  }

  searchEl.addEventListener('input', paint);
  sel.addEventListener('change', paint);
  paint();
}
renderPromptsMatrix();

function renderPrompts(){
  const P = DATA.prompts;
  if(P.survey_date){
    $('#prompts-survey-date').innerHTML = `｜調査日：<b>${esc(P.survey_date)}</b>`;
  }
  const llms = P.llms;
  const llmKeys = llms.map(l=>l.toLowerCase());

  /* Compute mention rates */
  const ideaCount = [0,0,0,0];
  const prizmaCount = [0,0,0,0];
  const ideaRecoCount = [0,0,0,0];
  const prizmaRecoCount = [0,0,0,0];
  P.rows.forEach(r=>{
    llms.forEach((_,i)=>{
      const m = r.ideatech[i];
      if(m && m.trim()){ ideaCount[i]++; }
      if(m==='⚫︎'||m==='●'||m==='◉'){ ideaRecoCount[i]++; }
      const p = r.prizma[i];
      if(p && p.trim()){ prizmaCount[i]++; }
      if(p==='⚫︎'||p==='●'||p==='◉'){ prizmaRecoCount[i]++; }
    });
  });
  const ideaRecoTotal = sum(ideaRecoCount);
  const prizmaRecoTotal = sum(prizmaRecoCount);
  const totalCells = P.rows.length * llms.length;

  /* Hero */
  $('#prompts-title').innerHTML = `言及率（⚫︎）は <span class="answer">${(ideaRecoTotal/totalCells*100).toFixed(1)}%</span>（IDEATECH／リサピー、4LLM × ${P.rows.length}プロンプト）<span class="sub-h">— PRIZMA は ${(prizmaRecoTotal/totalCells*100).toFixed(1)}%（${prizmaRecoTotal}/${totalCells}件）</span>`;
  $('#prompts-lead').textContent = `IDEATECH／リサピー の LLM 別「言及あり」件数：${llms.map((l,i)=>`${l} ${ideaRecoCount[i]}/${P.rows.length}`).join('、')}`;

  /* KPI */
  $('#prompts-kpis').innerHTML = [
    kpiBox('プロンプト総数', fmt(P.rows.length), '件', '<div class="delta delta-flat">分類数 '+(new Set(P.rows.map(r=>r.category))).size+'</div>', true),
    kpiBox('IDEATECH 言及あり ⚫︎', `${ideaRecoTotal} / ${totalCells}`, '件', `<div class="delta delta-flat">言及率 ${(ideaRecoTotal/totalCells*100).toFixed(1)}%</div>`),
    kpiBox('IDEATECH 回答セル数', `${sum(ideaCount)} / ${totalCells}`, '件', `<div class="delta delta-flat">回収率 ${(sum(ideaCount)/totalCells*100).toFixed(1)}%</div>`),
    kpiBox('競合 PRIZMA 言及あり ⚫︎', `${prizmaRecoTotal} / ${totalCells}`, '件', `<div class="delta delta-flat">言及率 ${(prizmaRecoTotal/totalCells*100).toFixed(1)}%</div>`),
  ].join('');

  const cats = [...new Set(P.rows.map(r=>r.category))].filter(Boolean);
  const sel = $('#prompts-cat');
  sel.innerHTML = '<option value="">全分類</option>' + cats.map(c=>`<option value="${esc(c)}">${esc(c.replace(/\s*\/?\s*\n\s*\/?\s*/g,' / ').trim())}</option>`).join('');

  const searchEl = $('#prompts-search');
  const listEl = $('#prompts-list');
  const countEl = $('#prompts-count');

  function symbol(v){
    if(v==='⚫︎'||v==='●'||v==='◉') return '<span class="mark-reco r2">⚫︎</span>';
    if(v==='▲') return '<span class="mark-reco r1">▲</span>';
    return '<span class="mark-reco r0">‐</span>';
  }
  function buildRow(r){
    const catStr = (r.category||'').replace(/\s*\/?\s*\n\s*\/?\s*/g, ' / ').trim();
    const ideaCells = llms.map((l,i)=>`<div class="mention-cell"><span class="brand-name">${esc(l)}</span>${symbol(r.ideatech[i])}</div>`).join('');
    const prizmaCells = llms.map((l,i)=>`<div class="mention-cell"><span class="brand-name">${esc(l)}</span>${symbol(r.prizma[i])}</div>`).join('');
    const responses = llms.map((l,i)=>{
      const body = r.responses[i];
      const cls = llmKeys[i];
      const mentionCount = body ? ((String(body).match(/IDEATECH|アイデアテック|リサピー/gi)||[]).length) : 0;
      const badge = mentionCount>0 ? `<span class="mention-badge">言及 ${mentionCount}</span>` : '';
      return `<details><summary><span><span class="llm-tag ${cls}">${esc(l)}</span>応答全文（${body?body.length.toLocaleString('ja-JP')+' 文字':'なし'}）${badge}</span></summary><div class="detail-body">${highlightBrands(renderMD(body))}</div></details>`;
    }).join('');
    const volStr = r.volume!=null ? r.volume.toLocaleString('ja-JP') : '—';
    return `
      <div class="card prompt-card" id="prompt-${r.no}" data-cat="${esc(r.category||'')}" data-text="${esc((r.prompt||'')+' '+(r.category||''))}">
        <div class="prompt-header">
          <div class="no-badge">${r.no}</div>
          <div>
            <div class="prompt-text">${esc(r.prompt||'')}</div>
            <div class="meta">分類: ${esc(catStr)} ｜ ボリューム: ${volStr}</div>
          </div>
        </div>
        <div class="row2col">
          <div>
            <h4 style="margin:2px 0 6px">IDEATECH／リサピー 言及</h4>
            <div class="mention-grid">${ideaCells}</div>
          </div>
          <div>
            <h4 style="margin:2px 0 6px">競合①：PRIZMA 言及</h4>
            <div class="mention-grid">${prizmaCells}</div>
          </div>
        </div>
        <h4 style="margin-top:12px">各LLMの応答内容</h4>
        ${responses}
      </div>
    `;
  }

  function applyFilter(){
    const q = (searchEl.value||'').trim().toLowerCase();
    const selected = sel.value;
    let visible = 0;
    $$('.prompt-card', listEl).forEach(card=>{
      const text = (card.dataset.text||'').toLowerCase();
      const cat = card.dataset.cat||'';
      const matches = (!q || text.includes(q)) && (!selected || cat===selected);
      card.style.display = matches ? '' : 'none';
      if(matches) visible++;
    });
    countEl.textContent = `表示中 ${visible} / 全 ${P.rows.length} 件`;
  }

  listEl.innerHTML = P.rows.map(buildRow).join('');
  searchEl.addEventListener('input', applyFilter);
  sel.addEventListener('change', applyFilter);
  applyFilter();

  $('#prompts-notes').innerHTML = (P.footnotes||[]).map(n=>`<div>※ ${esc(n.replace(/^※/,''))}</div>`).join('');
}
renderPrompts();

/* Hash / direct navigation: when arriving at #prompt-N (e.g. from the matrix table),
   switch to the prompts section first, then auto-open all <details> inside the
   target card, scroll into view, and briefly highlight. */
function jumpToPrompt(no){
  if(!no) return;
  /* 1) Activate prompts section */
  $$('.section').forEach(s=>s.classList.remove('active'));
  const target = $('#sec-prompts');
  if(target) target.classList.add('active');
  navBtns.forEach(b=>b.classList.toggle('active', b.dataset.section==='prompts'));
  closeSidebar();
  /* 2) Update hash to #prompt-N (without firing hashchange recursion) */
  if(location.hash !== '#prompt-'+no){
    history.replaceState(null,'','#prompt-'+no);
  }
  /* 3) Find card, open details, scroll, highlight */
  const card = document.getElementById('prompt-'+no);
  if(!card) return;
  /* Make sure search/filter doesn't hide it */
  card.style.display = '';
  card.querySelectorAll('details').forEach(d => d.open = true);
  card.style.transition = 'box-shadow .25s';
  card.style.boxShadow = '0 0 0 3px var(--blue-soft)';
  setTimeout(()=>{ card.style.boxShadow = ''; }, 1600);
  /* Wait a tick so the section becomes visible before scrolling */
  setTimeout(()=>card.scrollIntoView({behavior:'smooth', block:'start'}), 80);
}
function openPromptByHash(){
  const m = (window.location.hash||'').match(/^#prompt-(\d+)/);
  if(!m) return;
  jumpToPrompt(m[1]);
}
/* Intercept clicks on matrix prompt links to bypass hashchange races */
document.addEventListener('click', (e)=>{
  const a = e.target.closest && e.target.closest('a.prompt-link');
  if(!a) return;
  const href = a.getAttribute('href')||'';
  const m = href.match(/^#prompt-(\d+)/);
  if(!m) return;
  e.preventDefault();
  jumpToPrompt(m[1]);
});
window.addEventListener('hashchange', openPromptByHash);
if(/^#prompt-/.test(window.location.hash)) setTimeout(openPromptByHash, 250);

/* =========================================================== */
/* ④ サイテーション                                            */
/* =========================================================== */
function renderCitation(prefix, dataKey, sheetLabel){
  const C = DATA[dataKey];
  const rows = C.rows;
  const summary = C.summary || {};

  /* DR helpers */
  const drNum = r => { const n = parseInt(String(r.dr||'').trim(),10); return Number.isFinite(n) ? n : -1; };
  const drTier = n => n>=90 ? 'top' : n>=70 ? 'high' : n>=50 ? 'mid' : n>0 ? 'low' : 'zero';
  const drPill = r => {
    const n = drNum(r);
    const t = drTier(n);
    const lbl = n<0 ? '—' : String(n);
    return `<span class="dr-pill dr-${t}">${lbl}</span>`;
  };

  /* Counts */
  const cntBacklink = rows.filter(r => drNum(r) > 0).length;
  const cntNoBacklink = rows.length - cntBacklink;
  const cntHigh = rows.filter(r => drNum(r) >= 70).length;
  const cntTop = rows.filter(r => drNum(r) >= 90).length;

  const totalMentions = summary['総言及数'] || (rows.length+'件');
  const y2026 = summary['2026年言及数'] || '—';
  const m3 = summary['3月言及数'] || '—';

  /* Hero */
  $(`#${prefix}-title`).innerHTML = `${esc(sheetLabel)} 総言及数 <span class="answer">${esc(totalMentions)}</span><span class="sub-h">— 高DR(70+) ${fmt(cntHigh)}件・最上位(90+) ${fmt(cntTop)}件・被リンクなし(DR=0) ${fmt(cntNoBacklink)}件</span>`;
  $(`#${prefix}-lead`).textContent = `DR（Domain Rating）はahrefsの掲載ドメインの権威スコア(0〜100)。70以上は高権威メディア、90以上は最上位（NHK・日経・Yahoo!ニュース 等）。`;

  $(`#${prefix}-kpis`).innerHTML = [
    kpiBox('総言及数', totalMentions, '', '<div class="delta delta-flat">Excel サマリ</div>', true),
    kpiBox('被リンクあり (DR>0)', fmt(cntBacklink), '件', `<div class="delta delta-flat">${(cntBacklink/Math.max(1,rows.length)*100).toFixed(1)}%</div>`),
    kpiBox('高DR ⭐︎ (70+)', fmt(cntHigh), '件', `<div class="delta delta-flat">${(cntHigh/Math.max(1,rows.length)*100).toFixed(1)}% / うち90+ ${fmt(cntTop)}件</div>`),
    kpiBox('被リンクなし (DR=0)', fmt(cntNoBacklink), '件', `<div class="delta delta-flat">${(cntNoBacklink/Math.max(1,rows.length)*100).toFixed(1)}%</div>`),
  ].join('');

  const tbl = $(`#tbl-${prefix}`);
  const pager = $(`#pager-${prefix}`);
  const searchEl = $(`#${prefix}-search`);
  const countEl = $(`#${prefix}-count`);
  const filterEl = $(`#${prefix}-filter`);

  let filtered = rows.slice();
  let page = 0;
  let drFilter = 'with'; /* default: 被リンクあり */
  const perPage = 100;

  function paint(){
    const start = page*perPage;
    const end = Math.min(start+perPage, filtered.length);
    const slice = filtered.slice(start, end);
    let html = '<tr><th style="width:40px">No.</th><th style="width:100px">Date</th><th>Title</th><th>URL</th><th class="num" style="width:60px">DR</th></tr>';
    slice.forEach(r=>{
      const dom = (r.url.match(/^https?:\/\/([^/]+)/)||[])[1] || '';
      const n = drNum(r);
      const rowCls = n>=90 ? ' class="dr-row-top"' : (n>=70 ? ' class="dr-row-high"' : '');
      html += `<tr${rowCls}>
        <td class="num small">${esc(r.no)}</td>
        <td class="small" style="white-space:nowrap">${esc(r.date)}</td>
        <td>${esc(r.title)}</td>
        <td class="small">${r.url?`<a href="${esc(r.url)}" target="_blank" rel="noopener">${esc(dom||r.url.slice(0,50))}</a>`:''}</td>
        <td class="num">${drPill(r)}</td>
      </tr>`;
    });
    tbl.innerHTML = html;
    countEl.textContent = `表示 ${start+1}〜${Math.min(end,filtered.length)} / ${filtered.length}件（全${rows.length}件中）`;
    const totalPages = Math.max(1, Math.ceil(filtered.length / perPage));
    pager.innerHTML = `
      <button ${page<=0?'disabled':''} data-act="prev">◀ 前へ</button>
      <span>ページ ${page+1} / ${totalPages}</span>
      <button ${page>=totalPages-1?'disabled':''} data-act="next">次へ ▶</button>
    `;
    pager.querySelectorAll('button').forEach(b=>b.addEventListener('click',()=>{
      if(b.dataset.act==='prev') page--; else page++;
      paint();
    }));
  }
  function applyFilter(){
    const q = (searchEl.value||'').trim().toLowerCase();
    let base = rows.slice();
    if(drFilter==='with')   base = base.filter(r => drNum(r) > 0);
    else if(drFilter==='no') base = base.filter(r => drNum(r) <= 0);
    else if(drFilter==='high') base = base.filter(r => drNum(r) >= 70);
    else if(drFilter==='top')  base = base.filter(r => drNum(r) >= 90);
    filtered = !q ? base : base.filter(r => (r.title+' '+r.url).toLowerCase().includes(q));
    page = 0;
    paint();
  }
  function setupFilter(){
    if(!filterEl) return;
    filterEl.innerHTML = `
      <button class="dr-tab is-active" data-f="with">被リンクあり (${fmt(cntBacklink)})</button>
      <button class="dr-tab" data-f="high">高DR 70+ (${fmt(cntHigh)})</button>
      <button class="dr-tab" data-f="top">最上位 90+ (${fmt(cntTop)})</button>
      <button class="dr-tab" data-f="no">被リンクなし (${fmt(cntNoBacklink)})</button>
      <button class="dr-tab" data-f="all">全件 (${fmt(rows.length)})</button>
    `;
    filterEl.querySelectorAll('.dr-tab').forEach(b=>{
      b.addEventListener('click', ()=>{
        filterEl.querySelectorAll('.dr-tab').forEach(x=>x.classList.remove('is-active'));
        b.classList.add('is-active');
        drFilter = b.dataset.f;
        applyFilter();
      });
    });
  }
  setupFilter();
  searchEl.addEventListener('input', applyFilter);
  applyFilter();
}
renderCitation('cit-ideatech', 'citation_ideatech', 'IDEATECH');
renderCitation('cit-risapy', 'citation_risapy', 'リサピー');

/* =========================================================== */
/* ★ Diff tab — week-over-week changes                         */
/* =========================================================== */
function renderDiff(){
  const D = (DATA && DATA.diff) || null;
  const N = n => (n==null||Number.isNaN(n)) ? '—' : Number(n).toLocaleString('ja-JP');
  const sgn = n => n==null ? '' : (n>0?'+':n<0?'':'±');
  const fmtPct = p => p==null ? '—' : (p>=0?'+':'') + (p*100).toFixed(1) + '%';
  const pill = (delta, pct, opts={}) => {
    if(delta==null && pct==null) return '<span class="diff-pill flat">—</span>';
    const cls = delta>0 ? 'up' : delta<0 ? 'down' : 'flat';
    const dn = delta==null ? '—' : (sgn(delta) + (opts.ratio ? (delta*100).toFixed(2)+'pt' : N(Math.abs(delta))));
    const pn = pct==null ? '' : ` (${fmtPct(pct)})`;
    return `<span class="diff-pill ${cls}">${dn}${pn}</span>`;
  };

  /* As-of date in hero */
  const asof = $('#diff-asof');
  const head = $('#diff-headline');
  if(D && D.generated_at){
    const t = new Date(D.generated_at);
    const fmt = isNaN(t) ? D.generated_at : `${t.getFullYear()}/${String(t.getMonth()+1).padStart(2,'0')}/${String(t.getDate()).padStart(2,'0')} ${String(t.getHours()).padStart(2,'0')}:${String(t.getMinutes()).padStart(2,'0')} JST`;
    if(asof) asof.textContent = ' — 算出: ' + fmt;
  }

  if(!D || !D.has_prev){
    if(head) head.textContent = '— 初回スナップショット（前週データなし）';
    const lead = $('#diff-lead'); if(lead) lead.textContent = '今回が最初のスナップショット取得のため、前週との差分はまだ計算されていません。来週以降の更新から差分が反映されます。';
    const sumEl = $('#diff-summary');
    if(sumEl) sumEl.innerHTML = `<span class="ts-label">概況</span>初回ベースライン取得済み。次回（来週月曜7:00）から週次の流入/CV増分・推奨ステータス変化・新規サイテーションが本タブに集約されます。`;
    /* Fill empty placeholders */
    ['tbl-diff-flow','tbl-diff-flips','tbl-diff-cit'].forEach(id => { const e = $('#'+id); if(e) e.innerHTML = ''; });
    const respList = $('#diff-resp-list'); if(respList) respList.innerHTML = '';
    ['diff-flips-empty','diff-resp-empty','diff-cit-empty'].forEach(id => { const e = $('#'+id); if(e) e.style.display = 'block'; });
    /* KPIs: zeroed */
    const kpi = $('#diff-kpis');
    if(kpi){
      kpi.innerHTML = `
        <div class="kpi"><div class="label">推奨ステータス変化</div><div class="value">0</div><div class="delta">▲↔⚫︎ flip 件数</div></div>
        <div class="kpi"><div class="label">応答内容の差分</div><div class="value">0</div><div class="delta">プロンプト × LLM</div></div>
        <div class="kpi"><div class="label">新規サイテーション</div><div class="value">0</div><div class="delta">IDEATECH + リサピー</div></div>
        <div class="kpi"><div class="label">直近月 流入Δ</div><div class="value">—</div><div class="delta">前週スナップショット比</div></div>
      `;
    }
    return;
  }

  /* ---------- KPI row ---------- */
  const flipsTot = (D.prompts && D.prompts.flips_summary && D.prompts.flips_summary.total) || 0;
  const flipsGain = (D.prompts && D.prompts.flips_summary && D.prompts.flips_summary.gained) || 0;
  const flipsLost = (D.prompts && D.prompts.flips_summary && D.prompts.flips_summary.lost) || 0;
  const respCnt = (D.prompts && D.prompts.response_changes_count) || 0;
  const newCitI = (D.citation_ideatech && D.citation_ideatech.count_new) || 0;
  const newCitR = (D.citation_risapy && D.citation_risapy.count_new) || 0;
  const newCitTot = newCitI + newCitR;
  const flowLatest = D.flow && D.flow.site_total && D.flow.site_total.latest_month;
  const flowDelta = flowLatest && flowLatest.delta;
  const flowPct = flowLatest && flowLatest.pct_change;
  const aiFlowLatest = D.flow && D.flow.ai_total && D.flow.ai_total.latest_month;
  const aiRatioLatest = D.flow && D.flow.ai_ratio && D.flow.ai_ratio.latest_month;
  const cvLatest = D.cv && D.cv.cv_site_total && D.cv.cv_site_total.latest_month;
  const cvDelta = cvLatest && cvLatest.delta;
  const cvAiLatest = D.cv && D.cv.cv_ai_total && D.cv.cv_ai_total.latest_month;

  const kpi = $('#diff-kpis');
  if(kpi){
    kpi.innerHTML = `
      <div class="kpi"><div class="label">推奨ステータス変化</div><div class="value">${flipsTot}</div><div class="delta">獲得 ${flipsGain} / 喪失 ${flipsLost}</div></div>
      <div class="kpi"><div class="label">応答内容の差分</div><div class="value">${respCnt}</div><div class="delta">プロンプト × LLM</div></div>
      <div class="kpi"><div class="label">新規サイテーション</div><div class="value">${newCitTot}</div><div class="delta">IDEATECH ${newCitI} / リサピー ${newCitR}</div></div>
      <div class="kpi ${flowDelta>0?'primary':''}"><div class="label">直近月 サイト流入Δ</div><div class="value">${flowDelta==null?'—':(sgn(flowDelta)+N(Math.abs(flowDelta)))}</div><div class="delta">${flowLatest?esc(flowLatest.month||''):''}${flowPct==null?'':' / '+fmtPct(flowPct)}</div></div>
    `;
  }

  /* ---------- 概況 ---------- */
  const sumEl = $('#diff-summary');
  if(sumEl){
    const parts = [];
    if(flowLatest && flowLatest.current!=null && flowLatest.previous!=null){
      const dirT = (flowLatest.delta||0) > 0 ? '増加' : (flowLatest.delta||0) < 0 ? '減少' : '横ばい';
      parts.push(`直近月 <b>${esc(flowLatest.month||'')}</b> のサイト全体流入は <b>${N(flowLatest.current)}件</b>（前週スナップショット比 ${flowLatest.delta==null?'—':sgn(flowLatest.delta)+N(Math.abs(flowLatest.delta))}件 / ${fmtPct(flowLatest.pct_change)}）で<b>${dirT}</b>`);
    }
    if(aiFlowLatest && (aiFlowLatest.current!=null || aiFlowLatest.previous!=null)){
      const aiDirT = (aiFlowLatest.delta||0) > 0 ? '増加' : (aiFlowLatest.delta||0) < 0 ? '減少' : '横ばい';
      const ratioStr = (aiRatioLatest && aiRatioLatest.current!=null) ? `／AI経由比率 <b>${fmtPct(aiRatioLatest.current)}</b>` : '';
      parts.push(`うちAI経由流入は <b>${N(aiFlowLatest.current||0)}件</b>（${aiFlowLatest.delta==null?'—':sgn(aiFlowLatest.delta)+N(Math.abs(aiFlowLatest.delta))}件 / ${fmtPct(aiFlowLatest.pct_change)}）で<b>${aiDirT}</b>${ratioStr}`);
    }
    if(cvLatest && (cvLatest.current!=null || cvLatest.previous!=null)){
      parts.push(`同月CVは <b>${N(cvLatest.current||0)}件</b>（${cvLatest.delta==null?'—':sgn(cvLatest.delta)+N(Math.abs(cvLatest.delta))}件）`);
    }
    if(cvAiLatest && (cvAiLatest.current!=null || cvAiLatest.previous!=null)){
      parts.push(`うちAI経由CVは <b>${N(cvAiLatest.current||0)}件</b>（${cvAiLatest.delta==null?'—':sgn(cvAiLatest.delta)+N(Math.abs(cvAiLatest.delta))}件）`);
    }
    if(flipsTot > 0){
      parts.push(`推奨ステータスは <b>${flipsTot}件 flip</b>（獲得 ${flipsGain} / 喪失 ${flipsLost}）`);
    } else {
      parts.push(`推奨ステータスの変化は<b>なし</b>`);
    }
    if(newCitTot > 0){
      parts.push(`新規サイテーション <b>${newCitTot}件</b>（IDEATECH ${newCitI} / リサピー ${newCitR}）`);
    } else {
      parts.push(`新規サイテーションは<b>なし</b>`);
    }
    if(respCnt > 0){
      parts.push(`応答内容の差分 <b>${respCnt}ケース</b>を本タブ③に格納`);
    }
    sumEl.innerHTML = `<span class="ts-label">概況</span>${parts.join('。<br>')}。`;
  }

  /* ---------- ① 流入 / CV ---------- */
  const flowTbl = $('#tbl-diff-flow');
  if(flowTbl){
    const groups = [
      {key:'flow', metrics:[
        {k:'site_total', label:'サイト全体流入', ratio:false},
        {k:'organic',    label:'オーガニック流入', ratio:false},
        {k:'ai_total',   label:'AI経由流入',     ratio:false},
        {k:'ai_ratio',   label:'AI経由比率',     ratio:true},
      ]},
      {key:'cv', metrics:[
        {k:'cv_site_total', label:'CV（サイト全体）', ratio:false},
        {k:'cv_organic',    label:'CV（オーガニック）', ratio:false},
        {k:'cv_ai_total',   label:'CV（AI経由）',   ratio:false},
      ]},
    ];
    const buckets = [
      {b:'latest_month', lab:'直近月'},
      {b:'ytd',          lab:'年累計（YTD）'},
      {b:'cumulative',   lab:'全期間累計'},
    ];
    const rows = [];
    groups.forEach(g => {
      g.metrics.forEach(m => {
        const series = (D[g.key]||{})[m.k];
        if(!series) return;
        buckets.forEach((bk, idx) => {
          const v = series[bk.b];
          if(!v) return;
          const cur = m.ratio && v.current!=null ? (v.current*100).toFixed(2)+'%' : N(v.current);
          const prv = m.ratio && v.previous!=null ? (v.previous*100).toFixed(2)+'%' : N(v.previous);
          const lab = bk.b==='ytd' && v.year ? `${bk.lab} (${v.year})` : (bk.b==='latest_month' && v.month ? `${bk.lab} (${v.month})` : bk.lab);
          rows.push(`<tr>
            <td class="col-metric">${idx===0?esc(m.label):''}</td>
            <td class="col-bucket">${esc(lab)}</td>
            <td style="text-align:right">${cur}</td>
            <td style="text-align:right;color:var(--ink2)">${prv}</td>
            <td style="text-align:right">${pill(v.delta, v.pct_change, {ratio:m.ratio})}</td>
          </tr>`);
        });
      });
    });
    flowTbl.innerHTML = `
      <thead><tr>
        <th>指標</th><th>区分</th><th style="text-align:right">今週</th>
        <th style="text-align:right">前週スナップショット</th><th style="text-align:right">差分</th>
      </tr></thead>
      <tbody>${rows.join('')}</tbody>
    `;
  }

  /* ---------- ② 推奨ステータス flip ---------- */
  const flipsTbl = $('#tbl-diff-flips');
  const flipsEmpty = $('#diff-flips-empty');
  const flips = (D.prompts && D.prompts.flips) || [];
  if(flipsTbl){
    if(!flips.length){
      flipsTbl.innerHTML = '';
      if(flipsEmpty) flipsEmpty.style.display = 'block';
    } else {
      if(flipsEmpty) flipsEmpty.style.display = 'none';
      const brandLabel = b => b==='ideatech' ? 'IDEATECH' : (b==='prizma' ? 'PRIZMA' : esc(b));
      const arrow = f => {
        if(f.to==='yes' && f.from==='no') return `<span class="diff-pill gain">${esc(f.from_mark||'▲')} → ${esc(f.to_mark||'⚫︎')}</span>`;
        if(f.to==='no' && f.from==='yes') return `<span class="diff-pill lost">${esc(f.from_mark||'⚫︎')} → ${esc(f.to_mark||'▲')}</span>`;
        return `<span class="diff-pill flat">${esc(f.from_mark||'')} → ${esc(f.to_mark||'')}</span>`;
      };
      const body = flips.slice().sort((a,b)=>{
        /* gains first, then losses, then by no */
        const score = x => (x.to==='yes' && x.from==='no') ? 0 : (x.to==='no' && x.from==='yes') ? 1 : 2;
        return score(a) - score(b) || ((a.no||0)-(b.no||0));
      }).map(f => `
        <tr>
          <td style="text-align:right;font-variant-numeric:tabular-nums">${esc(f.no||'')}</td>
          <td class="col-prompt"><a href="#prompt-${esc(f.no||'')}" class="prompt-link">${esc(f.prompt||'')}</a></td>
          <td>${esc(f.category||'')}</td>
          <td>${brandLabel(f.brand)}</td>
          <td>${esc(f.llm||'')}</td>
          <td>${arrow(f)}</td>
        </tr>
      `).join('');
      flipsTbl.innerHTML = `
        <thead><tr>
          <th style="text-align:right">No.</th><th>プロンプト</th><th>カテゴリ</th>
          <th>ブランド</th><th>LLM</th><th>変化</th>
        </tr></thead>
        <tbody>${body}</tbody>
      `;
    }
  }
  /* Filter toolbar for flips */
  const flipsTool = $('#diff-flips-toolbar');
  if(flipsTool){
    if(!flips.length){ flipsTool.innerHTML = ''; }
    else {
      const cntAll = flips.length;
      const cntGain = flips.filter(f=>f.to==='yes' && f.from==='no').length;
      const cntLost = flips.filter(f=>f.from==='yes' && f.to==='no').length;
      flipsTool.innerHTML = `
        <button class="is-active" data-filter="all">全件 <b>${cntAll}</b></button>
        <button data-filter="gain">獲得 <b>${cntGain}</b></button>
        <button data-filter="lost">喪失 <b>${cntLost}</b></button>
        <button data-filter="ideatech">IDEATECH のみ</button>
        <button data-filter="prizma">PRIZMA のみ</button>
      `;
      flipsTool.querySelectorAll('button').forEach(btn => {
        btn.addEventListener('click', () => {
          flipsTool.querySelectorAll('button').forEach(b=>b.classList.remove('is-active'));
          btn.classList.add('is-active');
          const f = btn.dataset.filter;
          flipsTbl.querySelectorAll('tbody tr').forEach((tr, idx) => {
            const item = flips[idx]; if(!item) return;
            let show = true;
            if(f==='gain') show = item.to==='yes' && item.from==='no';
            else if(f==='lost') show = item.from==='yes' && item.to==='no';
            else if(f==='ideatech') show = item.brand==='ideatech';
            else if(f==='prizma') show = item.brand==='prizma';
            tr.style.display = show ? '' : 'none';
          });
        });
      });
    }
  }

  /* ---------- ③ 応答内容差分 ---------- */
  const respList = $('#diff-resp-list');
  const respEmpty = $('#diff-resp-empty');
  const respTool = $('#diff-resp-toolbar');
  const resps = (D.prompts && D.prompts.response_changes) || [];
  /* Lightweight word-level diff (LCS on whitespace tokens) */
  const tokenize = s => (s||'').split(/(\s+)/);
  const lcsDiff = (a, b) => {
    const A = tokenize(a), B = tokenize(b);
    if(A.length > 800 || B.length > 800){
      /* Too large for full LCS — fallback: prefix/suffix match + diff middle */
      return [{op:'eq', text:''}, {op:'del', text:a}, {op:'add', text:b}];
    }
    const m = A.length, n = B.length;
    const dp = new Array(m+1);
    for(let i=0;i<=m;i++){ dp[i] = new Int16Array(n+1); }
    for(let i=m-1;i>=0;i--){
      for(let j=n-1;j>=0;j--){
        if(A[i]===B[j]) dp[i][j] = dp[i+1][j+1] + 1;
        else dp[i][j] = Math.max(dp[i+1][j], dp[i][j+1]);
      }
    }
    const out = [];
    let i=0, j=0;
    while(i<m && j<n){
      if(A[i]===B[j]){ out.push({op:'eq', text:A[i]}); i++; j++; }
      else if(dp[i+1][j] >= dp[i][j+1]){ out.push({op:'del', text:A[i]}); i++; }
      else { out.push({op:'add', text:B[j]}); j++; }
    }
    while(i<m){ out.push({op:'del', text:A[i++]}); }
    while(j<n){ out.push({op:'add', text:B[j++]}); }
    return out;
  };
  const renderInlineDiff = (prev, cur) => {
    const ops = lcsDiff(prev, cur);
    return ops.map(o => {
      const t = esc(o.text);
      if(o.op==='add') return `<span class="diff-text-add">${t}</span>`;
      if(o.op==='del') return `<span class="diff-text-del">${t}</span>`;
      return t;
    }).join('');
  };
  if(respList){
    if(!resps.length){
      respList.innerHTML = '';
      if(respEmpty) respEmpty.style.display = 'block';
      if(respTool) respTool.innerHTML = '';
    } else {
      if(respEmpty) respEmpty.style.display = 'none';
      const kindLabel = k => k==='new' ? '<span class="diff-pill gain">新規</span>' : k==='removed' ? '<span class="diff-pill lost">削除</span>' : '<span class="diff-pill up">更新</span>';
      const cards = resps.map((r, idx) => {
        const dlt = r.len_delta || 0;
        const dltPill = `<span class="diff-pill ${dlt>0?'up':dlt<0?'down':'flat'}">${sgn(dlt)}${N(Math.abs(dlt))}文字</span>`;
        const inline = (r.kind==='changed') ? renderInlineDiff(r.prev||'', r.cur||'') : null;
        const fullPrev = `<details><summary>前週の応答全文（${N(r.prev_len)}文字${r.prev_truncated?' / 4000文字で切詰':''}）</summary><div class="diff-text-block">${esc(r.prev||'')}</div></details>`;
        const fullCur  = `<details open><summary>今週の応答全文（${N(r.cur_len)}文字${r.cur_truncated?' / 4000文字で切詰':''}）</summary><div class="diff-text-block">${esc(r.cur||'')}</div></details>`;
        const inlineBlock = inline ? `<details open><summary>差分ハイライト（語単位）</summary><div class="diff-text-block">${inline}</div></details>` : '';
        return `
          <div class="diff-resp-card" data-kind="${esc(r.kind||'')}" data-llm="${esc(r.llm||'')}">
            <div class="diff-resp-head">
              <div>
                <span style="font-weight:700">No.${esc(r.no||'')}</span>
                <a href="#prompt-${esc(r.no||'')}" class="prompt-link" style="margin-left:8px;color:var(--blue);text-decoration:none">${esc(r.prompt||'')}</a>
              </div>
              <div class="diff-resp-meta">${esc(r.llm||'')} ${kindLabel(r.kind)} ${dltPill}</div>
            </div>
            <div class="diff-resp-body">
              ${inlineBlock}
              ${fullCur}
              ${fullPrev}
            </div>
          </div>
        `;
      }).join('');
      respList.innerHTML = cards;
      if(respTool){
        const cntAll = resps.length;
        const cntChg = resps.filter(r=>r.kind==='changed').length;
        const cntNew = resps.filter(r=>r.kind==='new').length;
        const cntDel = resps.filter(r=>r.kind==='removed').length;
        const llms = Array.from(new Set(resps.map(r=>r.llm).filter(Boolean)));
        respTool.innerHTML = `
          <button class="is-active" data-filter="all">全件 <b>${cntAll}</b></button>
          <button data-filter="changed">更新 <b>${cntChg}</b></button>
          <button data-filter="new">新規 <b>${cntNew}</b></button>
          <button data-filter="removed">削除 <b>${cntDel}</b></button>
          ${llms.map(l=>`<button data-filter="llm:${esc(l)}">${esc(l)}</button>`).join('')}
        `;
        respTool.querySelectorAll('button').forEach(btn => {
          btn.addEventListener('click', () => {
            respTool.querySelectorAll('button').forEach(b=>b.classList.remove('is-active'));
            btn.classList.add('is-active');
            const f = btn.dataset.filter;
            respList.querySelectorAll('.diff-resp-card').forEach(card => {
              let show = true;
              if(f==='all') show = true;
              else if(f.startsWith('llm:')) show = card.dataset.llm === f.slice(4);
              else show = card.dataset.kind === f;
              card.style.display = show ? '' : 'none';
            });
          });
        });
      }
    }
  }

  /* ---------- ④ 新規サイテーション (IDEATECH / リサピー切替) ---------- */
  const citTbl = $('#tbl-diff-cit');
  const citEmpty = $('#diff-cit-empty');
  const citCntI = $('#diff-cit-cnt-ideatech');
  const citCntR = $('#diff-cit-cnt-risapy');
  const newRowsI = (D.citation_ideatech && D.citation_ideatech.new_rows) || [];
  const newRowsR = (D.citation_risapy && D.citation_risapy.new_rows) || [];
  if(citCntI) citCntI.textContent = newRowsI.length;
  if(citCntR) citCntR.textContent = newRowsR.length;

  const renderCitTable = (rows) => {
    if(!rows || !rows.length){
      if(citEmpty) citEmpty.style.display = 'block';
      if(citTbl) citTbl.innerHTML = '';
      return;
    }
    if(citEmpty) citEmpty.style.display = 'none';
    const dr = r => { const n = parseInt(String(r.dr||'').trim(),10); return Number.isFinite(n) ? n : -1; };
    const drBadge = v => {
      if(v >= 90) return `<span class="diff-pill gain">DR ${v}</span>`;
      if(v >= 70) return `<span class="diff-pill up">DR ${v}</span>`;
      if(v >= 0)  return `<span class="diff-pill flat">DR ${v}</span>`;
      return `<span class="diff-pill flat">DR —</span>`;
    };
    const body = rows.map(r => `
      <tr>
        <td>${drBadge(dr(r))}</td>
        <td>${esc(r.title || r.url || '')}</td>
        <td>${r.url ? `<a href="${esc(r.url)}" target="_blank" rel="noopener" style="color:var(--blue);text-decoration:none">${esc((r.url||'').replace(/^https?:\/\//,'').slice(0,60))}${(r.url||'').length>60?'…':''}</a>` : ''}</td>
        <td style="color:var(--ink2)">${esc(r.first_seen || r.date || r.no || '')}</td>
      </tr>
    `).join('');
    if(citTbl){
      citTbl.innerHTML = `
        <thead><tr>
          <th style="width:90px">DR</th><th>タイトル / メディア</th><th>URL</th><th>取得日</th>
        </tr></thead>
        <tbody>${body}</tbody>
      `;
    }
  };
  /* Default tab: IDEATECH */
  renderCitTable(newRowsI);
  $$('.diff-cit-tab').forEach(btn => {
    btn.addEventListener('click', () => {
      $$('.diff-cit-tab').forEach(b => b.classList.remove('is-active'));
      btn.classList.add('is-active');
      const t = btn.dataset.target;
      renderCitTable(t==='risapy' ? newRowsR : newRowsI);
    });
  });
}
renderDiff();

/* =========================================================== */
/* ⑤ AI Topics                                                 */
/* =========================================================== */
function renderTopics(){
  const T = (DATA.ai_topics && DATA.ai_topics.entries) || [];
  const asofEl = $('#topics-asof');
  if(asofEl && DATA.ai_topics && DATA.ai_topics.generated_at){
    const ts = String(DATA.ai_topics.generated_at).replace('T',' ').slice(0,16);
    asofEl.textContent = ' — 取得 ' + ts;
  }

  const sumEl = $('#topics-summary');
  if(sumEl){
    if(!T.length){
      sumEl.innerHTML = `<span class="ts-label">概況</span>本タブはAnthropic API（Claude + web_search）で週次に主要AIニュースを自動収集します。<br>初回実行までは空欄ですが、来週月曜の自動更新後に反映されます。`;
    } else {
      const byAi = {};
      T.forEach(e => { byAi[e.ai] = (byAi[e.ai]||0) + 1; });
      const aiList = Object.entries(byAi).sort((a,b)=>b[1]-a[1]).map(([k,v])=>`${esc(k)} ${v}件`).join(' / ');
      const dates = T.map(e=>e.date).filter(Boolean).sort();
      const span = dates.length ? `${dates[0]} 〜 ${dates[dates.length-1]}` : '直近';
      sumEl.innerHTML = `<span class="ts-label">概況</span>${T.length}件のAIニュースを表示中（${esc(span)}）。<br>内訳: ${aiList}。`;
    }
  }

  const listEl = $('#topics-list');
  const cntEl = $('#topics-count');
  const emptyEl = $('#topics-empty');
  if(!listEl) return;

  if(!T.length){
    listEl.innerHTML = '';
    if(emptyEl) emptyEl.style.display = '';
    if(cntEl) cntEl.textContent = '';
    return;
  }
  if(emptyEl) emptyEl.style.display = 'none';

  /* Build filter chips */
  const aiSet = [...new Set(T.map(e=>e.ai).filter(Boolean))].sort();
  const tagSet = [...new Set(T.flatMap(e=>e.topic_tags||[]).filter(Boolean))].sort();
  const yearSet = [...new Set(T.map(e=>(e.date||'').slice(0,4)).filter(s=>s.length===4))].sort().reverse();

  const filterYearEl = $('#topics-filter-year');
  const filterAiEl = $('#topics-filter-ai');
  const filterTagEl = $('#topics-filter-tag');
  const state = { year: 'ALL', ai: 'ALL', tag: 'ALL', q: '' };

  function chip(label, active, onClick){
    const b = document.createElement('button');
    b.className = 'dr-tab' + (active ? ' is-active' : '');
    b.textContent = label;
    b.addEventListener('click', onClick);
    return b;
  }

  function renderFilters(){
    if(filterYearEl){
      filterYearEl.innerHTML = '<span class="flbl">年</span>';
      filterYearEl.appendChild(chip('全て', state.year==='ALL', ()=>{state.year='ALL'; renderFilters(); apply();}));
      yearSet.forEach(y => filterYearEl.appendChild(chip(y, state.year===y, ()=>{state.year=y; renderFilters(); apply();})));
      filterYearEl.style.display = (yearSet.length >= 2) ? '' : 'none';
    }
    if(filterAiEl){
      filterAiEl.innerHTML = '<span class="flbl">AI</span>';
      filterAiEl.appendChild(chip('全て', state.ai==='ALL', ()=>{state.ai='ALL'; renderFilters(); apply();}));
      aiSet.forEach(a => filterAiEl.appendChild(chip(a, state.ai===a, ()=>{state.ai=a; renderFilters(); apply();})));
    }
    if(filterTagEl){
      filterTagEl.innerHTML = '<span class="flbl">トピック</span>';
      filterTagEl.appendChild(chip('全て', state.tag==='ALL', ()=>{state.tag='ALL'; renderFilters(); apply();}));
      tagSet.forEach(t => filterTagEl.appendChild(chip(t, state.tag===t, ()=>{state.tag=t; renderFilters(); apply();})));
    }
  }

  function escAttr(v){ return String(v||'').replace(/[&<>"']/g, c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c])); }

  function aiBadgeClass(ai){
    const safe = String(ai||'').replace(/[^A-Za-z]/g,'');
    return safe ? ('ai-' + safe) : '';
  }

  function hostOf(u){
    try { return new URL(u).hostname.replace(/^www\./,''); } catch { return ''; }
  }

  function cardHtml(e){
    const ai = esc(e.ai || 'その他');
    const tags = (e.topic_tags||[]).map(t=>`<span class="tc-tag">${esc(t)}</span>`).join('');
    const reactions = e.reactions || {};
    const rSum = reactions.summary || '';
    const rSrc = (reactions.sources||[]);
    const rLinks = rSrc.map(s => `<a href="${escAttr(s.url)}" target="_blank" rel="noopener">${esc(s.label||hostOf(s.url)||'link')} ↗</a>`).join('');
    const reactionsBlock = (rSum || rLinks)
      ? `<div class="tc-reactions"><div class="tc-r-h">世間の反応</div>${rSum?`<div class="tc-r-s">${esc(rSum)}</div>`:''}${rLinks?`<div class="tc-r-l">${rLinks}</div>`:''}</div>`
      : '';
    const host = hostOf(e.url);
    const dateStr = esc(e.date || '');
    const titleHtml = e.url
      ? `<a href="${escAttr(e.url)}" target="_blank" rel="noopener">${esc(e.title||'')}</a>`
      : esc(e.title||'');
    return `
      <div class="topic-card">
        <div class="tc-meta">
          <span class="tc-date">${dateStr}</span>
          <span class="tc-ai ${aiBadgeClass(e.ai)}">${ai}</span>
          ${tags}
        </div>
        <div class="tc-title">${titleHtml}</div>
        ${e.summary?`<div class="tc-summary">${esc(e.summary)}</div>`:''}
        ${host?`<div class="tc-source"><a href="${escAttr(e.url)}" target="_blank" rel="noopener">${esc(host)} ↗</a></div>`:''}
        ${reactionsBlock}
      </div>
    `;
  }

  function apply(){
    const q = (state.q||'').trim().toLowerCase();
    let rows = T.slice();
    if(state.year !== 'ALL') rows = rows.filter(e => (e.date||'').startsWith(state.year));
    if(state.ai !== 'ALL') rows = rows.filter(e => e.ai === state.ai);
    if(state.tag !== 'ALL') rows = rows.filter(e => (e.topic_tags||[]).includes(state.tag));
    if(q){
      rows = rows.filter(e => {
        const blob = [e.title, e.summary, (e.reactions||{}).summary, e.ai, ...(e.topic_tags||[])].join(' ').toLowerCase();
        return blob.includes(q);
      });
    }
    if(cntEl) cntEl.textContent = `${rows.length} / ${T.length} 件`;
    if(!rows.length){
      listEl.innerHTML = '<div class="topics-empty-search">該当するニュースはありません。フィルタや検索条件を見直してください。</div>';
      return;
    }
    listEl.innerHTML = rows.map(cardHtml).join('');
  }

  const searchEl = $('#topics-search');
  if(searchEl){
    searchEl.addEventListener('input', ()=>{ state.q = searchEl.value; apply(); });
  }
  renderFilters();
  apply();
}
renderTopics();

/* =========================================================== */
/* Tab summaries — interpretive callouts based on actual data  */
/* =========================================================== */
function renderTabSummaries(){
  const wrap = (label, html) => `<span class="ts-label">${label}</span>${html}`;
  const num = n => `<span class="hl-num">${(typeof n==='number'?n.toLocaleString('ja-JP'):n)}</span>`;
  const yesMarks = ['⚫︎','●','◉'];

  /* ---------- ① diag ---------- */
  try {
    const diag = DATA.diag || [];
    if(diag.length){
      const overall = diag.reduce((a,r)=>a+(r.score||0),0)/diag.length;
      const byCat = {};
      diag.forEach(r=>{
        if(!byCat[r.group]) byCat[r.group] = [];
        byCat[r.group].push(r.score||0);
      });
      const catAvg = Object.fromEntries(Object.entries(byCat).map(([k,v])=>[k, v.reduce((a,b)=>a+b,0)/v.length]));
      const groupNames = {'A':'技術基盤','B':'コンテンツ網羅性','C':'コンテンツ品質','D':'外部評価'};
      const sortedCats = Object.entries(catAvg).sort((a,b)=>a[1]-b[1]);
      const lowestCat = sortedCats[0]; /* lowest avg */
      const top5 = diag.filter(r=>(r.score||0)>=5).length;
      const low = diag.filter(r=>(r.score||0)<=2).sort((a,b)=>(a.score||0)-(b.score||0));
      const lowItems = low.length ? low.map(r=>`<b>「${esc(r.item||'')}」(${r.score}点)</b>`).join('・') : 'なし';
      const otherCats = sortedCats.slice(1).filter(([_,v])=>v>=4.5).map(([k,_])=>`カテゴリ${k}（${groupNames[k]||''}）`).join('・');
      const html = `総合スコア ${num(overall.toFixed(2))} / 5.0、20項目中 ${num(top5)}項目が満点。${otherCats?otherCats+'は高水準で':''}<b>カテゴリ${lowestCat[0]}（${groupNames[lowestCat[0]]||''}）が${lowestCat[1].toFixed(1)}点</b>と最も低く、特に ${lowItems} が改善余地。技術・品質・外部評価は LLMO 最適化済みで、<b>第三者言及型の網羅性強化（Wikipedia・外部ナレッジソース）</b>が次の打ち手。`;
      const el = $('#diag-summary'); if(el) el.innerHTML = wrap('概況', html);
    }
  } catch(e){ console.warn('diag-summary err', e); }

  /* ---------- ② flow-ss ---------- */
  try {
    const flow = DATA.flow || {};
    const months = flow.months || [];
    const aiTot = (flow.series||{}).ai_total || [];
    const aiRatio = (flow.series||{}).ai_ratio || [];
    const yearSum = yr => aiTot.reduce((s,v,i)=>s+((months[i]||'').startsWith(yr)&&v!=null?v:0),0);
    const yearN = yr => aiTot.reduce((s,v,i)=>s+((months[i]||'').startsWith(yr)&&v!=null?1:0),0);
    const y24 = yearSum('2024'), y25 = yearSum('2025'), y26 = yearSum('2026');
    const n26 = yearN('2026');
    const ratio2425 = y24>0 ? (y25/y24).toFixed(1) : '—';
    /* per-LLM totals */
    const llmTotals = [];
    (flow.flow_groups||[]).forEach(g => (g.llms||[]).forEach(l => {
      const t = (l.data||[]).reduce((s,v)=>s+(v||0),0);
      if(t>0) llmTotals.push({name:l.name, total:t});
    }));
    llmTotals.sort((a,b)=>b.total-a.total);
    const top2 = llmTotals.slice(0,2).map(l=>`<b>${esc(l.name)} 累計${num(l.total)}件</b>`).join('・');
    /* latest non-null month */
    let lastIdx=-1;
    for(let i=aiTot.length-1;i>=0;i--){ if(aiTot[i]!=null){lastIdx=i;break;} }
    const lastM = lastIdx>=0 ? months[lastIdx] : '—';
    const lastV = lastIdx>=0 ? aiTot[lastIdx] : 0;
    const lastR = lastIdx>=0 && aiRatio[lastIdx]!=null ? (aiRatio[lastIdx]*100).toFixed(2)+'%' : '—';
    const html = `AI経由流入は <b>2024年${num(y24)}件 → 2025年${num(y25)}件（約${ratio2425}倍）</b>と急拡大。直近 ${esc(lastM||'')} は ${num(lastV)}件・AI比率 ${num(lastR)}と当月分のため低めで推移。LLM別では ${top2 || '—'} が中心で、<b>SNS型・専門分野型LLMからの流入はほぼゼロ</b>のため、新興LLMへの露出拡大が次の伸びしろ。`;
    const el = $('#flow-ss-summary'); if(el) el.innerHTML = wrap('概況', html);
  } catch(e){ console.warn('flow-ss-summary err', e); }

  /* ---------- ② flow-cv ---------- */
  try {
    const flow = DATA.flow || {};
    const months = flow.months || [];
    const cvSite = flow.cv_site_total || [];
    const cvAi = flow.cv_ai_total || [];
    const sumYr = (arr, yr) => arr.reduce((s,v,i)=>s+((months[i]||'').startsWith(yr)&&v!=null?v:0),0);
    const s24 = sumYr(cvSite,'2024'), s25 = sumYr(cvSite,'2025'), s26 = sumYr(cvSite,'2026');
    const a24 = sumYr(cvAi,'2024'), a25 = sumYr(cvAi,'2025'), a26 = sumYr(cvAi,'2026');
    const ratio = s24>0 ? (s25/s24).toFixed(1) : '—';
    /* AI CV per LLM */
    const llmCv = [];
    (flow.cv_groups||[]).forEach(g => (g.llms||[]).forEach(l => {
      const t = (l.data||[]).reduce((s,v)=>s+(v||0),0);
      if(t>0) llmCv.push({name:l.name, total:t});
    }));
    llmCv.sort((a,b)=>b.total-a.total);
    const topLLMCv = llmCv.length ? llmCv.slice(0,2).map(l=>`<b>${esc(l.name)} 累計${num(l.total)}件</b>`).join('・') : '—';
    const aiCvTot = a24+a25+a26;
    const html = `サイト全体CVは <b>2024年 ${num(s24)}件 → 2025年 ${num(s25)}件（約${ratio}倍）</b>と順調に成長、2026年は4ヶ月で${num(s26)}件のペース。一方 <b>AI経由CVは累計わずか${num(aiCvTot)}件</b>（2024:${num(a24)} / 2025:${num(a25)} / 2026:${num(a26)}）。AI経由CVは ${topLLMCv} が中心で、<b>AI流入の量は伸びているが CV化率はまだ低い</b>のが課題。直近の対策はAI経由訪問者の動線最適化。`;
    const el = $('#flow-cv-summary'); if(el) el.innerHTML = wrap('概況', html);
  } catch(e){ console.warn('flow-cv-summary err', e); }

  /* ---------- ③ prompts-matrix ---------- */
  try {
    const P = DATA.prompts || {};
    const rows = P.rows || [];
    const llms = P.llms || [];
    const ideAny = rows.filter(r => (r.ideatech||[]).some(x=>yesMarks.includes(x))).length;
    const przAny = rows.filter(r => (r.prizma||[]).some(x=>yesMarks.includes(x))).length;
    const perLLMIde = llms.map((l,i)=>({l, c: rows.filter(r=>yesMarks.includes((r.ideatech||[])[i])).length}));
    const perLLMPrz = llms.map((l,i)=>({l, c: rows.filter(r=>yesMarks.includes((r.prizma||[])[i])).length}));
    perLLMIde.sort((a,b)=>b.c-a.c);
    perLLMPrz.sort((a,b)=>b.c-a.c);
    const bestIde = perLLMIde[0], worstIde = perLLMIde[perLLMIde.length-1];
    const topPrz = perLLMPrz[0];
    const total = rows.length;
    const html = `40プロンプト中 <b>IDEATECH／リサピーは${num(ideAny)}件（${(ideAny/total*100).toFixed(0)}%）</b>で言及あり。一方競合 <b>PRIZMAは${num(przAny)}件（${(przAny/total*100).toFixed(0)}%）</b>のみで優位性は明確。LLM別では <b>${esc(bestIde.l)} が${num(bestIde.c)}件（${(bestIde.c/total*100).toFixed(0)}%）と最もヒット率が高く</b>、${esc(worstIde.l)} は${num(worstIde.c)}件（${(worstIde.c/total*100).toFixed(0)}%）と最低。PRIZMA は ${esc(topPrz.l)} で${num(topPrz.c)}件最多のため、<b>${esc(topPrz.l)} 向けの差別化発信</b>が次の打ち手。`;
    const el = $('#matrix-summary'); if(el) el.innerHTML = wrap('概況', html);
  } catch(e){ console.warn('matrix-summary err', e); }

  /* ---------- ③ prompts ---------- */
  try {
    const P = DATA.prompts || {};
    const rows = P.rows || [];
    const llms = P.llms || [];
    let ideTotal=0, przTotal=0;
    rows.forEach(r => {
      ideTotal += (r.ideatech||[]).filter(x=>yesMarks.includes(x)).length;
      przTotal += (r.prizma||[]).filter(x=>yesMarks.includes(x)).length;
    });
    const maxCells = rows.length * llms.length;
    const html = `40プロンプト × 4LLM = ${num(maxCells)}回答中、<b>IDEATECH／リサピー言及は計 ${num(ideTotal)}回（${(ideTotal/maxCells*100).toFixed(0)}%）</b>に対し、<b>競合 PRIZMA は${num(przTotal)}回（${(przTotal/maxCells*100).toFixed(0)}%）</b>と差は ${(ideTotal/Math.max(1,przTotal)).toFixed(1)}倍。応答内のブランド言及は <mark class="hl-brand">黄色</mark>／<mark class="hl-competitor">紫色</mark> でハイライトされるため、推奨文脈の質（ポジティブ／中立／比較対象）を素早く目視確認できます。`;
    const el = $('#prompts-summary'); if(el) el.innerHTML = wrap('概況', html);
  } catch(e){ console.warn('prompts-summary err', e); }

  /* ---------- ④ citations ---------- */
  function citSum(prefix, dataKey, label, compareTo){
    try {
      const C = DATA[dataKey] || {};
      const rows = C.rows || [];
      const drNum = r => { const n = parseInt(String(r.dr||'').trim(),10); return Number.isFinite(n) ? n : -1; };
      const total = rows.length;
      const withBL = rows.filter(r => drNum(r) > 0).length;
      const noBL = total - withBL;
      const high = rows.filter(r => drNum(r) >= 70).length;
      const top = rows.filter(r => drNum(r) >= 90).length;
      const y2026 = (C.summary||{})['2026年言及数'] || '—';
      const m3 = (C.summary||{})['3月言及数'] || '—';
      let compareTxt = '';
      if(compareTo && DATA[compareTo]){
        const ct = (DATA[compareTo].rows||[]).length;
        if(ct>0 && total>0){
          const ratio = total>=ct ? (total/ct).toFixed(1)+'倍' : '1/'+(ct/total).toFixed(1);
          compareTxt = `（${compareTo==='citation_ideatech'?'IDEATECH':'リサピー'}比 約${ratio}）`;
        }
      }
      const html = `サイテーション総数 <b>${num(total)}件</b>${compareTxt}。被リンクあり (DR>0) が <b>${num(withBL)}件（${(withBL/total*100).toFixed(1)}%）</b>とほぼ全て ahrefs にインデックスされた信頼性の高いメディア。<b>高DR70+ ${num(high)}件（${(high/total*100).toFixed(1)}%）、最上位90+ ${num(top)}件（${(top/total*100).toFixed(1)}%）</b>と権威性が高水準。2026年は ${esc(y2026)} の新規言及で、<b>${label}は${total>=1000?'圧倒的な物量':total>=300?'安定したメディア露出':'露出量にまだ伸びしろ'}</b>。`;
      const el = $(`#${prefix}-summary`); if(el) el.innerHTML = wrap('概況', html);
    } catch(e){ console.warn(prefix+'-summary err', e); }
  }
  citSum('cit-ideatech', 'citation_ideatech', 'IDEATECH', 'citation_risapy');
  citSum('cit-risapy', 'citation_risapy', 'リサピー', 'citation_ideatech');
}
renderTabSummaries();
</script>
</body>
</html>
"""

OUT = os.path.abspath(_ARGS.out)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
final = HTML.replace('__DATA_PLACEHOLDER__', DATA_JSON)
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(final)
print(f'Wrote {OUT} ({os.path.getsize(OUT)/1024:.1f} KB)')
