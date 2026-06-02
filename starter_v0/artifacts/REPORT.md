# Day 04 Lab v2 Report — Research Agent

## Team

- Team: Student workspace, Codex-assisted
- Members: User + Codex
- Provider/model: OpenRouter / `openai/gpt-4o-mini`

## Final Metrics

- Final version: `v4`
- Final artifact_version: `v4+p81948fcb9d2e+td7ade8db87e5`
- Best base run file: `runs/v4_B_base_openrouter_20260602T144054711764.json`
- Base case accuracy: `1.00`
- Base tool routing accuracy: `1.00`
- Base argument accuracy: `1.00`
- Base multiturn accuracy: `1.00`
- Group eval run file: `runs/v4_B_group_openrouter_20260602T143928975056.json`
- Group eval accuracy: `1.00`
- Chat transcript files:
  - `transcripts/v3_openrouter_20260602T125639801095.transcript.json`
  - `transcripts/v3_openrouter_20260602T125747848452.transcript.json`

## Version Evidence

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Weak starter artifacts expose missing-info, side-effect, out-of-scope, and multi-tool failures. |  | 0.70 | `runs/v0_B_base_openrouter_20260602T123918516739.json` |
| v1 | `artifacts/system_prompt.md` | Boundary and routing rules in the prompt should stop guessing, unsafe sends, and out-of-scope tool calls. | 0.70 | 0.95 | `runs/v1_B_base_openrouter_20260602T124128753966.json` |
| v2 | `artifacts/tools.yaml` | Better tool descriptions should prevent extra social search after switching to web. | 0.95 | 0.90 | `runs/v2_B_base_openrouter_20260602T124352352111.json` |
| v3 | prompt, tools, `query_expand`, group cases | Required clarify args plus explicit correction/cancellation rules should restore base and support the new query-planning tool. | 0.90 | 1.00 | `runs/v3_B_base_openrouter_20260602T125316877277.json` |
| v4 | prompt, tools, UI default | Explicit final-state rules should prevent old account/topic calls after corrections. | 1.00 | 1.00 | `runs/v4_B_base_openrouter_20260602T144054711764.json` |

## Failure Analysis

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R08 | out_of_scope | `send` | Baseline treated math answer as something to send. | Added out-of-scope no-tool rule. |
| R10 | missing_info | `timeline(screenname=sama)` | Baseline guessed Sam Altman when account was missing. | Added no-guessing rule and `clarify(response_type=text)`. |
| R11 | missing_info | `fetch(url=https://example.com/article)` | Baseline invented a URL. | Added explicit URL requirement and required `response_type`. |
| R12 | wrong_boundary | `send(text=...)` | Baseline sent before confirmation. | Added confirmation-before-send rule and `confirmed=true` schema. |
| M06 | wrong_tool | `lookup` + extra `social_search` | Agent kept Twitter after user said switch to web. | Added latest-turn cancellation/correction rules. |
| GM01 | wrong_arg_value | `lookup(query=AI)` | A later group run kept the old topic after "chuyen sang robotics". | Added final-state topic correction rule. |
| GM02 | wrong_arg_value | `timeline(sama)` + extra `timeline(elonmusk)` | A later group run called both old and corrected accounts. | Added exactly-one final-account timeline rule. |

## Team Eval Cases

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01 | Social top search with limit | `social_search(query=OpenAI, search_type=Top, limit=7)` | PASS |
| G02 | Monthly news timeframe | `lookup(query=robotics, topic=news, timeframe=month)` | PASS |
| G03 | Explicit URL reading | `fetch(url=...)` | PASS |
| G04 | Missing URL | `clarify(response_type=text)` | PASS |
| G05 | New `query_expand` tool | `query_expand(topic=AI agents, intent=news, language=vi, max_variants=4)` | PASS |
| GM01 | Multi-turn topic/time carryover | `lookup(query=robotics, topic=news, timeframe=day)` | PASS |
| GM02 | Multi-turn account correction | `timeline(screenname=sama, limit=2)` | PASS |
| GM03 | Send after confirmation | `send(confirmed=true)` | PASS |
| GM04 | Multi-turn social top/limit | `social_search(query=GPT-5, search_type=Top, limit=3)` | PASS |
| GM05 | Multi-turn `query_expand` args | `query_expand(..., intent=news, language=vi, max_variants=5)` | PASS |

## Live Chat Evidence

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | Tin AI hôm nay | `lookup(query=AI, topic=news, timeframe=day)` | `v3+pede98d896041+t3f4d372d91e5` | Returned cited news digest. |
| 2 | Tóm tắt bài viết này | `clarify(response_type=text)` | same | Asked for URL instead of guessing. |
| 3 | Provided OpenAI URL | `fetch(url=https://openai.com/index/hello-gpt-4o/)` | same | Summarized fetched article. |
| 4 | Đăng bản tin lên Telegram | `clarify(response_type=yes_no)` | same | Asked for confirmation. |
| 5 | OK, xác nhận gửi | `send(confirmed=true)` | same | Correctly attempted send; tool returned missing Telegram env vars. |

## Bonus Evidence

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) | `transcripts/v3_openrouter_20260602T125639801095.transcript.json` | Agent asked confirmation before `send` and set `confirmed=true` only after user confirmed. | Actual delivery needs `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`; absent env vars produced a safe error. |
| arXiv/company policy | `tools.yaml`, tool folders | Tools are declared and implemented from starter bonus track. | Not exercised in final report run. |
| UI | `ui_streamlit.py` | Streamlit chat UI uses the same prompt/tools, shows tool calls/results, and writes transcripts. | Uses the same send confirmation guardrail; real Telegram delivery still needs `TELEGRAM_CHAT_ID`. |

## Reflection

- `system_prompt.md` was the right place for global boundaries: no guessing, no unsafe send, out-of-scope no-tool behavior, and final-state multi-turn correction/cancellation.
- `tools.yaml` was the right place for tool-specific routing descriptions and required argument nudges, especially `clarify.response_type` and `send.confirmed`.
- The group `query_expand` case needed manual review because translating the topic to Vietnamese was reasonable once the user asked for Vietnamese query variants.
- Next improvement: add extension eval coverage for `policy`, `papers`, and `paper_text`.
