# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

`news_to_html.py` fetches rows from the `bs_news_sentiment` Supabase table and renders each row as a standalone `docs/{id}/index.html` file.

## Running

`run.sh`는 `nix-shell`을 통해 실행합니다. 서버에 Nix만 설치되어 있으면 됩니다.

```bash
# 전체 생성
./run.sh

# 특정 ID만
./run.sh 123

# 출력 디렉토리 지정
./run.sh -o ./custom-dir
```

nix-shell 없이 직접 실행:
```bash
python3 news_to_html.py [id] [-o 출력디렉토리]
```

## 서버 배포

Oracle Linux 서버에 Nix 설치 (최초 1회):
```bash
curl -L https://nixos.org/nix/install | sh
```

파일 복사:
```bash
scp shell.nix requirements.txt news_to_html.py run.sh .env opc@<서버IP>:~/mknews/
ssh opc@<서버IP> "chmod +x ~/mknews/run.sh"
```

서버에서 실행:
```bash
cd ~/mknews && ./run.sh
```

첫 실행 시 `.venv/`가 자동 생성되고 `requirements.txt` 패키지가 설치됩니다. 이후 실행부터는 기존 venv를 재사용합니다.

## Environment

Credentials are loaded from `.env` via `python-dotenv`. Required keys:
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

## Table: bs_news_sentiment

Key columns: `id`, `title`, `summary`, `news_content`, `sentiment` (긍정/부정/중립), `strength` (0–10), `score`, `reason`, `sector`, `sector_code`, `theme_code`, `uncertainty`, `impact_horizon`, `source_url`, `author`, `published_at`, `relatedsectors` (jsonb), `relatedstocks` (jsonb), `hashtags` (jsonb), `created_at`.

## Architecture

All logic lives in `news_to_html.py`:

- `fetch_all(client, id)` — paginates with 1000-row pages; if `id` given, fetches single row
- `build_html(row)` — renders a full self-contained HTML page from a row dict; CSS is inlined
- `write_news(row, output_dir)` — creates `{output_dir}/{id}/index.html`
- `main()` — argparse entry point; orchestrates fetch → build → write

Sentiment color theming (`긍정` green, `부정` red, `중립` amber) is driven by `SENTIMENT_CONFIG` at the top of the file. The HTML is Python 3.9-compatible — use `Optional[X]` instead of `X | None`.
