# Day 04 Lab v2 Report — Research Agent

## Team

- Team: (điền tên nhóm)
- Members: (điền thành viên)
- Provider/model: `openrouter` / `openai/gpt-4o-mini` (hoặc model bạn dùng khi chạy eval)

## Final Metrics

> Điền sau khi chạy `./scripts/run_all_versions.sh` — lấy số từ `summary` trong file `runs/*.json` mới nhất.

- Final version: v3
- Final artifact_version: (từ run JSON)
- Best base run file: `runs/<run_id>_v3_*.json`
- Base case accuracy:
- Base tool routing accuracy:
- Base argument accuracy:
- Group eval run file: `runs/<run_id>_v3-group_*.json`
- Group eval accuracy:
- Chat transcript file: `transcripts/*.transcript.json`

## Version Evidence

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | `artifacts/prompts/v0_baseline_system_prompt.md` | Baseline cố ý đoán bừa | — | (điền) | `runs/*_v0_*.json` |
| v1 | `artifacts/prompts/v1_system_prompt.md` | clarify + no_tool | (v0) | (điền) | `runs/*_v1_*.json` |
| v2 | v1 + `artifacts/tools.yaml` routing | đúng tool/args | (v1) | (điền) | `runs/*_v2_*.json` |
| v3 | `artifacts/system_prompt.md` (final) | parallel + multiturn + send | (v2) | (điền) | `runs/*_v3_*.json` |

## Failure Analysis

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R10_missing_handle | missing_info | timeline + guess | Đoán handle thay vì clarify | v1: rule clarify khi thiếu handle |
| R12_confirm_before_send | wrong_boundary | send | Gửi không xác nhận | v1/v3: clarify yes_no trước send |
| R01_user_tweets_routing | wrong_tool | social_search | Nhầm timeline | v2: bảng routing + map sama |

## Team Eval Cases

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_resolve_handle_sam | Mapping tên → handle | resolve_handle | (điền sau run group) |
| G02_karpathy_timeline_limit | karpathy + limit 3 | timeline | |
| G06_multiturn_handle_then_timeline | Multiturn → timeline sama | timeline limit=2 | |

## Live Chat Evidence

Chạy: `python chat.py --provider openrouter --version v3`

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | Tin AI hôm nay + tweet về AI | lookup + social_search | v3 parallel rule | (điền) |
| 2 | Tóm tắt 5 tweet (thiếu handle) → bổ sung Elon | clarify → timeline | v1 clarify | |
| 3 | Đăng Telegram | clarify yes_no | v3 send boundary | |

## Custom Tool

- **resolve_handle** (`tools/resolve_handle/`): map tên hiển thị phổ biến → Twitter handle (local, không cần API key).

## Reflection

- **system_prompt.md**: clarify, out-of-scope, multiturn, parallel, send boundary, name→handle mapping.
- **tools.yaml**: mô tả rõ phạm vi từng tool (timeline vs social_search, lookup news/timeframe, send confirmed).
- **Manual review**: case có nhiều tool song song — eval không kiểm thứ tự, chỉ kiểm đủ tên/args.
- **Tiếp theo**: nạp credit OpenRouter + keys Tavily/Firecrawl/RapidAPI để tool live chạy trong chat.

## Lưu ý chạy eval

1. Nạp credit OpenRouter hoặc dùng provider còn quota.
2. Bổ sung `TAVILY_API_KEY`, `FIRECRAWL_API_KEY`, `RAPIDAPI_KEY` trong `.env` (xem `TOOL-SETUP.md`).
3. `cd starter_v0 && source .venv/bin/activate && ./scripts/run_all_versions.sh openrouter`
