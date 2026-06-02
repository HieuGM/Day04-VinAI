---
name: query_expand
track: bonus
kind: local_formatter
provider: local
requires_env: []
inputs: [topic, intent, language, max_variants]
outputs: [queries, topic, intent, language]
side_effect: false
---
# query_expand

Creates local search-query variants for a research topic. This tool is for
planning searches only; it does not call the web or retrieve results.
