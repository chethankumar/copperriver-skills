# Browser Control Skill

Use this skill when a user asks you to work with a webpage or web app opened in CopperRiver. CopperRiver exposes visible browser tabs through Electron's CDP debug port:

`CopperRiver BrowserView tabs → Electron --remote-debugging-port=9222 → CDP (WebSocket)`

All actions are visible to the user. Be deliberate, prefer existing tabs, and never create duplicate tabs when the user clearly referred to one that is already open.

## Non-Negotiables

- Always call `http://localhost:9222/json/list` before interacting with tabs.
- Match CopperRiver tabs by **URL or title** (the CDP target IDs differ from CopperRiver's internal `tab_xxx` IDs).
- Attach CDP once before automating a tab. If an operation returns `"Session not found"`, attach and retry once.
- Prefer compact DOM inspection with `Runtime.evaluate` over full-page HTML dumps.
- Check `success` on CDP responses before continuing.
- Do not use screenshots to understand or navigate pages. Use DOM, text, selectors, and JavaScript. Screenshots are only for user-requested visual proof.
- Tabs persist until closed. Close only tabs you created for a temporary task, unless the user wants them left open.

## Two Browser Contexts

| Context | Access Method | What's There |
|---------|---------------|-------------|
| **Electron BrowserView** | CDP `localhost:9222` | User's visible tabs (X, Slack, Gmail, any site the user opened) |
| **Headless Chrome** | `browser` tool (rebrowser-playwright) | Subagent browsing, search, research |

**Rule:** If the user says "the X tab", "my Slack", or references a specific site — use CDP on 9222. If you're doing research or browsing for information — use the `browser` tool (headless Chrome).

## Shell Helper

Define these once per shell session:

```bash
# List all visible browser tabs (CDP targets)
list_tabs() {
  curl -s http://localhost:9222/json/list | jq -r '.[] | [.id, .title, .url] | @tsv'
}

# Find a tab by URL or title keyword
find_tab() {
  local query="$1"
  curl -s http://localhost:9222/json/list | jq -r --arg q "$query" '
    map(select((.url // "" | ascii_downcase | contains($q | ascii_downcase)) or
               (.title // "" | ascii_downcase | contains($q | ascii_downcase))))
    | sort_by(.lastActivityTime // 0)
    | last
    | .id // empty
  '
}
```

## Quick Workflow

```bash
# 1. Find the tab
TAB_ID=$(find_tab "reddit")
if [ -z "$TAB_ID" ]; then
  echo "No matching tab found"
  # List all tabs to see what's available
  list_tabs
  return
fi

# 2. Connect via WebSocket and interact (use Python for complex CDP)
# Or use simple evaluate via HTTP endpoint
```

## CDP via Python (recommended for complex interactions)

For anything beyond simple page inspection, use Python with `websockets`:

```python
import json, asyncio, websockets

TAB_ID = "<cdp_target_id>"

async def cdp(ws, msg_id, method, params=None):
    msg = {"id": msg_id, "method": method, "params": params or {}}
    await ws.send(json.dumps(msg))
    resp = await asyncio.wait_for(ws.recv(), timeout=15)
    return json.loads(resp)

async def main():
    async with websockets.connect(f"ws://localhost:9222/devtools/page/{TAB_ID}") as ws:
        # Evaluate JavaScript
        result = await cdp(ws, 1, "Runtime.evaluate", {
            "expression": "document.title",
            "returnByValue": True
        })
        print(result)

asyncio.run(main())
```

## CDP via curl + jq (simple queries)

For quick one-liners, you can use the HTTP endpoint for basic evaluation:

```bash
# Note: CDP mostly requires WebSocket. For simple things, use the Python approach above.
# The HTTP list endpoint is the main useful curl target:
curl -s http://localhost:9222/json/list | jq '.[] | {id, title, url}'
```

## Page Inspection Patterns

### Compact Page Model (via Python)

```python
PAGE_MODEL_JS = """
(() => {
  const visible = (el) => {
    const s = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    return s.visibility !== "hidden" && s.display !== "none" && r.width > 0 && r.height > 0;
  };
  const text = (el) => (el.innerText || el.textContent || "").replace(/\\s+/g, " ").trim();
  const labelFor = (el) => {
    const id = el.id && CSS.escape(el.id);
    const aria = el.getAttribute("aria-label") || el.getAttribute("aria-labelledby");
    const labelled = id ? document.querySelector(`label[for="${id}"]`) : null;
    return el.getAttribute("placeholder") || aria || (labelled && text(labelled)) || text(el);
  };
  const selectorFor = (el) => {
    if (el.id) return `#${CSS.escape(el.id)}`;
    for (const attr of ["data-testid", "data-test", "data-qa", "name", "aria-label", "role"]) {
      const value = el.getAttribute(attr);
      if (value) return `${el.tagName.toLowerCase()}[${attr}=${JSON.stringify(value)}]`;
    }
    const parts = [];
    let cur = el;
    while (cur && cur.nodeType === 1 && parts.length < 4) {
      let part = cur.tagName.toLowerCase();
      const parent = cur.parentElement;
      if (parent) {
        const peers = Array.from(parent.children).filter(x => x.tagName === cur.tagName);
        if (peers.length > 1) part += `:nth-of-type(${peers.indexOf(cur) + 1})`;
      }
      parts.unshift(part);
      cur = parent;
    }
    return parts.join(" > ");
  };
  const controls = Array.from(document.querySelectorAll('a[href], button, input, textarea, select, [role="button"], [role="link"], [contenteditable="true"]'))
    .filter(visible)
    .slice(0, 80)
    .map((el, index) => ({
      index,
      tag: el.tagName.toLowerCase(),
      role: el.getAttribute("role") || "",
      type: el.getAttribute("type") || "",
      name: labelFor(el),
      href: el.href || "",
      selector: selectorFor(el)
    }));
  const headings = Array.from(document.querySelectorAll("h1,h2,h3,[role='heading']"))
    .filter(visible)
    .slice(0, 30)
    .map(el => ({level: el.tagName.toLowerCase(), text: text(el), selector: selectorFor(el)}));
  return {url: location.href, title: document.title, headings, controls};
})()
"""

# Use via: result = await cdp(ws, 1, "Runtime.evaluate", {"expression": PAGE_MODEL_JS, "returnByValue": True})
```

### Current Page Summary

```python
SUMMARY_JS = """
({
  url: location.href,
  title: document.title,
  h1: Array.from(document.querySelectorAll("h1")).map(x => x.innerText.trim()),
  visibleText: document.body.innerText.replace(/\\s+/g, " ").trim().slice(0, 2000)
})
"""
```

## Interaction Patterns

### Click via CDP

```python
# Method 1: JavaScript click (works for most buttons)
await cdp(ws, 1, "Runtime.evaluate", {
    "expression": """
    (() => {
        const button = Array.from(document.querySelectorAll("button,[role=button]"))
            .find(el => /save/i.test(el.innerText || ""));
        if (!button) return {ok:false, error:"Button not found"};
        button.scrollIntoView({block:"center"});
        button.click();
        return {ok:true};
    })()
    """,
    "returnByValue": True
})

# Method 2: CDP mouse event (for apps that ignore JS clicks)
await cdp(ws, 1, "Runtime.evaluate", {
    "expression": """
    (() => {
        const el = document.querySelector('button[type="submit"]');
        const r = el.getBoundingClientRect();
        return {x: r.x + r.width/2, y: r.y + r.height/2};
    })()
    """,
    "returnByValue": True
})
# Then: Input.dispatchMouseEvent with type="mousePressed"/"mouseReleased"
```

### Type into React/SPA Editors

Many modern web apps use JS editor frameworks that track their own state. Use `Input.insertText` after focusing:

```python
# 1. Focus the element via JS
await cdp(ws, 1, "Runtime.evaluate", {
    "expression": """
    (() => {
        const el = document.querySelector('[data-testid="editor"]');
        el.focus();
        el.dispatchEvent(new FocusEvent('focus', {bubbles: true}));
        return true;
    })()
    """,
    "returnByValue": True
})
await asyncio.sleep(0.3)

# 2. Use CDP Input.insertText (generates isTrusted input events)
await cdp(ws, 2, "Input.insertText", {"text": "Your text here"})
```

### Clear Existing Editor Text

```python
await cdp(ws, 1, "Runtime.evaluate", {
    "expression": """
    (() => {
        const el = document.querySelector('[data-testid="editor"]');
        el.focus();
        const range = document.createRange();
        range.selectNodeContents(el);
        const sel = window.getSelection();
        sel.removeAllRanges();
        sel.addRange(range);
        document.execCommand('delete');
        return true;
    })()
    """,
    "returnByValue": True
})
await asyncio.sleep(0.3)
# Then focus again and insertText
```

### Navigate to a URL

```python
await cdp(ws, 1, "Page.navigate", {"url": "https://example.com"})
```

### Screenshot

```python
result = await cdp(ws, 1, "Page.captureScreenshot", {"format": "png"})
import base64
with open("/tmp/screenshot.png", "wb") as f:
    f.write(base64.b64decode(result["result"]["data"]))
```

## Resolving @tab Mentions

When the user mentions a tab like `@hermesagent (https://www.reddit.com/r/hermesagent/)`, match it by URL or title:

```bash
# Extract URL from the mention
TAB_ID=$(find_tab "reddit.com/r/hermesagent")
```

For older mentions still using `@tab_xxx` format, resolve via CopperRiver's config:

```bash
# Read tab metadata from CopperRiver config
jq -r '.browserTabs[] | select(.id == "tab_xxx") | "\(.title) \(.url)"' \
  "$HOME/Library/Application Support/copperriver/config.json"
```

## App-Specific Notes

- **X/Twitter**: See `skills/x-twitter.md` for complete patterns
- **Slack Canvas**: Use raw CDP `Input.dispatchKeyEvent` for `isTrusted` keyboard events
- **Notion**: `Input.insertText` works after focus

## Remember

- The user can see every browser action.
- Existing tabs are the right starting point.
- Match tabs by URL/title, not by CopperRiver's internal IDs.
- Verify the result before telling the user it is done.
- CDP port 9222 is always available when CopperRiver is running.
