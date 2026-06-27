#!/usr/bin/env python3
"""
Slack CDP Helper - One-command Slack operations via Chrome DevTools Protocol.

Usage:
  python3 slack_helper.py find <name>
  python3 slack_helper.py dm <name> <message>
  python3 slack_helper.py send <message>          # send to current open DM/channel
  python3 slack_helper.py read [count]             # read last N messages
  python3 slack_helper.py navigate <name>          # navigate to channel/DM by name
  python3 slack_helper.py status                   # show current conversation info
"""

import asyncio
import json
import sys
import os

CDP_PORT = 9222

def find_slack_target():
    """Find the Slack tab's CDP target ID."""
    import urllib.request
    try:
        resp = urllib.request.urlopen(f"http://localhost:{CDP_PORT}/json/list")
        targets = json.loads(resp.read())
        for t in targets:
            if 'slack.com/client' in t.get('url', ''):
                return t['id'], t['url']
    except:
        pass
    return None, None

async def cdp_ws():
    """Get a websocket connection to the Slack tab."""
    target_id, _ = find_slack_target()
    if not target_id:
        print("ERROR: No Slack tab found. Open Slack in Chrome first.")
        sys.exit(1)
    ws = await __import__('websockets').connect(f"ws://localhost:{CDP_PORT}/devtools/page/{target_id}")
    return ws

async def eval_js(ws, expr, timeout=5):
    """Evaluate JS in the Slack page. Uses IIFE to avoid redeclaration errors."""
    wrapped = f"(function() {{ {expr} }})()"
    cid = hash(wrapped) % 100000
    await ws.send(json.dumps({'id': cid, 'method': 'Runtime.evaluate', 'params': {'expression': wrapped, 'returnByValue': True}}))
    
    deadline = asyncio.get_event_loop().time() + timeout
    while asyncio.get_event_loop().time() < deadline:
        try:
            msg = await asyncio.wait_for(ws.recv(), timeout=1)
            data = json.loads(msg)
            if data.get('id') == cid:
                result = data.get('result', {}).get('result', {})
                if result.get('subtype') == 'error':
                    return None, result.get('description', 'Unknown error')
                return result.get('value'), None
        except asyncio.TimeoutError:
            continue
    return None, "Timeout waiting for CDP response"

async def eval_js_retry(ws, expr, retries=2):
    """Evaluate JS, retrying once on redeclaration errors by wrapping in IIFE with fresh scope."""
    val, err = await eval_js(ws, expr)
    if err and 'already been declared' in (err or ''):
        # The IIFE should handle this, but try eval instead of call
        cid = hash(expr + str(asyncio.get_event_loop().time())) % 100000
        await ws.send(json.dumps({'id': cid, 'method': 'Runtime.evaluate', 'params': {
            'expression': expr,
            'returnByValue': True
        }}))
        for _ in range(10):
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=1)
                data = json.loads(msg)
                if data.get('id') == cid:
                    result = data.get('result', {}).get('result', {})
                    if result.get('subtype') == 'error':
                        return None, result.get('description')
                    return result.get('value'), None
            except:
                continue
    return val, err

def get_workspace_id():
    """Extract workspace ID from current Slack URL."""
    import urllib.request
    resp = urllib.request.urlopen(f"http://localhost:{CDP_PORT}/json/list")
    targets = json.loads(resp.read())
    for t in targets:
        if 'slack.com/client' in t.get('url', ''):
            parts = t['url'].split('/')
            return parts[-2] if len(parts) >= 2 else None
    return None

async def search_sidebar(ws, name):
    """Search sidebar virtual-list-items for a name match. Returns list of {name, key}."""
    expr = f'''
        var items = Array.from(document.querySelectorAll("[data-qa='virtual-list-item']"));
        var results = items.map(function(el) {{
            var n = el.innerText.split('\\n')[0];
            var k = el.getAttribute('data-item-key');
            return {{name: n, key: k}};
        }}).filter(function(i) {{ return i.name && i.name.toLowerCase().includes("{name.lower()}") }});
        return JSON.stringify(results);
    '''
    val, err = await eval_js(ws, expr)
    if val:
        return json.loads(val)
    return []

async def do_find(name):
    ws = await cdp_ws()
    results = await search_sidebar(ws, name)
    if not results:
        print(f"No sidebar matches for '{name}'. Try scrolling sidebar or use navigate.")
    else:
        for r in results:
            print(f"  {r['name']}  →  {r['key']}")
    await ws.close()

async def do_navigate(name):
    ws = await cdp_ws()
    workspace = get_workspace_id()
    results = await search_sidebar(ws, name)
    
    if not results:
        print(f"'{name}' not found in sidebar.")
        await ws.close()
        return
    
    target = results[0]
    url = f"https://app.slack.com/client/{workspace}/{target['key']}"
    
    await ws.send(json.dumps({'id': 1, 'method': 'Runtime.evaluate', 'params': {
        'expression': f'window.location.href = "{url}"'
    }}))
    await asyncio.sleep(2)
    
    # Verify
    val, _ = await eval_js(ws, 'return document.querySelector("[data-qa=texty_input]")?.getAttribute("aria-label") || document.title')
    print(f"Navigated to: {val}")
    await ws.close()

async def do_send(message):
    """Send a message to the currently open conversation."""
    ws = await cdp_ws()
    
    # Focus input and type via execCommand
    escaped_msg = json.dumps(message)
    val, err = await eval_js(ws, f'''
        var el = document.querySelector("[data-qa=texty_input]");
        if (!el) return "ERROR: No message input found";
        el.focus();
        document.execCommand("selectAll");
        document.execCommand("delete");
        document.execCommand("insertText", false, {escaped_msg});
        return el.textContent;
    ''')
    
    if err or (isinstance(val, str) and val.startswith("ERROR")):
        print(f"Failed to type message: {err or val}")
        await ws.close()
        return
    
    await asyncio.sleep(0.3)
    
    # Click send button via JS
    val, err = await eval_js(ws, '''
        var btn = document.querySelector("[data-qa=texty_send_button]");
        if (!btn) return "ERROR: No send button";
        btn.click();
        return "sent";
    ''')
    
    if err or (isinstance(val, str) and val.startswith("ERROR")):
        print(f"Send failed: {err or val}")
        await ws.close()
        return
    
    await asyncio.sleep(1)
    
    # Verify input cleared
    val, _ = await eval_js(ws, 'return document.querySelector("[data-qa=texty_input]").textContent || "(empty)"')
    if val == "(empty)" or val == "":
        print("✓ Message sent")
    else:
        print(f"⚠ Message may not have sent. Input still has: {val}")
    
    await ws.close()

async def do_dm(name, message):
    """Navigate to a DM and send a message. All-in-one."""
    ws = await cdp_ws()
    workspace = get_workspace_id()
    
    # Search sidebar
    results = await search_sidebar(ws, name)
    if not results:
        print(f"'{name}' not found in sidebar.")
        await ws.close()
        return
    
    target = results[0]
    
    # Navigate to DM
    url = f"https://app.slack.com/client/{workspace}/{target['key']}"
    await ws.send(json.dumps({'id': 1, 'method': 'Runtime.evaluate', 'params': {
        'expression': f'window.location.href = "{url}"'
    }}))
    await asyncio.sleep(2)
    
    # Type message
    escaped_msg = json.dumps(message)
    val, err = await eval_js(ws, f'''
        var el = document.querySelector("[data-qa=texty_input]");
        if (!el) return "ERROR: No message input found";
        el.focus();
        document.execCommand("selectAll");
        document.execCommand("delete");
        document.execCommand("insertText", false, {escaped_msg});
        return el.textContent;
    ''')
    
    if err or (isinstance(val, str) and val.startswith("ERROR")):
        print(f"Failed to type: {err or val}")
        await ws.close()
        return
    
    await asyncio.sleep(0.3)
    
    # Click send
    val, err = await eval_js(ws, '''
        var btn = document.querySelector("[data-qa=texty_send_button]");
        if (!btn) return "ERROR: No send button";
        btn.click();
        return "sent";
    ''')
    
    await asyncio.sleep(1)
    
    # Verify
    val, _ = await eval_js(ws, 'return document.querySelector("[data-qa=texty_input]").textContent || "(empty)"')
    if val == "(empty)" or val == "":
        print(f"✓ Message sent to {target['name']}")
    else:
        print(f"⚠ May not have sent. Input: {val}")
    
    await ws.close()

async def do_read(count=5):
    """Read the last N messages from current conversation."""
    ws = await cdp_ws()
    
    val, err = await eval_js(ws, f'''
        var msgs = Array.from(document.querySelectorAll("[data-qa=message-text]"));
        var recent = msgs.slice(-{count});
        var result = recent.map(function(m) {{
            var senderEl = m.closest("[data-qa=message_container]") || m.closest(".c-message");
            var sender = "";
            if (senderEl) {{
                var s = senderEl.querySelector("[data-qa=message_sender_name]");
                if (s) sender = s.innerText;
            }}
            return sender + ": " + m.innerText;
        }});
        return JSON.stringify(result);
    ''')
    
    if val:
        msgs = json.loads(val) if isinstance(val, str) else val
        for m in msgs:
            print(f"  {m}")
    elif err:
        print(f"Error reading messages: {err}")
    
    await ws.close()

async def do_status():
    """Show current conversation info."""
    ws = await cdp_ws()
    val, _ = await eval_js(ws, '''
        return JSON.stringify({
            title: document.title,
            inputLabel: document.querySelector("[data-qa=texty_input]")?.getAttribute("aria-label") || "none",
            url: window.location.href
        });
    ''')
    if val:
        info = json.loads(val) if isinstance(val, str) else val
        print(f"  Title: {info.get('title', '?')}")
        print(f"  Input: {info.get('inputLabel', '?')}")
        print(f"  URL:   {info.get('url', '?')}")
    await ws.close()

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "find" and len(sys.argv) >= 3:
        asyncio.run(do_find(sys.argv[2]))
    elif cmd == "dm" and len(sys.argv) >= 4:
        asyncio.run(do_dm(sys.argv[2], " ".join(sys.argv[3:])))
    elif cmd == "send" and len(sys.argv) >= 3:
        asyncio.run(do_send(" ".join(sys.argv[2:])))
    elif cmd == "read":
        count = int(sys.argv[2]) if len(sys.argv) >= 3 else 5
        asyncio.run(do_read(count))
    elif cmd == "navigate" and len(sys.argv) >= 3:
        asyncio.run(do_navigate(sys.argv[2]))
    elif cmd == "status":
        asyncio.run(do_status())
    else:
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()
