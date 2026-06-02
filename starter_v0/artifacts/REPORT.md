# Day 04 Lab v2 Report - Research Agent

## Team

- Team: 1 - Zone 9
- Members: 
  - Phạm Duy Thái
  - Nguyễn Thành Vinh
  - Giáp Minh Hiếu
- Provider/model: OpenRouter / `openai/gpt-4o-mini`
- Final version: `v7`
- Final artifact_version: `v7+pd196a96b3700+tde3933158338`

---

# PHAN A - Gioi thieu agent

## A1. Agent nay lam duoc gi

Research agent nay dung de tim tin web/news, social/X, doc URL, tim paper, format digest, tra cuu policy, va gui ket qua sang Telegram/Discord/email sau khi nguoi dung xac nhan.

Link dung thu local:

```text
http://localhost:8501
```

## A2. Tool agent co

| Ten tool | Lam duoc gi | Tool moi nhom them? |
|---|---|---|
| clarify | Hoi lai khi thieu thong tin hoac can xac nhan action | khong |
| timeline | Lay post/tweet moi tu mot account cu the | khong |
| social_search | Tim post/tweet ve mot chu de | khong |
| lookup | Tim web/news live | khong |
| fetch | Doc/tom tat URL cu the | khong |
| format | Format item co san thanh digest/markdown | khong |
| send | Gui Telegram sau xac nhan | khong |
| policy | Tim trong company policy local | khong |
| papers | Tim arXiv papers | khong |
| paper_text | Doc text/PDF arXiv | khong |
| query_expand | Tao search query variants | co |
| github_search | Tim repo/issue/user tren GitHub | co |
| hn_search | Tim story/comment tren Hacker News | co |
| wikipedia_summary | Lay summary Wikipedia | co |
| rss_read | Doc RSS/Atom feed | co |
| discord_send | Gui Discord webhook sau xac nhan | co |
| email_send | Gui email qua Resend sau xac nhan | co |

## A3. Cau hoi mau de thu

1. `Tin AI hom nay co gi noi bat?`
2. `Tweet moi nhat cua Sam Altman la gi?`
3. `Format cac item co san nay thanh markdown bullets: 1) OpenAI ra mat model moi - https://openai.com 2) GitHub co repo agent moi - https://github.com`
4. `Tim tren GitHub cac repository ve streamlit dashboard`
5. `Tim tin AI moi nhat hom nay, tao ban tin ngan va gui toi your@email.com voi subject AI News.`

---

# PHAN B - Chi tiet / Bang chung

## Final Metrics

- Best base run file: `runs/v7_B_base_openrouter_20260602T161256459841.json`
- Base case accuracy: `1.00` (`20/20`)
- Base tool routing accuracy: `1.00`
- Base argument accuracy: `1.00`
- Base multiturn accuracy: `1.00`
- Group eval run file: `runs/v7_B_group_openrouter_20260602T161109493711.json`
- Group eval accuracy: `1.00` (`17/17`)
- Group provider errors: `0`

## B1. Version Evidence

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Weak starter artifacts expose missing-info, side-effect, out-of-scope, and multi-tool failures. |  | 0.70 | `runs/v0_B_base_openrouter_20260602T123918516739.json` |
| v1 | `artifacts/system_prompt.md` | Boundary and routing rules in the prompt should stop guessing, unsafe sends, and out-of-scope tool calls. | 0.70 | 0.95 | `runs/v1_B_base_openrouter_20260602T124128753966.json` |
| v2 | `artifacts/tools.yaml` | Better tool descriptions should prevent extra social search after switching to web. | 0.95 | 0.90 | `runs/v2_B_base_openrouter_20260602T124352352111.json` |
| v3 | prompt, tools, `query_expand`, group cases | Required clarify args plus explicit correction/cancellation rules should restore base and support query planning. | 0.90 | 1.00 | `runs/v3_B_base_openrouter_20260602T125316877277.json` |
| v4 | prompt, tools, UI default | Explicit final-state rules should prevent old account/topic calls after corrections. | 1.00 | 1.00 | `runs/v4_B_base_openrouter_20260602T144054711764.json` |
| v5 | six external/public tools, prompt, group cases | New GitHub/HN/Wikipedia/RSS/Discord tools should expand demos while preserving routing accuracy. | 1.00 | 1.00 | `runs/v5_B_base_openrouter_20260602T151636559527.json` |
| v6 | timeline fallback, format eval, remove Slack | Timeline fallback and format coverage should improve demo reliability while preserving eval accuracy. | 1.00 | 1.00 | `runs/v6_B_base_openrouter_20260602T154425159362.json` |
| v7 | Resend email tool, prompt/tools, provider token cap, group case | Email delivery should be available after confirmation without unsafe sends, while lower `max_tokens` avoids OpenRouter 402 errors. | 1.00 | 1.00 | `runs/v7_B_base_openrouter_20260602T161256459841.json` |

## B2. Failure Analysis

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R08 | out_of_scope | `send` | Baseline treated a math answer as something to send. | Added out-of-scope no-tool rule. |
| R10 | missing_info | `timeline(screenname=sama)` | Baseline guessed Sam Altman when account was missing. | Added no-guessing rule and `clarify(response_type=text)`. |
| R11 | missing_info | `fetch(url=https://example.com/article)` | Baseline invented a URL. | Added explicit URL requirement. |
| R12 | wrong_boundary | `send(text=...)` or `clarify(response_type=text)` | Agent did not ask yes/no confirmation before a send/post action. | Added confirmation-boundary priority for Telegram/Discord/post actions. |
| M06 | wrong_tool | `lookup` + extra `social_search` | Agent kept Twitter after user switched to web. | Added latest-turn cancellation/correction rules. |
| GM01 | wrong_arg_value | `lookup(query=AI)` | Group run kept old topic after "chuyen sang robotics". | Added final-state topic correction rule. |
| GM02 | wrong_arg_value | `timeline(sama)` + extra `timeline(elonmusk)` | Group run called both old and corrected accounts. | Added exactly-one final-account timeline rule. |
| Group v7 first run | provider_error | none | OpenRouter requested default `max_tokens=16384`, exceeding remaining credit. | Added provider max token cap default `2048`. |

## B3. Team Eval Cases

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
| G06 | GitHub repo search | `github_search(search_type=repositories)` | PASS |
| G07 | Hacker News story search | `hn_search(search_type=story)` | PASS |
| G08 | Wikipedia background summary | `wikipedia_summary(...)` | PASS |
| G09 | RSS feed reader | `rss_read(feed_url=..., max_items=3)` | PASS |
| GM07 | Discord send after confirmation | `discord_send(confirmed=true)` | PASS |
| G10 | Format existing items | `format(template=bullets)` | PASS |
| G11 | Email requires confirmation | `clarify(response_type=yes_no)` before `email_send` | PASS |

## B4. Live Chat Evidence

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | Tin AI hom nay | `lookup(query=AI, topic=news, timeframe=day)` | `transcripts/v3_openrouter_20260602T125639801095.transcript.json` | Returned cited news digest. |
| 2 | Tom tat bai viet nay | `clarify(response_type=text)` | same | Asked for URL instead of guessing. |
| 3 | Provided OpenAI URL | `fetch(url=https://openai.com/index/hello-gpt-4o/)` | same | Summarized fetched article. |
| 4 | Dang ban tin len Telegram | `clarify(response_type=yes_no)` | same | Asked for confirmation. |
| 5 | OK, xac nhan gui | `send(confirmed=true)` | same | Correct action boundary; delivery depends on env. |

## B5. Bonus Evidence

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) | `runs/v7_B_group_openrouter_20260602T161109493711.json` | Agent routes Telegram send only after confirmation. | Real delivery needs `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`; eval can be run with action env disabled to avoid sending. |
| Discord | `tools/discord_send`, group eval GM07 | Webhook action tool requires confirmation before sending. | Real delivery needs `DISCORD_WEBHOOK_URL`. |
| Resend email | `tools/email_send`, group eval G11 | Email action tool is declared, implemented, visible in UI env checks, and refuses to send before confirmation. | Real delivery needs `RESEND_API`, `RESEND_FROM`, recipient, subject, body, and explicit confirmation. |
| GitHub/HN/Wikipedia/RSS | `tools/*/TOOL.md`, group eval G06-G09 | Public API tools route correctly and return structured items. | External services can rate-limit or reject malformed requests. |
| arXiv/company policy | `tools.yaml`, tool folders | Tools are declared and implemented from starter bonus track. | Not exercised in final group eval. |
| UI | `ui_streamlit.py` | Streamlit chat UI uses the same prompt/tools, shows calls/results, and writes transcripts. | Uses confirmation guardrail for Telegram, Discord, and Resend email. |

## B6. Reflection

- `system_prompt.md` was the right place for global boundaries: no guessing, no unsafe send, out-of-scope no-tool behavior, and final-state multi-turn correction/cancellation.
- `tools.yaml` was the right place for tool-specific routing descriptions and required argument nudges, especially `clarify.response_type`, action `confirmed`, and `email_send` fields.
- Manual review was needed for provider errors: the first v7 group run failed because of OpenRouter credit/max-token configuration, not because of routing.
- Next improvement: add extension eval coverage for `policy`, `papers`, and `paper_text`, plus a non-sending mock mode for action tools.
