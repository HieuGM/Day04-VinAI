---
name: email_send
track: bonus
kind: action
provider: Resend
requires_env: [RESEND_API, RESEND_FROM]
inputs: [to, subject, text, html, confirmed]
outputs: [status, id]
side_effect: true
requires_confirmation: true
---
# email_send

Sends an email through Resend. This is an action tool and must only be called
after explicit user confirmation. It reads `RESEND_API` and `RESEND_FROM` from
the local environment.
