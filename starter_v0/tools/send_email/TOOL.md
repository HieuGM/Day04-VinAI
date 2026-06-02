---
name: send_email
track: bonus
kind: action
provider: Resend
requires_env: [RESEND_API_KEY, RESEND_FROM]
inputs: [to_email, subject, text, items, confirmed]
outputs: [status, to, email_id]
side_effect: true
requires_confirmation: true
---
# send_email

Gửi tin tức AI (hoặc digest đã soạn) tới email người dùng qua Resend. Chỉ gửi khi `confirmed=true` sau khi user xác nhận và đã cung cấp địa chỉ Gmail.
