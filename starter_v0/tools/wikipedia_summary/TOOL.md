---
name: wikipedia_summary
track: bonus
kind: live_api
provider: Wikipedia REST API
requires_env: []
inputs: [query, language, max_chars]
outputs: [items]
side_effect: false
---
# wikipedia_summary

Finds a Wikipedia page and returns its summary extract. Useful for background
research, definitions, entities, and quick context.
