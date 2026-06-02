---
name: resolve_handle
track: core
kind: local_formatter
requires_env: []
inputs: [display_name]
outputs: [display_name, screenname, found]
side_effect: false
---

# resolve_handle

Maps a well-known display name (e.g. "Sam Altman") to a Twitter/X `screenname` using a built-in dictionary.
Use when the user asks for a handle explicitly, or before `timeline` if you only have a person's name and need the handle.
