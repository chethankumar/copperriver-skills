---
name: notification-watcher
description: "Watch macOS notifications for tracked apps. Uses log stream on usernoted, investigates content using tools, and suggests actions."
version: 1.0.0
category: system
source: copperriver
---

# Notification Watcher

## Architecture (v5 - Log-Only, Zero Screenshots)
1. `log stream` watches `usernoted` for notification deliveries (zero cost when idle)
2. When a tracked app sends a notification → write app + timestamp to queue
3. Cron job (every 2 min) reads queue → agent investigates content using tools
4. Agent opens the source app (browser/AppleScript) to read the actual message/email
5. Suggests action → waits for user confirmation → executes

## Why No Screenshots
macOS suppresses notification banners when screen capture is active (CopperRiver uses ScreenCaptureKit). Screenshots can't catch banners. The log-only approach is 100% reliable and zero disk usage.

## Components
- **Watcher**: `~/Library/Application Support/copperriver/agent22/scripts/notif-watcher-v5.sh`
- **Processor**: `~/Library/Application Support/copperriver/agent22/scripts/notif-processor.sh`
- **Queue**: `~/notif-queue.jsonl` (JSON Lines)
- **Cron**: "Notification Action Agent" (every 2 min)

## Tracked Apps
Slack, Outlook, Teams, Mail, Messages, Calendar, Safari, Chrome
(Skips: CopperRiver self-notifications, Script Editor, system noise)

## Management
```bash
# Start
nohup bash ~/Library/Application\ Support/copperriver/agent22/scripts/notif-watcher-v5.sh > /dev/null 2>&1 &
echo $! > ~/notif-watcher.pid

# Stop
kill $(cat ~/notif-watcher.pid)

# Check queue
cat ~/notif-queue.jsonl
```
