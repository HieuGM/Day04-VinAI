---
name: rss_read
track: bonus
kind: live_api
provider: RSS/Atom feed
requires_env: []
inputs: [feed_url, max_items]
outputs: [items]
side_effect: false
---
# rss_read

Reads RSS or Atom feeds and returns recent entries. Requires an explicit feed
URL.
