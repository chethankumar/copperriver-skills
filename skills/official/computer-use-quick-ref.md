# Computer Use - Quick Reference

## The Golden Rule
**Always capture → identify element → act → verify**

Never guess coordinates. Always use element indices.

## Most Common Actions

### 1. Capture with Overlays
```json
{"action": "capture", "mode": "som"}
```
Returns screenshot with numbered elements.

### 2. Click Element
```json
{"action": "click", "element": 42}
```

### 3. Type Text
```json
{"action": "type", "text": "Hello"}
```

### 4. Press Keys
```json
{"action": "key", "keys": "cmd+s"}
```

### 5. Scroll
```json
{"action": "scroll", "element": 42, "direction": "down", "amount": 5}
```

### 6. Set Dropdown Value
```json
{"action": "set_value", "element": 42, "value": "Option Name"}
```

## Quick Patterns

### Click Button
```
capture(som) → click(element) → capture(som)
```

### Fill Form
```
capture(som) → click(field) → type(text) → tab → type(text) → click(submit)
```

### Work with Specific App
```
list_apps() → focus_app(name) → capture(som, app=name) → [interact]
```

## Safety Reminders

✅ **Always allowed**: capture, list_apps, wait
⚠️ **Needs approval**: click, type, key, scroll, drag, set_value
🚫 **Hard-blocked**: logout keys, `curl | bash`, `sudo rm -rf`

## Troubleshooting

- **Element not found**: Capture again (UI changed)
- **Too many elements**: Use `max_elements` or scope to app
- **Focus stolen**: Don't use `raise_window=true`
- **Coordinates fail**: Use element indices instead

## When to Use

✅ Native macOS apps, background automation, form filling
❌ Web pages (use browser-control), files (use file tools), terminal (use bash)

---
See `computer-use.md` for full documentation.
