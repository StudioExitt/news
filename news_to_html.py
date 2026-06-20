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
    config = SENTIMENT_CONFIG.get(sentiment, DEFAULT_SENTIMENT)
    title = row.get("title") or "제목 없음"
    summary = row.get("summary") or ""
    news_content = row.get("news_content") or ""
    reason = row.get("reason") or ""
    source_url = row.get("source_url") or ""
    author = row.get("author") or ""
    published_at = row.get("published_at") or row.get("published") or ""
    sector = row.get("sector") or ""
    sector_code = row.get("sector_code") or ""
    theme_code = row.get("theme_code") or ""
    uncertainty = row.get("uncertainty") or ""
    impact_horizon = row.get("impact_horizon") or ""
    strength = row.get("strength")
    score = row.get("score")
    hashtags = row.get("hashtags")
    related_sectors = row.get("relatedsectors")
    related_stocks_data = row.get("relatedstocks")
    created_at = row.get("created_at") or ""
    news_id = row.get("id")

    sector_display = f"{sector}" + (f" <code>{sector_code}</code>" if sector_code else "")
    theme_display = theme_code or '<span class="empty">—</span>'

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
      background: #f1f5f9;
      color: #1e293b;
      line-height: 1.6;
      padding: 2rem 1rem;
    }}
    .container {{ max-width: 800px; margin: 0 auto; }}
    .card {{
      background: #fff;
      border-radius: 16px;
      box-shadow: 0 1px 3px rgba(0,0,0,.08), 0 8px 24px rgba(0,0,0,.06);
      overflow: hidden;
      margin-bottom: 1rem;
    }}
    .header {{
      background: {config["bg"]};
      border-bottom: 2px solid {config["border"]};
      padding: 1.5rem 1.75rem;
    }}
    .header-meta {{
      display: flex;
      align-items: center;
      gap: .75rem;
      margin-bottom: .75rem;
      flex-wrap: wrap;
    }}
    .more-btn {{
      margin-left: auto;
      display: inline-flex;
      align-items: center;
      gap: .3rem;
      background: #fff;
      color: {config["color"]};
      border: 1.5px solid {config["color"]};
      font-size: .78rem;
      font-weight: 700;
      padding: .25rem .75rem;
      border-radius: 999px;
      text-decoration: none;
      white-space: nowrap;
    }}
    .more-btn:hover {{ background: {config["bg"]}; }}
    .sentiment-badge {{
      display: inline-flex;
      align-items: center;
      gap: .35rem;
      background: {config["color"]};
      color: #fff;
      font-size: .8rem;
      font-weight: 700;
      padding: .25rem .75rem;
      border-radius: 999px;
    }}
    .score-badge {{
      color: #fff;
      font-size: .8rem;
      font-weight: 700;
      padding: .25rem .6rem;
      border-radius: 999px;
    }}
    .meta-text {{ font-size: .8rem; color: #64748b; }}
    h1 {{
      font-size: 1.35rem;
      font-weight: 700;
      color: #0f172a;
      line-height: 1.4;
    }}
    .body {{ padding: 1.5rem 1.75rem; }}
    .section {{ margin-bottom: 1.5rem; }}
    .section:last-child {{ margin-bottom: 0; }}
    .section-label {{
      font-size: .7rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: .08em;
      color: #94a3b8;
      margin-bottom: .5rem;
    }}
    .section-content {{ font-size: .95rem; color: #334155; }}
    .news-content {{
      font-size: .9rem;
      color: #475569;
      white-space: pre-wrap;
      background: #f8fafc;
      border-radius: 8px;
      padding: 1rem;
      border: 1px solid #e2e8f0;
    }}
    .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }}
    .grid-3 {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; }}
    .info-box {{
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 10px;
      padding: .9rem 1rem;
    }}
    .info-box .section-label {{ margin-bottom: .3rem; }}
    .info-value {{ font-size: .95rem; font-weight: 600; color: #1e293b; }}
    .strength-bar {{
      display: flex;
      gap: 3px;
      margin-top: .3rem;
    }}
    .strength-bar span {{
      flex: 1;
      height: 8px;
      border-radius: 2px;
    }}
    .tag {{
      display: inline-block;
      font-size: .78rem;
      font-weight: 500;
      padding: .2rem .55rem;
      border-radius: 6px;
      border: 1px solid transparent;
      margin: .15rem .1rem;
    }}
    .stock-tag {{
      background: #eff6ff;
      color: #1d4ed8;
      border-color: #bfdbfe;
    }}
    .empty {{ color: #cbd5e1; font-size: .9rem; }}
    .divider {{
      border: none;
      border-top: 1px solid #f1f5f9;
      margin: 1.25rem 0;
    }}
    code {{
      background: #f1f5f9;
      padding: .1rem .35rem;
      border-radius: 4px;
      font-size: .82rem;
      color: #64748b;
    }}
    .footer {{
      text-align: center;
      font-size: .75rem;
      color: #94a3b8;
      padding: 1rem;
    }}
    @media (max-width: 600px) {{
      .grid-2, .grid-3 {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
<div class="container">

  <div class="card">
    <div class="header">
      <div class="header-meta">
        <span class="sentiment-badge">{config["icon"]} {sentiment or "미분류"}</span>
        {score_badge(score)}
        <span class="meta-text">ID #{news_id}</span>
        {"<span class='meta-text'>·</span><span class='meta-text'>" + published_at + "</span>" if published_at else ""}
        {"<span class='meta-text'>·</span><span class='meta-text'>" + author + "</span>" if author else ""}
        <a class="more-btn" href="https://studioexitt.net/news/{news_id}" target="_blank" rel="noopener">More ↗</a>
      </div>
      <h1>{title}</h1>
    </div>

    <div class="body">

      {"<div class='section'><div class='section-label'>요약</div><div class='section-content'>" + summary + "</div></div><hr class='divider'>" if summary else ""}

      <div class="grid-3" style="margin-bottom:1.25rem">
        <div class="info-box">
          <div class="section-label">감성 강도</div>
          <div class="info-value">{strength if strength is not None else "—"} / 10</div>
          {strength_bar(strength, sentiment)}
        </div>
        <div class="info-box">
          <div class="section-label">불확실성</div>
          <div class="info-value">{uncertainty or "—"}</div>
        </div>
        <div class="info-box">
          <div class="section-label">영향 시계</div>
          <div class="info-value">{impact_horizon or "—"}</div>
        </div>
      </div>

      <div class="grid-2" style="margin-bottom:1.25rem">
        <div class="info-box">
          <div class="section-label">섹터</div>
          <div class="info-value">{sector_display or "—"}</div>
        </div>
        <div class="info-box">
          <div class="section-label">테마 코드</div>
          <div class="info-value">{theme_display}</div>
        </div>
      </div>

      {"<div class='section'><div class='section-label'>감성 분석 근거</div><div class='section-content'>" + reason + "</div></div><hr class='divider'>" if reason else ""}

      <div class="section">
        <div class="section-label">관련 섹터</div>
        <div class="section-content">{tag_list(related_sectors, "#0891b2")}</div>
      </div>

      <div class="section">
        <div class="section-label">관련 종목</div>
        <div class="section-content">{related_stocks(related_stocks_data)}</div>
      </div>

      <div class="section">
        <div class="section-label">해시태그</div>
        <div class="section-content">{tag_list(hashtags, "#7c3aed")}</div>
      </div>

      <hr class="divider">

      <div class="section">
        <div class="section-label">뉴스 원문</div>
        <div class="news-content">{news_content}</div>
      </div>

    </div>
  </div>

  <div class="footer">
    {"출처: <a href='" + source_url + "' target='_blank' rel='noopener' style='color:#94a3b8;text-decoration:underline;'>" + source_url + "</a> &nbsp;|&nbsp;" if source_url else ""}
    자료제공: AI 및 알고리즘에 의한 본 자료는 스튜디오엑싯에 의해 제공되었습니다. <a href="https://studioexitt.net" target="_blank" rel="noopener" style="color:#3b82f6;text-decoration:underline;">https://studioexitt.net</a>
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
