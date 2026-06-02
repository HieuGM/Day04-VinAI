---
name: github_search
track: bonus
kind: live_api
provider: GitHub REST API
requires_env: []
inputs: [query, search_type, max_results, sort]
outputs: [items]
side_effect: false
---
# github_search

Searches GitHub repositories, issues, or users with the public GitHub Search
API. `GITHUB_TOKEN` is optional and only improves rate limits.
