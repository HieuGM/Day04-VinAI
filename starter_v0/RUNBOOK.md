# Runbook — Day 04 Research Agent

## 1. Thu muc lam viec

Chay tat ca lenh ben duoi tu thu muc `starter_v0`:

```powershell
cd C:\Users\Laptop\OneDrive\Laptop\WorkSpace\VinAI\Session\Day04-C401-Prompt-Engineering-Tool-Calling-Labs-student\starter_v0
```

## 2. Moi truong Python

Repo da co `.venv`. Neu can active:

```powershell
.\.venv\Scripts\Activate.ps1
```

Hoac chay truc tiep bang Python trong venv:

```powershell
.\.venv\Scripts\python.exe --version
```

Neu can cai lai dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Ghi chu Windows/OneDrive: `streamlit` da duoc pin `1.38.0` vi ban moi hon co duong dan package rat dai va co the loi khi cai trong thu muc OneDrive.

## 3. File `.env`

Khong nop `.env`. File nay chi dung local.

Can co cac bien chinh:

```env
OPENROUTER_API_KEY=...
TAVILY_API_KEY=...
FIRECRAWL_API_KEY=...
RAPIDAPI_KEY=...
RAPIDAPI_TWITTER_HOST=twitter-api45.p.rapidapi.com
```

Telegram send can them:

```env
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

Ban da dien `TELEGRAM_BOT_TOKEN`. Hien tai may dang thieu `TELEGRAM_CHAT_ID`, nen agent se goi `send(confirmed=true)` dung guardrail nhung tool se bao loi thieu chat id.

Neu da dien ca hai bien nhung van khong send duoc:

- `getMe ok=True`: token dung.
- `Bad Request: chat not found`: `TELEGRAM_CHAT_ID` sai hoac bot chua truy cap duoc chat do.
- Neu gui direct message cho bot: mo Telegram, tim bot, bam Start hoac gui `/start`, sau do lay lai chat id.
- Neu gui vao group: add bot vao group, gui mot message trong group, sau do lay chat id cua group. Group id thuong la so am.
- Neu gui vao channel: add bot lam admin co quyen post. Public channel co the dung `@channel_username`; private channel thuong can id dang `-100...`.
- Sau khi sua `.env`, restart Streamlit/CLI process vi app da load env luc khoi dong.

Voi Telegram channel:

- Bot phai duoc add vao channel/group.
- Bot can quyen gui message.
- Public channel co the dung `TELEGRAM_CHAT_ID=@ten_channel`.
- Private channel/group thuong can numeric chat id.

## 4. Kiem tra provider

```powershell
.\.venv\Scripts\python.exe scripts\preflight_provider.py --provider openrouter
```

Ky vong:

```text
OK provider=openrouter model=openai/gpt-4o-mini
tool=timeline
args={'screenname': 'sama', 'limit': 1}
```

## 5. Chay eval final

Base eval:

```powershell
.\.venv\Scripts\python.exe run_eval.py --provider openrouter --version v4 --suite base --eval-cases data\eval_base.json
```

Group eval:

```powershell
.\.venv\Scripts\python.exe run_eval.py --provider openrouter --version v4 --suite group --eval-cases data\eval_group.json
```

Ket qua final da chay:

- Base: `runs/v4_B_base_openrouter_20260602T144054711764.json`, accuracy `1.00`
- Group: `runs/v4_B_group_openrouter_20260602T143928975056.json`, accuracy `1.00`

Moi lan chay se tao file moi trong `runs/`.

## 6. Parse run logs thanh CSV

```powershell
.\.venv\Scripts\python.exe scripts\parse_runs.py runs --output analysis\runs.csv
```

CSV da co san:

```text
analysis/runs.csv
```

## 7. Chay chat CLI

```powershell
.\.venv\Scripts\python.exe chat.py --provider openrouter --version v4
```

Thu 3 nhom case:

```text
Tin AI hom nay co gi noi bat?
```

```text
Tom tat bai viet nay ho minh
```

Sau khi agent hoi URL, nhap:

```text
https://openai.com/index/hello-gpt-4o/
```

Telegram confirmation:

```text
Dang ban tin nay len Telegram: Ban tin AI da san sang.
```

Sau khi agent hoi xac nhan:

```text
OK, toi xac nhan gui
```

Transcript se nam trong:

```text
transcripts/*.transcript.json
```

## 8. Chay Streamlit UI

Chay:

```powershell
.\.venv\Scripts\python.exe -m streamlit run ui_streamlit.py --server.headless true --server.port 8501
```

Mo trinh duyet:

```text
http://localhost:8501
```

UI se:

- Dung cung `artifacts/system_prompt.md` va `artifacts/tools.yaml`.
- Goi tool that qua provider/tools.
- Hien tool calls/tool results trong expander.
- Ghi transcript vao `transcripts/`.
- Hien trang thai env var o sidebar.
- Co nut `Confirm`/`Cancel` khi agent dang cho xac nhan yes/no.

Neu port `8501` bi dung, doi port:

```powershell
.\.venv\Scripts\python.exe -m streamlit run ui_streamlit.py --server.headless true --server.port 8502
```

## 9. Cac file quan trong da lam

Prompt/tooldesc:

- `artifacts/system_prompt.md`
- `artifacts/tools.yaml`
- `artifacts/version_log.csv`
- `artifacts/REPORT.md`

Tool moi:

- `tools/query_expand/TOOL.md`
- `tools/query_expand/tool.py`
- `tools/__init__.py`

Eval/report:

- `data/eval_group.json`
- `runs/*.json`
- `analysis/runs.csv`
- `transcripts/*.transcript.json`

UI:

- `ui_streamlit.py`
- `requirements.txt`

## 10. Goi y nop bai

Nen nop ca thu muc `starter_v0/`, tru:

- Khong nop `.env`
- Khong nop `.venv`
- Khong nop API keys

Neu nen clean truoc khi zip, giu lai:

- `artifacts/`
- `data/`
- `tools/`
- `runs/`
- `analysis/`
- `transcripts/`
- `ui_streamlit.py`
- source Python chinh cua starter
