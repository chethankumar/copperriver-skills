---
name: computer-use
description: "Universal macOS desktop automation via cua-driver. Control any native app — click, type, read UI state — entirely in the background without stealing focus or moving the user's cursor. Use when automating Slack, Mail, Finder, or any macOS application."
version: 2.0.0
category: system
source: copperriver
---

# Computer Use (cua-driver)

Drive any native macOS application in the background — no focus steal, no cursor movement, no disruption. Powered by [cua-driver](https://github.com/trycua/cua).

## Setup

```bash
# Check if installed
which cua-driver || echo "NOT INSTALLED"

# Install (macOS)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/trycua/cua/main/libs/cua-driver/scripts/install.sh)"

# Grant permissions (Accessibility + Screen Recording)
cua-driver permissions grant
```

## Core Principles

1. **Snapshot before AND after every action.** Element indices go stale after any state change. Never reuse indices across turns.
2. **Always prefer `element_index` over pixel coordinates.** AX actions are semantic and don't steal focus. Pixels are blind fallback.
3. **Never use `open -a`, `osascript activate`, `cliclick`, or focus-stealing hotkeys (⌘L, ⌘⇧G).** These violate the background contract.
4. **Use `launch_app` to start apps**, never `open`. It has FocusRestoreGuard.
5. **The daemon must be running** for element-indexed workflows.

## Session Lifecycle

```bash
# Start daemon (once per session — required for element_index caching)
cua-driver serve &
sleep 1
cua-driver status  # verify running

# Declare a session (optional but recommended for agent cursor tracking)
cua-driver start_session '{"session":"my-task"}'

# ... do work ...

# Cleanup
cua-driver end_session '{"session":"my-task"}'
cua-driver stop
```

## Canonical Workflow

```bash
# 1. Launch the target app (no focus steal)
cua-driver launch_app '{"bundle_id":"com.apple.finder"}'
# → {"pid":844, "windows":[{"window_id":6123, "title":"Downloads", ...}]}

# 2. Snapshot — read UI state, cache element indices
cua-driver get_window_state '{"pid":844,"window_id":6123}'
# → tree_markdown + elements[] + screenshot

# 3. Act — click/type by element index
cua-driver click '{"pid":844,"window_id":6123,"element_index":14}'

# 4. Verify — snapshot again to confirm
cua-driver get_window_state '{"pid":844,"window_id":6123}'
```

## Finding Your Target

```bash
# List all running apps
cua-driver list_apps '{}'

# List windows for a specific app
cua-driver list_windows '{"pid":844}'

# Find a window by title (use list_windows + grep)
cua-driver list_windows '{}' | python3 -c "
import sys,json
d=json.load(sys.stdin)
for w in d.get('windows',[]):
    print(f'pid={w[\"pid\"]} wid={w[\"window_id\"]} {w[\"app_name\"]}: {w[\"title\"]}')
"

# Launch by bundle_id (preferred) or name
cua-driver launch_app '{"bundle_id":"com.tinyspeck.slackmacgap"}'
cua-driver launch_app '{"name":"Slack"}'
```

## Actions

### Reading State

```bash
# Full window state — AX tree + screenshot (DEFAULT)
cua-driver get_window_state '{"pid":844,"window_id":6123}'

# AX tree only (no screenshot — cheaper, use before clicking)
cua-driver get_window_state '{"pid":844,"window_id":6123,"capture_mode":"ax"}'

# Screenshot only (visual inspection, no tree)
cua-driver get_window_state '{"pid":844,"window_id":6123,"capture_mode":"vision"}'

# Full desktop screenshot
cua-driver get_desktop_state '{}'

# Filter tree for specific elements
cua-driver get_window_state '{"pid":844,"window_id":6123,"query":"download"}'

# Write screenshot to file (instead of base64)
cua-driver get_window_state '{"pid":844,"window_id":6123,"screenshot_out_file":"~/screen.png"}'
```

### Clicking

```bash
# By element index (PREFERRED — semantic, no focus steal)
cua-driver click '{"pid":844,"window_id":6123,"element_index":14}'

# Double click
cua-driver double_click '{"pid":844,"window_id":6123,"element_index":5}'

# Right click
cua-driver right_click '{"pid":844,"window_id":6123,"element_index":5}'

# By pixel coords (FALLBACK — for canvas/webview only)
cua-driver click '{"pid":844,"window_id":6123,"x":450,"y":280}'

# Click with modifier
cua-driver click '{"pid":844,"window_id":6123,"element_index":14,"modifier":["cmd"]}'
```

### Typing

```bash
# Type into focused field
cua-driver type_text '{"pid":844,"text":"Hello world","window_id":6123}'

# Type into a specific field by element index
cua-driver type_text '{"pid":844,"text":"search term","window_id":6123,"element_index":5}'

# Character-by-character (for finicky apps)
cua-driver type_text_chars '{"pid":844,"text":"slow typing","window_id":6123,"delay_ms":50}'

# Set value directly via AX (bypasses keyboard — for minimized windows)
cua-driver set_value '{"pid":844,"window_id":6123,"element_index":5,"value":"Jane Doe"}'
```

### Keyboard

```bash
# Single key
cua-driver press_key '{"pid":844,"key":"return","window_id":6123}'
cua-driver press_key '{"pid":844,"key":"escape","window_id":6123}'

# Hotkey (modifier combo)
cua-driver hotkey '{"pid":844,"keys":["cmd","c"],"window_id":6123}'
cua-driver hotkey '{"pid":844,"keys":["cmd","s"],"window_id":6123}'

# ⚠️ NEVER use these hotkeys — they steal focus:
# ["cmd","l"] — omnibox focus
# ["cmd","shift","g"] — go to folder
# ["cmd","1".."9"] — tab switching
```

### Scrolling

```bash
cua-driver scroll '{"pid":844,"direction":"down","amount":5,"window_id":6123}'
cua-driver scroll '{"pid":844,"direction":"page","by":"page","amount":1,"window_id":6123}'
```

### Drag & Drop

```bash
cua-driver drag '{"pid":844,"from_x":100,"from_y":200,"to_x":300,"to_y":400,"window_id":6123}'
```

### Browser/Electron Apps

For Chromium/Electron apps (Slack, Chrome, VS Code) where AX tree is sparse, use the `page` tool:

```bash
# Read page text (fastest)
cua-driver page '{"action":"get_text","pid":844,"window_id":6123}'

# Query DOM elements
cua-driver page '{"action":"query_dom","pid":844,"window_id":6123,"css_selector":"button","attributes":["class"]}'

# Click a DOM element
cua-driver page '{"action":"click_element","pid":844,"window_id":6123,"selector":"button.submit"}'

# Execute JavaScript
cua-driver page '{"action":"execute_javascript","pid":844,"window_id":6123,"javascript":"document.title"}'
```

### App Management

```bash
# Kill an app (ask user first)
cua-driver kill_app '{"pid":844}'

# Zoom into a region of a window for higher detail
cua-driver zoom '{"window_id":6123,"pid":844,"x1":0,"y1":0,"x2":500,"y2":400}'
```

## Minimized Windows

Actions on minimized windows have limitations:
- `press_key("return")` silently no-ops — use `set_value` or click a button instead
- Use `set_value` to fill fields — it bypasses the keyboard entirely
- Windows still have valid `window_id` even when minimized

## Common Bundle IDs

| App | Bundle ID |
|-----|-----------|
| Slack | `com.tinyspeck.slackmacgap` |
| Finder | `com.apple.finder` |
| Safari | `com.apple.Safari` |
| Chrome | `com.google.Chrome` |
| Mail | `com.apple.mail` |
| Terminal | `com.apple.Terminal` |
| Notes | `com.apple.Notes` |
| Calendar | `com.apple.calendar` |
| Xcode | `com.apple.dt.Xcode` |

Find bundle IDs: `cua-driver list_apps '{}' | python3 -c "import sys,json; [print(f'{a[\"bundle_id\"]}: {a[\"name\"]}') for a in json.load(sys.stdin).get('apps',[])]"`

## Troubleshooting

```bash
# Check daemon status
cua-driver status

# Check permissions
cua-driver permissions status

# Diagnose environment
cua-driver doctor

# List all available tools
cua-driver list-tools

# Get schema for a specific tool
cua-driver describe get_window_state
```

## Navigation via AppleScript + cua-driver

For opening specific views in apps (like switching Slack channels), use AppleScript for navigation then cua-driver for interaction:

```bash
# Navigate via AppleScript (Cmd+K → type → Enter)
osascript -e 'tell application "Slack" to activate' -e 'delay 0.3' -e 'tell application "System Events" to keystroke "k" using command down' -e 'delay 0.2' -e 'tell application "System Events" to keystroke "general"' -e 'delay 0.3' -e 'tell application "System Events" to key code 36'

# Then read and interact with cua-driver
PID=$(pgrep -x Slack)
cua-driver get_window_state "{\"pid\":$PID,\"window_id\":$(cua-driver list_windows "{\"pid\":$PID}" | python3 -c "import sys,json; print(json.load(sys.stdin)['windows'][0]['window_id'])}")}"
```
