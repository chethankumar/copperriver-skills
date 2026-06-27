---
name: computer-use
description: "Universal macOS desktop automation using accessibility APIs. Control any native application — click buttons, fill forms, read UI state — all while the user continues working."
version: 1.0.0
category: system
source: copperriver
---

# Computer Use

Universal macOS desktop automation that works in the background without stealing focus, cursor, or disrupting the user's workflow.

## What This Skill Does

Control any native macOS application — click buttons, fill forms, read UI state, automate workflows — all while the user continues working. Unlike browser automation or AppleScript, this operates at the OS level using accessibility APIs and can interact with hidden, minimized, or background windows.

## Core Workflow

**Always follow this pattern:**

1. **Capture first** - Take a screenshot with element overlays
2. **Identify target** - Find the element you need by its index number
3. **Act** - Click, type, or interact using the element index
4. **Verify** - Capture again to confirm the action worked

**Never guess coordinates.** Always use element-based targeting.

## Actions Reference

### Capture (Read-Only)

#### Take Screenshot with Element Overlays (Preferred)
```json
{
  "action": "capture",
  "mode": "som"
}
```
Returns: Screenshot with numbered overlays on every interactive element + accessibility tree.

**When to use:** Before every interaction. The numbered overlays are your map.

#### Plain Screenshot
```json
{
  "action": "capture",
  "mode": "vision"
}
```
Returns: Plain screenshot without overlays.

**When to use:** When you just need to see what's on screen, not interact.

#### Accessibility Tree Only
```json
{
  "action": "capture",
  "mode": "ax"
}
```
Returns: Text-only accessibility tree (no image).

**When to use:** When you need to read UI structure but don't need visual confirmation.

#### App-Specific Capture
```json
{
  "action": "capture",
  "mode": "som",
  "app": "Safari"
}
```
**When to use:** When working with a specific app. Accepts app name or bundle ID (e.g., "com.apple.Safari").

#### Limit Element Count
```json
{
  "action": "capture",
  "mode": "som",
  "max_elements": 200
}
```
**When to use:** Dense UIs (VS Code, Obsidian, IDEs) can return 500+ elements. Cap to prevent context overflow.

### Click Actions

#### Click by Element (Strongly Preferred)
```json
{
  "action": "click",
  "element": 42
}
```
**Always use this over coordinates.** Element indices come from `capture(mode='som')`.

#### Click with Modifiers
```json
{
  "action": "click",
  "element": 42,
  "modifiers": ["cmd", "shift"]
}
```
Available modifiers: `cmd`, `shift`, `option`, `alt`, `ctrl`, `fn`

#### Right Click
```json
{
  "action": "right_click",
  "element": 42
}
```

#### Double Click
```json
{
  "action": "double_click",
  "element": 42
}
```

#### Click by Coordinates (Fallback Only)
```json
{
  "action": "click",
  "coordinate": [100, 200]
}
```
**Only use when no element index is available.** Coordinates are [x, y] in logical screen space.

### Drag Actions

#### Drag Between Elements
```json
{
  "action": "drag",
  "from_element": 10,
  "to_element": 20
}
```

#### Drag by Coordinates (Fallback)
```json
{
  "action": "drag",
  "from_coordinate": [100, 200],
  "to_coordinate": [300, 400]
}
```

### Scroll Actions

```json
{
  "action": "scroll",
  "element": 42,
  "direction": "down",
  "amount": 5
}
```
- **direction**: `up`, `down`, `left`, `right`
- **amount**: Wheel ticks (default: 3)

### Keyboard Actions

#### Type Text
```json
{
  "action": "type",
  "text": "Hello, world!"
}
```
Respects current keyboard layout. Types at current cursor position.

#### Press Key Combinations
```json
{
  "action": "key",
  "keys": "cmd+s"
}
```
Examples: `cmd+s`, `ctrl+alt+t`, `return`, `escape`, `tab`

Use `+` to combine keys.

### Set Value (Advanced)

#### Set Dropdown/Select Value
```json
{
  "action": "set_value",
  "element": 42,
  "value": "Blue"
}
```
**When to use:** For AXPopUpButton / select dropdowns. Pass the option's display label. This selects the option directly without opening the native menu (no focus steal).

#### Set Slider Value
```json
{
  "action": "set_value",
  "element": 42,
  "value": "50"
}
```
**When to use:** For sliders and other AXValue-settable elements.

### App Management

#### List Running Apps
```json
{
  "action": "list_apps"
}
```
Returns: Array of running applications with name, PID, bundle ID.

#### Focus App (Background Mode)
```json
{
  "action": "focus_app",
  "app": "Safari"
}
```
Routes input to the app without raising the window. User's current app stays in front.

#### Focus App (Disruptive Mode)
```json
{
  "action": "focus_app",
  "app": "Safari",
  "raise_window": true
}
```
**Warning:** Brings window to front. Disrupts user. Only use when explicitly requested.

### Utility Actions

#### Wait
```json
{
  "action": "wait",
  "seconds": 2
}
```
Max: 30 seconds.

#### Capture After Action
```json
{
  "action": "click",
  "element": 42,
  "capture_after": true
}
```
Takes a follow-up screenshot after the action. Saves a round-trip for verification.

## Safety & Approval

### Always Allowed (No Approval)
- `capture` (all modes)
- `list_apps`
- `wait`

### Requires Approval
All interaction actions: `click`, `double_click`, `right_click`, `middle_click`, `drag`, `scroll`, `type`, `key`, `set_value`, `focus_app`

### Hard-Blocked (Never Allowed)

**Key combinations:**
- `cmd+shift+backspace` - Empty trash
- `cmd+option+backspace` - Force delete
- `cmd+ctrl+q` - Lock screen
- `cmd+shift+q` - Log out
- `cmd+option+shift+q` - Force log out

**Type patterns:**
- `curl ... | bash` or `curl ... | sh`
- `wget ... | bash`
- `sudo rm -rf`
- `rm -rf /`
- Fork bombs

## Common Patterns

### Pattern 1: Click a Button
```
1. capture(mode='som') → See numbered overlays
2. Identify button (e.g., element #15)
3. click(element=15)
4. capture(mode='som', capture_after=true) → Verify
```

### Pattern 2: Fill a Form
```
1. capture(mode='som')
2. click(element=<first_field>)
3. type(text="John Doe")
4. key(keys="tab")
5. type(text="john@example.com")
6. click(element=<submit_button>)
```

### Pattern 3: Select from Dropdown
```
1. capture(mode='som')
2. set_value(element=<dropdown>, value="Option Name")
   OR
2. click(element=<dropdown>)
3. wait(seconds=0.5)
4. capture(mode='som')
5. click(element=<option>)
```

### Pattern 4: Work with Specific App
```
1. list_apps() → Find app name/PID
2. focus_app(app="AppName")
3. capture(mode='som', app="AppName")
4. [interact with app]
```

### Pattern 5: Scroll and Search
```
1. capture(mode='som')
2. scroll(element=<scrollable_area>, direction="down", amount=5)
3. capture(mode='som')
4. [repeat until target found]
```

## Troubleshooting

### "Element not found"
- The UI changed between capture and action
- Solution: Capture again immediately before acting

### "Too many elements" / Context overflow
- Dense UI (IDE, Electron app) returned 500+ elements
- Solution: Use `max_elements` parameter or target specific app

### "Action had no effect"
- Wrong element targeted
- Solution: Verify element index from latest capture

### "Focus stolen" / User disrupted
- Used `raise_window=true` or clicked wrong window
- Solution: Always use `raise_window=false` (default)

### Coordinates not working
- Screen resolution changed or window moved
- Solution: Always use element-based targeting, never coordinates

## Advanced Techniques

### Multi-Step Verification
```json
{
  "action": "click",
  "element": 42,
  "capture_after": true
}
```
Combines action + verification in one call. Saves a round-trip.

### App-Scoped Operations
When working with a specific app for multiple actions:
```
1. focus_app(app="Safari")
2. All subsequent captures/actions automatically scoped to Safari
```

### Dense UI Handling
For apps with 500+ UI elements:
```
1. capture(mode='som', app="VS Code", max_elements=100)
2. If target not found, increase max_elements or narrow scope
```

### Background Automation
All actions work on hidden/minimized windows:
```
1. focus_app(app="Mail", raise_window=false)
2. capture(mode='som', app="Mail")
3. [automate without bringing Mail to front]
```

## Limitations

- **macOS only** - Uses private Apple APIs
- **Requires cua-driver** - Must be installed separately
- **30-second timeout** - Per operation
- **Max 1000 elements** - Per accessibility tree capture
- **Private APIs** - Can break on OS updates

## Installation

If computer_use tool is not available:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/trycua/cua/main/libs/cua-driver/scripts/install.sh)"
```

Or run: `hermes tools` and enable Computer Use toolset.

## When to Use This Skill

✅ **Use when:**
- Automating native macOS apps (Mail, Calendar, Finder, etc.)
- Filling forms in desktop applications
- Testing UI workflows
- Reading UI state from background apps
- Chaining actions across multiple apps

❌ **Don't use when:**
- Web automation (use browser tool instead)
- Simple file operations (use file tools)
- Terminal commands (use terminal tool)
- The user is actively working in the target app (wait or ask first)

## Examples

### Example 1: Open Safari and Navigate
```
User: "Open Safari and go to github.com"

1. list_apps() → Check if Safari is running
2. focus_app(app="Safari", raise_window=true)
3. wait(seconds=1)
4. capture(mode='som', app="Safari")
5. click(element=<address_bar>)
6. type(text="github.com")
7. key(keys="return")
```

### Example 2: Read Notification
```
User: "What does my latest notification say?"

1. capture(mode='som')
2. [Identify notification element from overlays]
3. capture(mode='ax') → Get text content
4. [Parse and report notification text]
```

### Example 3: Fill Form in Background
```
User: "Fill out the registration form in the app behind my browser"

1. list_apps() → Find target app
2. focus_app(app="RegistrationApp", raise_window=false)
3. capture(mode='som', app="RegistrationApp")
4. click(element=<name_field>)
5. type(text="John Doe")
6. [continue filling form]
7. click(element=<submit_button>, capture_after=true)
```

## Best Practices

1. **Always capture before acting** - UI state changes constantly
2. **Use element indices, not coordinates** - 10x more reliable
3. **Verify after destructive actions** - Use `capture_after=true`
4. **Scope to specific apps** - Reduces element count and improves accuracy
5. **Never raise windows unless asked** - Respect user's workflow
6. **Wait after UI changes** - Give animations time to complete (0.5-1s)
7. **Handle dense UIs carefully** - Use `max_elements` to prevent context overflow
8. **Check approval requirements** - Warn user before destructive actions

## Related Skills

- **browser-control.md** - For web automation (Chrome/Safari tabs)
- **terminal_tool** - For shell commands
- **file_tools** - For file operations

---

**Remember:** This is a powerful tool. Always capture first, target by element, and verify after. Never guess coordinates.
