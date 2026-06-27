# Slack Skill

Automate Slack via CDP. All operations use a single Python helper script.

## Prerequisites
- Slack open in Chrome (logged in)
- CDP enabled on port 9222

## Quick Commands

**Helper script:** `skills/slack_helper.py`

```bash
HELPER="/Users/chethankumar/Library/Application Support/copperriver/agent22/skills/slack_helper.py"

# Send a DM to someone (finds them + navigates + sends — all in one)
python3 "$HELPER" dm "Name" "Your message here"

# Send a message to the currently open conversation
python3 "$HELPER" send "Your message here"

# Find a person/channel in sidebar
python3 "$HELPER" find "search term"

# Navigate to a channel or DM by name
python3 "$HELPER" navigate "channel-or-person-name"

# Read last N messages (default 5)
python3 "$HELPER" read 10

# Show current conversation info
python3 "$HELPER" status
```

## Typical Workflows

### "Tell X to do Y" → One command
```bash
python3 "$HELPER" dm "Sangeetha Subramanyam" "Please cancel tomorrow's AIops training session."
```

### Check recent messages
```bash
python3 "$HELPER" read 5
```

### Navigate somewhere and send
```bash
python3 "$HELPER" navigate "ops-team"
python3 "$HELPER" send "Deploying in 10 minutes"
```

## Architecture

The helper (`slack_helper.py`) connects directly to Slack's Chrome tab via CDP WebSocket:
- Auto-discovers the Slack tab from `/json/list`
- Evaluates JS in page context using IIFEs (avoids redeclaration errors)
- Uses `document.execCommand("insertText")` for typing (works with contenteditable)
- Uses `send_button.click()` for sending

## Selectors Reference

| Element | Selector |
|---------|----------|
| Message input | `[data-qa="texty_input"]` |
| Send button | `[data-qa="texty_send_button"]` |
| Message text | `[data-qa="message-text"]` |
| Sidebar items | `[data-qa='virtual-list-item']` |
| Message sender | `[data-qa="message_sender_name"]` |
| Search button | `[data-qa="top_nav_search"]` |

## URL Pattern
```
https://app.slack.com/client/{WORKSPACE_ID}/{CHANNEL_OR_DM_ID}
```
- `D` prefix = DM, `C` = public channel, `G` = private channel/group DM

## Troubleshooting

- **"No Slack tab found"** → Open Slack in Chrome, make sure CDP is running on 9222
- **Session expired** → Slack redirects to workspace-signin. User must sign in manually.
- **"No send button"** → Input might be empty. Verify text was typed with `status`.
