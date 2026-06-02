---
name: timeline
track: core
kind: live_api
provider: RapidAPI Twitter API45 + Nitter RSS fallback
requires_env: [RAPIDAPI_KEY, RAPIDAPI_TWITTER_HOST]
inputs: [screenname, limit]
outputs: [items]
side_effect: false
---
# timeline

Fetches recent posts from a single account. `screenname` is an account handle
without `@`.

The tool first tries RapidAPI `twitter-api45`. If RapidAPI is not subscribed or
rate-limited, it falls back to `NITTER_BASE_URL/<screenname>/rss` with default
`NITTER_BASE_URL=https://nitter.net`.
