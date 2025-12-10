# Exercise 4.6

## Broadcaster

Simple service that uses NATS (https://nats.io / https://github.com/nats-io/nats.py) and Apprise (https://github.com/caronc/apprise) to send messages on changes to the todo
items to selected notification service.

### Architecture

1. The backend sends a message to NATS server with subject 'todo'.
2. The 'todo-broadcaster' subscribes this subject using a queue so that multiple replicas
   can run without duplicating the notification.
3. Broadcaster forwards the messages received from the NAT server using Apprise to the
   configured service (Slack/Telegram/...)

### Configuration

Specify the notifaction service using key APPRISE_URL in secret broadcaster-secret. For
example: https://discord.com/api/webhooks/466749326fwf76BlrQAjJQWKzP_ycy2N78lrr11AtcC 

```
k apply -f ~/.secrets/broadcaster.yaml
```
