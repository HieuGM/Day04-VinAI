---
name: discord_send
track: bonus
kind: action
provider: Discord webhook
requires_env: [DISCORD_WEBHOOK_URL]
inputs: [text, username, confirmed]
outputs: [status]
side_effect: true
requires_confirmation: true
---
# discord_send

Sends a message to a Discord channel through an incoming webhook. This is an
action tool and must only be called after explicit user confirmation.
