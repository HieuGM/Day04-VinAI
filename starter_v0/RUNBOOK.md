# Runbook — Day 04 Research Agent

## 1. Thu muc lam viec

Chay tat ca lenh ben duoi tu thu muc `starter_v0`:

```powershell
cd C:\Users\Laptop\OneDrive\Laptop\WorkSpace\VinAI\Session\Day04-C401-Prompt-Engineering-Tool-Calling-Labs-student\starter_v0
```

## 2. Moi truong Python

```powershell
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Ghi chu Windows/OneDrive: `streamlit` dang pin `1.38.0` de tranh loi path qua dai khi cai package.

## 3. File `.env`

Khong nop `.env`.

Bien chinh:

```env
OPENROUTER_API_KEY=...
TAVILY_API_KEY=...
FIRECRAWL_API_KEY=...
RAPIDAPI_KEY=...
RAPIDAPI_TWITTER_HOST=twitter-api45.p.rapidapi.com
NITTER_BASE_URL=https://nitter.net
```

`timeline` se thu RapidAPI truoc. Neu RapidAPI bao `not subscribed` hoac `too many requests`, tool fallback sang Nitter RSS.

Action tools:

```env
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
DISCORD_WEBHOOK_URL=...
RESEND_API=...
RESEND_FROM=...
```

Telegram, Discord, va Resend email chi gui that sau khi user xac nhan. Neu sua `.env`, restart Streamlit/CLI vi app load env luc khoi dong.

Optional:

```env
GITHUB_TOKEN=...
```

GitHub token khong bat buoc, chi giup tang rate limit.

## 4. Kiem tra provider

```powershell
.\.venv\Scripts\python.exe scripts\preflight_provider.py --provider openrouter
```

## 5. Chay eval final

```powershell
.\.venv\Scripts\python.exe run_eval.py --provider openrouter --version v7 --suite base --eval-cases data\eval_base.json
.\.venv\Scripts\python.exe run_eval.py --provider openrouter --version v7 --suite group --eval-cases data\eval_group.json
```

Expected final: base `1.00`, group `1.00`.

Latest verified runs:

- Base: `runs/v7_B_base_openrouter_20260602T161256459841.json`
- Group: `runs/v7_B_group_openrouter_20260602T161109493711.json`

De tranh gui Telegram/Discord/email that trong luc eval, chay eval trong process tam thoi khong load action env. Cach don gian: dat `DAY04_ENV_FILE` tro toi file khong ton tai va set lai rieng provider key cho process do.

## 6. Parse run logs thanh CSV

```powershell
.\.venv\Scripts\python.exe scripts\parse_runs.py runs --output analysis\runs.csv
```

## 7. Chay chat CLI

```powershell
.\.venv\Scripts\python.exe chat.py --provider openrouter --version v7
```

Prompt demo:

```text
Tweet moi nhat cua Sam Altman la gi?
```

```text
Tin AI hom nay co gi noi bat?
```

```text
Tom tat bai viet nay ho minh
```

Sau khi agent hoi URL:

```text
https://openai.com/index/hello-gpt-4o/
```

```text
Format cac item co san nay thanh markdown bullets: 1) OpenAI ra mat model moi - https://openai.com 2) GitHub co repo agent moi - https://github.com
```

```text
Tim tren GitHub cac repository ve streamlit dashboard
```

```text
Tim Hacker News stories ve AI agents
```

```text
Lay tom tat Wikipedia ve Transformer neural network
```

```text
Doc 3 muc moi tu RSS feed https://hnrss.org/frontpage
```

```text
Gui vao Discord: Research agent da pass eval.
```

Voi Discord, agent phai hoi xac nhan truoc. Sau khi ban xac nhan, tool se gui that neu `DISCORD_WEBHOOK_URL` da cau hinh.

```text
Tim tin AI moi nhat hom nay, tao ban tin ngan va gui toi your@email.com voi subject AI News.
```

Voi email, agent nen tra cuu tin AI bang `lookup`, chuan bi noi dung, hoi xac nhan `yes_no`, sau do moi goi `email_send` neu ban xac nhan. Tool dung `RESEND_API` va `RESEND_FROM`.

## 8. Chay Streamlit UI

```powershell
.\.venv\Scripts\python.exe -m streamlit run ui_streamlit.py --server.headless true --server.port 8501
```

Mo:

```text
http://localhost:8501
```

UI se hien tool calls/tool results trong expander va ghi transcript vao `transcripts/`.

## 9. File quan trong

Prompt/tooldesc:

- `artifacts/system_prompt.md`
- `artifacts/tools.yaml`
- `artifacts/version_log.csv`
- `artifacts/REPORT.md`

Tool moi:

- `tools/query_expand/`
- `tools/github_search/`
- `tools/hn_search/`
- `tools/wikipedia_summary/`
- `tools/rss_read/`
- `tools/discord_send/`
- `tools/email_send/`
- `tools/__init__.py`

Eval/report:

- `data/eval_group.json`
- `runs/*.json`
- `analysis/runs.csv`
- `transcripts/*.transcript.json`

UI:

- `ui_streamlit.py`
- `requirements.txt`

## 10. Nop bai

Nen nop ca `starter_v0/`, tru:

- Khong nop `.env`
- Khong nop `.venv`
- Khong nop API keys
