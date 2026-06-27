---
name: x-twitter
description: "Post tweets and threads to X/Twitter via CDP on the CopperRiver visible browser tab."
version: 1.0.0
category: integration
source: copperriver
---

# X/Twitter Posting

Post tweets and threads to X/Twitter via CDP on the Electron visible browser tab.

## Finding the X Tab

X/Twitter runs in CopperRiver's visible Electron BrowserView, NOT in the headless Chrome that `browser` tool uses. Access it via CDP on the Electron debug port:

```bash
# Find the X tab from Electron's CDP endpoint
X_TAB=$(curl -s http://localhost:9222/json/list | jq -r '.[] | select(.url | test("x\\.com")) | .id' | head -1)
WS_URL="ws://localhost:9222/devtools/page/$X_TAB"
```

If no X tab exists, navigate an existing tab or ask the user to open X in the CopperRiver browser.

## CDP Helper Pattern

```bash
IPC_URL="http://localhost:9223/ipc"  # CopperRiver IPC (if available)
# OR use CDP directly:
WS_URL="ws://localhost:9222/devtools/page/$TAB_ID"
```

For Python-based CDP control (recommended for complex interactions):

```python
import json, asyncio, websockets

async def cdp(ws, msg_id, method, params=None):
    msg = {"id": msg_id, "method": method, "params": params or {}}
    await ws.send(json.dumps(msg))
    resp = await asyncio.wait_for(ws.recv(), timeout=15)
    return json.loads(resp)
```

## Compose Box: How It Works

X uses **Draft.js** for the compose editor. Key behaviors:

1. **Compose is a modal** — opened by clicking `[data-testid="SideNav_NewTweet_Button"]` or navigating to `/compose/tweet`
2. **Drafts persist** — X saves draft content across page navigations and reloads
3. **The textarea** is `[data-testid="tweetTextarea_0"]` — a `contenteditable="true"` div
4. **Post button** is `[data-testid="tweetButton"]` or `[data-testid="tweetButtonInline"]` (whichever is visible)

## CRITICAL: Typing into Draft.js

Draft.js tracks its own internal EditorState. Standard DOM manipulation (`.innerText`, `.innerHTML`) updates the visual but NOT Draft.js state, leaving the Post button disabled.

### What Works: `Input.insertText` after `el.focus()`

```python
# 1. Focus the textarea via JS
await cdp(ws, 1, "Runtime.evaluate", {
    "expression": """
(() => {
    const el = document.querySelector('[data-testid="tweetTextarea_0"]');
    el.focus();
    el.dispatchEvent(new FocusEvent('focus', {bubbles: true}));
    return true;
})()
""",
    "returnByValue": True
})
await asyncio.sleep(0.3)

# 2. Insert text via CDP Input.insertText
await cdp(ws, 2, "Input.insertText", {"text": "Your tweet text here"})
await asyncio.sleep(1)
```

### What Does NOT Work
- `document.execCommand('insertText')` — blocked by Draft.js
- `Input.dispatchKeyEvent` with `type: "char"` — Draft.js ignores untrusted chars
- Setting `.innerText` or `.innerHTML` directly — visual only, Draft state unchanged
- `Input.insertText` WITHOUT prior `el.focus()` — text goes nowhere

### When the Textarea Already Has Text

When the compose box has persisted draft text, you must clear it first:

```python
# Method 1: Select all via JS, then delete via keyboard
await cdp(ws, 1, "Runtime.evaluate", {
    "expression": """
(() => {
    const el = document.querySelector('[data-testid="tweetTextarea_0"]');
    el.focus();
    el.dispatchEvent(new FocusEvent('focus', {bubbles: true}));
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
```

**Important:** After clearing with `execCommand('delete')`, you must re-focus before `Input.insertText`:

```python
await cdp(ws, 2, "Runtime.evaluate", {
    "expression": """
(() => {
    const el = document.querySelector('[data-testid="tweetTextarea_0"]');
    el.focus();
    el.dispatchEvent(new FocusEvent('focus', {bubbles: true}));
    return true;
})()
""",
    "returnByValue": True
})
await asyncio.sleep(0.3)
await cdp(ws, 3, "Input.insertText", {"text": "New text"})
```

### Best Strategy for Multiple Tweets (Thread)

For each tweet in a thread:

1. **Close any existing compose** — click the Close button (`aria-label="Close"`) in the modal
2. **Discard draft if prompted** — click "Discard" button if X shows a discard dialog
3. **Open fresh compose** — click `[data-testid="SideNav_NewTweet_Button"]`
4. **Verify textarea is empty** — check `innerText.trim().length === 0`
5. **Focus + type** — `el.focus()` + `FocusEvent` + `Input.insertText`
6. **Verify Post button enabled** — check `aria-disabled !== "true"`
7. **Click Post** — click the visible tweetButton/tweetButtonInline

```python
# Step-by-step for each tweet
async def post_tweet(ws, text):
    # Close existing compose if any
    await cdp(ws, 1, "Runtime.evaluate", {
        "expression": """
(() => {
    const closeBtn = Array.from(document.querySelectorAll('button'))
        .filter(b => b.getBoundingClientRect().width > 0)
        .find(b => /close/i.test(b.getAttribute('aria-label') || '') && b.closest('[aria-modal="true"]'));
    if (closeBtn) closeBtn.click();
    return !!closeBtn;
})()
""",
        "returnByValue": True
    })
    await asyncio.sleep(1)
    
    # Discard if prompted
    await cdp(ws, 2, "Runtime.evaluate", {
        "expression": """
(() => {
    const btn = Array.from(document.querySelectorAll('button'))
        .filter(b => b.getBoundingClientRect().width > 0)
        .find(b => /discard/i.test(b.innerText || ''));
    if (btn) btn.click();
    return !!btn;
})()
""",
        "returnByValue": True
    })
    await asyncio.sleep(1)
    
    # Open fresh compose
    result = await cdp(ws, 3, "Runtime.evaluate", {
        "expression": """
(() => {
    const btn = document.querySelector('[data-testid="SideNav_NewTweet_Button"]');
    if (!btn) return {ok: false};
    const r = btn.getBoundingClientRect();
    return {ok: true, x: r.x + r.width/2, y: r.y + r.height/2};
})()
""",
        "returnByValue": True
    })
    pb = result.get("result", {}).get("result", {}).get("value", {})
    if pb.get("ok"):
        await cdp(ws, 4, "Input.dispatchMouseEvent", {
            "type": "mousePressed", "x": pb["x"], "y": pb["y"],
            "button": "left", "clickCount": 1
        })
        await cdp(ws, 5, "Input.dispatchMouseEvent", {
            "type": "mouseReleased", "x": pb["x"], "y": pb["y"],
            "button": "left", "clickCount": 1
        })
    await asyncio.sleep(3)
    
    # Focus and type
    await cdp(ws, 6, "Runtime.evaluate", {
        "expression": """
(() => {
    const el = document.querySelector('[data-testid="tweetTextarea_0"]');
    if (el) { el.focus(); el.dispatchEvent(new FocusEvent('focus', {bubbles: true})); }
    return !!el;
})()
""",
        "returnByValue": True
    })
    await asyncio.sleep(0.3)
    
    await cdp(ws, 7, "Input.insertText", {"text": text})
    await asyncio.sleep(1)
    
    # Verify and post
    result = await cdp(ws, 8, "Runtime.evaluate", {
        "expression": """
(() => {
    const btns = Array.from(document.querySelectorAll('[data-testid="tweetButton"], [data-testid="tweetButtonInline"]'));
    const btn = btns.find(b => b.getBoundingClientRect().width > 0);
    if (!btn) return {ok: false};
    const r = btn.getBoundingClientRect();
    return {
        ok: true, x: r.x + r.width/2, y: r.y + r.height/2,
        disabled: btn.getAttribute('aria-disabled') === 'true'
    };
})()
""",
        "returnByValue": True
    })
    btn = result.get("result", {}).get("result", {}).get("value", {})
    
    if btn.get("ok") and not btn.get("disabled"):
        await cdp(ws, 9, "Input.dispatchMouseEvent", {
            "type": "mousePressed", "x": btn["x"], "y": btn["y"],
            "button": "left", "clickCount": 1
        })
        await cdp(ws, 10, "Input.dispatchMouseEvent", {
            "type": "mouseReleased", "x": btn["x"], "y": btn["y"],
            "button": "left", "clickCount": 1
        })
        return True
    return False
```

## Posting a Reply Thread

To create a proper thread (each tweet replying to the previous one), you need the tweet ID after posting. After clicking Post:

1. Navigate to your profile: `https://x.com/_hey_chethan`
2. Find the first tweet in the timeline
3. Click on it to open the detail view
4. Find the reply compose area `[data-testid="tweetTextarea_0"]`
5. Type and post the reply
6. Repeat for subsequent tweets

**Simpler alternative:** Post all as standalone tweets (not threaded). Less elegant but reliable.

## Key Selectors

| Element | Selector |
|---------|----------|
| Compose textarea | `[data-testid="tweetTextarea_0"]` |
| Post button | `[data-testid="tweetButton"]` or `[data-testid="tweetButtonInline"]` |
| Nav Post button | `[data-testid="SideNav_NewTweet_Button"]` |
| Close compose | `button[aria-label="Close"]` inside `[aria-modal="true"]` |
| Discard draft | Button with text "Discard" |
| Character counter | `[data-testid="tweetCharacterCount"]` or `[role="progressbar"]` |
| Modal overlay | `[aria-modal="true"]` |

## Gotchas

1. **Draft.js state vs DOM state** — Always use `Input.insertText`, never DOM manipulation
2. **Focus is everything** — `el.focus()` + `FocusEvent` dispatch required before typing
3. **Drafts persist** — X saves compose drafts across navigations; must discard between tweets
4. **Post button disabled** — If `aria-disabled="true"`, Draft.js didn't register the text. Re-focus and retry.
5. **Character limit** — X's 280 char limit applies. Draft.js disables Post when over limit.
6. **Tab ID is on port 9222** — The Electron browser's CDP is on port 9222, NOT the headless Chrome
7. **Multiple Post buttons** — Always find the visible one (with non-zero bounding rect)
8. **emoji rendering** — Emojis in `Input.insertText` work fine (⚡🧵👇 etc.)

## Thread Character Budget

X counts characters differently from JS `string.length`:
- Most emojis: 2 chars
- CJK characters: 2 chars
- URLs: counted differently after t.co wrapping
- `→` and similar: 1 char

Keep tweets under ~250 JS-string-length to be safe within 280 X-char limit.
