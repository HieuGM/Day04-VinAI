---
name: post_reaction_analysis
track: group
kind: local_analyzer
provider: local
requires_env: []
inputs: [post_text, url, platform, likes, comments, shares, reposts, quotes, views, bookmarks]
outputs: [metrics, interpretation, recommendations]
side_effect: false
---
# post_reaction_analysis

Analyzes a social post from its reaction metrics. Use this when the user gives
or asks to analyze likes, comments, shares/reposts, quotes, views, or bookmarks.

The tool does not fetch reactions by itself. If required metrics are missing,
the agent should ask for them or combine this tool with another tool that
already returned post metrics.
