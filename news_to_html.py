#!/usr/bin/env python3
import sys
import json
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

SENTIMENT_CONFIG = {
    "긍정": {"color": "#16a34a", "bg": "#f0fdf4", "border": "#86efac", "icon": "▲"},
    "부정": {"color": "#dc2626", "bg": "#fef2f2", "border": "#fca5a5", "icon": "▼"},
    "중립": {"color": "#d97706", "bg": "#fffbeb", "border": "#fcd34d", "icon": "◆"},
}

DEFAULT_SENTIMENT = {"color": "#6b7280", "bg": "#f9fafb", "border": "#d1d5db", "icon": "●"}


def strength_bar(strength: Optional[int], sentiment: Optional[str]) -> str:
    if strength is None:
        return ""
    config = SENTIMENT_CONFIG.get(sentiment or "", DEFAULT_SENTIMENT)
    filled = max(0, min(10, strength))
    bars = "".join(
        f'<span style="background:{config["color"]};opacity:{0.3 + 0.07*i}"></span>'
        for i in range(filled)
    ) + "".join(
        f'<span style="background:#e5e7eb"></span>'
        for _ in range(10 - filled)
    )
    return f'<div class="strength-bar">{bars}</div>'


def score_badge(score: Optional[int]) -> str:
    if score is None:
        return ""
    color = "#16a34a" if score > 0 else "#dc2626" if score < 0 else "#6b7280"
    sign = "+" if score > 0 else ""
    return f'<span class="score-badge" style="background:{color}">{sign}{score}</span>'


def tag_list(items, color="#3b82f6") -> str:
    if not items:
        return '<span class="empty">—</span>'
    if isinstance(items, str):
        try:
            items = json.loads(items)
        except Exception:
            items = [items]
    return " ".join(
        f'<span class="tag" style="background:{color}20;color:{color};border-color:{color}40">{item}</span>'
        for item in items
    )


def tag_list_hash(items) -> str:
    if not items:
        return '<span class="empty">—</span>'
    if isinstance(items, str):
        try:
            items = json.loads(items)
        except Exception:
            items = [items]
    return " ".join(
        f'<span class="tag tag-hash">{item}</span>'
        for item in items
    )


def related_stocks(stocks) -> str:
    if not stocks:
        return '<span class="empty">—</span>'
    if isinstance(stocks, str):
        try:
            stocks = json.loads(stocks)
        except Exception:
            return '<span class="empty">—</span>'
    items = []
    for s in stocks:
        if isinstance(s, dict):
            name = s.get("name") or s.get("ticker") or str(s)
            ticker = s.get("ticker", "")
            label = f"{name} ({ticker})" if ticker and ticker != name else name
        else:
            label = str(s)
        items.append(f'<span class="tag stock-tag">{label}</span>')
    return " ".join(items) if items else '<span class="empty">—</span>'


def build_html(row: dict) -> str:
    sentiment = row.get("sentiment") or ""
    _key_map = {"positive": "긍정", "negative": "부정", "neutral": "중립"}
    config = SENTIMENT_CONFIG.get(_key_map.get(sentiment.lower(), sentiment), DEFAULT_SENTIMENT)

    title = row.get("title") or "제목 없음"
    summary = row.get("summary") or ""
    news_content = row.get("news_content") or ""
    reason = row.get("reason") or ""
    source_url = row.get("source_url") or ""
    published_at = row.get("published_at") or row.get("published") or ""
    uncertainty = row.get("uncertainty") or ""
    impact_horizon = row.get("impact_horizon") or ""
    strength = row.get("strength")
    hashtags = row.get("hashtags")
    related_sectors = row.get("relatedsectors")
    related_stocks_data = row.get("relatedstocks")
    news_id = row.get("id")

    _display_map = {
        "긍정": "긍정 (Positive)", "부정": "부정 (Negative)", "중립": "중립 (Neutral)",
        "positive": "긍정 (Positive)", "negative": "부정 (Negative)", "neutral": "중립 (Neutral)",
    }
    sentiment_label = _display_map.get(sentiment, sentiment or "미분류")
    s_color = config["color"]
    date_str = published_at[:10] if published_at else "—"
    s_strength = f"{strength} / 10" if strength is not None else "—"

    src_link = (
        "<span style='color:#e2e8f0'>|</span>"
        f"<a class='src-link' href='{source_url}' target='_blank' rel='noopener'>🔗 원문 보기</a>"
    ) if source_url else ""

    summary_block = (
        f'<div class="section">'
        f'<div class="section-title"><span class="dot" style="background:#3b82f6"></span>핵심 요약</div>'
        f'<div class="box" style="background:#eff6ff">{summary}</div>'
        f'</div>'
    ) if summary else ""

    reason_block = (
        f'<div class="section">'
        f'<div class="section-title"><span class="dot" style="background:#16a34a"></span>감성 판단 근거</div>'
        f'<div class="box" style="background:#f0fdf4">{reason}</div>'
        f'</div>'
    ) if reason else ""

    source_row = (
        f"<div class='news-src'>원문링크: "
        f"<a href='{source_url}' style='color:#64748b;word-break:break-all'>{source_url}</a></div>"
    ) if source_url else ""

    news_block = (
        f'<div class="news-wrap">'
        f'<div class="news-toggle" onclick="this.classList.toggle(\'open\');this.nextElementSibling.classList.toggle(\'open\')">'
        f'<span>🗃 뉴스 원문 보기</span><span class="arrow">∧</span></div>'
        f'<div class="news-body open">{news_content}</div>'
        f'{source_row}'
        f'</div>'
    ) if news_content else ""

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Pretendard", "Noto Sans KR", sans-serif;
      background: #f0f2f5;
      color: #1e293b;
      line-height: 1.6;
      padding: 1.5rem 1rem;
    }}
    .container {{ max-width: 640px; margin: 0 auto; }}
    .card {{
      background: #fff;
      border-radius: 12px;
      border: 1px solid #e2e8f0;
      overflow: hidden;
      margin-bottom: 1rem;
    }}
    .header {{
      padding: 1.25rem 1.5rem 1rem;
      border-bottom: 1px solid #f1f5f9;
    }}
    .header-top {{
      display: flex;
      align-items: center;
      gap: .5rem;
      font-size: .78rem;
      color: #94a3b8;
      margin-bottom: .65rem;
      flex-wrap: wrap;
    }}
    .src-link {{
      color: #3b82f6;
      text-decoration: none;
    }}
    .src-link:hover {{ text-decoration: underline; }}
    .more-btn {{
      margin-left: auto;
      color: #3b82f6;
      font-size: .78rem;
      font-weight: 600;
      text-decoration: none;
    }}
    .more-btn:hover {{ text-decoration: underline; }}
    h1 {{
      font-size: 1.35rem;
      font-weight: 700;
      color: #0f172a;
      line-height: 1.45;
    }}
    .info-bar {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      border-bottom: 1px solid #f1f5f9;
    }}
    .info-cell {{
      padding: .8rem .9rem;
      border-right: 1px solid #f1f5f9;
    }}
    .info-cell:last-child {{ border-right: none; }}
    .info-label {{
      font-size: .65rem;
      color: #94a3b8;
      font-weight: 500;
      margin-bottom: .2rem;
    }}
    .info-value {{
      font-size: .88rem;
      font-weight: 700;
      color: #1e293b;
    }}
    .sentiment-value {{ color: {s_color}; }}
    .body {{ padding: 1.25rem 1.5rem; }}
    .section {{ margin-bottom: 1.4rem; }}
    .section-title {{
      display: flex;
      align-items: center;
      gap: .5rem;
      font-size: .92rem;
      font-weight: 700;
      color: #1e293b;
      margin-bottom: .65rem;
    }}
    .dot {{
      width: 16px;
      height: 16px;
      border-radius: 50%;
      display: inline-block;
      flex-shrink: 0;
    }}
    .box {{
      border-radius: 8px;
      padding: .9rem 1rem;
      font-size: .875rem;
      color: #475569;
      line-height: 1.75;
    }}
    .sub-label {{
      font-size: .68rem;
      font-weight: 600;
      color: #94a3b8;
      text-transform: uppercase;
      letter-spacing: .05em;
      margin: .75rem 0 .35rem;
    }}
    .tag {{
      display: inline-block;
      font-size: .75rem;
      font-weight: 500;
      padding: .18rem .6rem;
      border-radius: 6px;
      border: 1px solid #bfdbfe;
      background: #eff6ff;
      color: #1d4ed8;
      margin: .12rem .08rem;
    }}
    .tag-hash {{
      background: #1e293b;
      color: #e2e8f0;
      border-color: #1e293b;
    }}
    .stock-tag {{
      background: #eff6ff;
      color: #1d4ed8;
      border-color: #bfdbfe;
    }}
    .empty {{ color: #cbd5e1; font-size: .875rem; }}
    .news-wrap {{ padding: 0 1.5rem 1.25rem; }}
    .news-toggle {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: #1e293b;
      color: #fff;
      padding: .8rem 1.1rem;
      cursor: pointer;
      user-select: none;
      font-size: .875rem;
      font-weight: 600;
      border-radius: 8px 8px 0 0;
    }}
    .arrow {{
      display: inline-block;
      transition: transform .2s;
    }}
    .news-toggle.open .arrow {{ transform: rotate(180deg); }}
    .news-body {{
      display: none;
      font-size: .85rem;
      color: #475569;
      white-space: pre-wrap;
      background: #f8fafc;
      padding: 1rem 1.1rem;
      border: 1px solid #e2e8f0;
      border-top: none;
      line-height: 1.8;
    }}
    .news-body.open {{ display: block; }}
    .news-src {{
      font-size: .72rem;
      color: #94a3b8;
      padding: .45rem 1.1rem .6rem;
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-top: 1px solid #f1f5f9;
      border-radius: 0 0 8px 8px;
    }}
    .footer {{
      text-align: center;
      font-size: .72rem;
      color: #94a3b8;
      padding: 1rem;
      line-height: 1.7;
    }}
    @media (max-width: 540px) {{
      .info-bar {{ grid-template-columns: repeat(2, 1fr); }}
      .info-cell:nth-child(2) {{ border-right: none; }}
      .info-cell:nth-child(3) {{ border-right: 1px solid #f1f5f9; }}
      h1 {{ font-size: 1.2rem; }}
    }}
  </style>
</head>
<body>
<div class="container">
  <div class="card">

    <div class="header">
      <div class="header-top">
        <span>📅 {date_str}</span>
        {src_link}
        <a class="more-btn" href="https://studioexitt.net/news/{news_id}" target="_blank" rel="noopener">More ↗</a>
      </div>
      <h1>{title}</h1>
    </div>

    <div class="info-bar">
      <div class="info-cell">
        <div class="info-label">↑ AI 감성 분석</div>
        <div class="info-value sentiment-value">{sentiment_label}</div>
      </div>
      <div class="info-cell">
        <div class="info-label">≡ 감성 스코어</div>
        <div class="info-value">{s_strength}</div>
      </div>
      <div class="info-cell">
        <div class="info-label">⏱ 영향력 기간 (HORIZON)</div>
        <div class="info-value">{impact_horizon or "—"}</div>
      </div>
      <div class="info-cell">
        <div class="info-label">⚡ 불확실성 (UNCERTAINTY)</div>
        <div class="info-value">{uncertainty or "—"}</div>
      </div>
    </div>

    <div class="body">
      {summary_block}
      {reason_block}
      <div class="section">
        <div class="section-title">
          <span class="dot" style="background:#f59e0b"></span>
          관련 항목 분석
        </div>
        <div class="sub-label">관련 종목</div>
        <div>{related_stocks(related_stocks_data)}</div>
        <div class="sub-label">관련 섹터</div>
        <div>{tag_list(related_sectors, "#3b82f6")}</div>
        <div class="sub-label">해시태그</div>
        <div>{tag_list_hash(hashtags)}</div>
      </div>
    </div>

    {news_block}

  </div>

  <div class="footer">
    자료제공: AI 및 알고리즘에 의한 본 자료는 스튜디오엑싯에 의해 제공되었습니다.<br>
    <a href="https://studioexitt.net" target="_blank" rel="noopener" style="color:#3b82f6;text-decoration:underline;">https://studioexitt.net</a>
  </div>
</div>
</body>
</html>"""



ID_FILE = Path("id.txt")


def read_processed_ids() -> set:
    if not ID_FILE.exists():
        return set()
    ids = set()
    for line in ID_FILE.read_text().splitlines():
        line = line.strip()
        if line.isdigit():
            ids.add(int(line))
    return ids


def append_processed_id(news_id: int) -> None:
    existing = read_processed_ids()
    if news_id not in existing:
        with ID_FILE.open("a") as f:
            f.write(f"{news_id}\n")


def fetch_recent(client, limit: int = 10) -> list[dict]:
    result = (
        client.table("bs_news_sentiment")
        .select("*")
        .order("id", desc=True)
        .limit(limit)
        .execute()
    )
    return list(reversed(result.data or []))


def fetch_one(client, news_id: int) -> list[dict]:
    result = client.table("bs_news_sentiment").select("*").eq("id", news_id).execute()
    return result.data or []


def write_news(row: dict, output_dir: Path) -> Path:
    news_id = row["id"]
    dest = output_dir / str(news_id)
    dest.mkdir(parents=True, exist_ok=True)
    html_path = dest / "index.html"
    html_path.write_text(build_html(row), encoding="utf-8")
    return html_path


def main():
    import argparse

    parser = argparse.ArgumentParser(description="bs_news_sentiment → {id}/index.html 생성")
    parser.add_argument("id", nargs="?", type=int, help="특정 뉴스 ID (생략 시 최근 10개 중 미처리 항목)")
    parser.add_argument("-o", "--output-dir", default="docs", help="출력 루트 디렉토리 (기본: docs)")
    args = parser.parse_args()

    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    output_dir = Path(args.output_dir)

    if args.id is not None:
        print(f"ID {args.id} 조회 중...")
        rows = fetch_one(client, args.id)
        if not rows:
            print("해당하는 뉴스가 없습니다.")
            sys.exit(1)
        for i, row in enumerate(rows, 1):
            path = write_news(row, output_dir)
            append_processed_id(row["id"])
            print(f"[{i}/{len(rows)}] {path}")
        print(f"\n완료: {len(rows)}개 파일 생성 → {output_dir.resolve()}")
    else:
        processed = read_processed_ids()
        print(f"최근 10개 조회 중... (처리 완료 ID {len(processed)}개 스킵)")
        recent = fetch_recent(client, limit=10)
        rows = [r for r in recent if r["id"] not in processed]
        if not rows:
            print("처리할 새 뉴스가 없습니다.")
            sys.exit(0)
        print(f"처리 대상: {len(rows)}건")
        for i, row in enumerate(rows, 1):
            path = write_news(row, output_dir)
            append_processed_id(row["id"])
            print(f"[{i}/{len(rows)}] {path}")
        print(f"\n완료: {len(rows)}개 파일 생성 → {output_dir.resolve()}")


if __name__ == "__main__":
    main()
