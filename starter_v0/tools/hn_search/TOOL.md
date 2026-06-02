---
name: hn_search
track: bonus
kind: live_api
provider: Hacker News Algolia API
requires_env: []
inputs: [query, search_type, max_results]
outputs: [items]
side_effect: false
---
# hn_search

Searches Hacker News stories or comments through Algolia's public HN API.
