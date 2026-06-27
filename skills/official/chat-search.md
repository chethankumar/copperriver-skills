# Chat Search Skill

Search and retrieve past CopperRiver conversations and messages from the local SQLite database.

## Database Location

The database is at the agent22 home directory: `$HOME/agent22.db`

All timestamps are **milliseconds since epoch**. Use `datetime(ts/1000, 'unixepoch', 'localtime')` to make them readable.

## Schema

### conversations
| Column | Type | Description |
|--------|------|-------------|
| id | TEXT | Conversation ID (e.g. `conv_xxx`) |
| title | TEXT | Conversation title |
| metadata | TEXT | JSON blob — may contain `group`, `modelProfileId`, etc. |
| model_profile_id | TEXT | Model used |
| status | TEXT | `idle`, `running`, etc. |
| created_at | INTEGER | Created timestamp (ms) |
| updated_at | INTEGER | Last updated timestamp (ms) |
| workspace_path | TEXT | Workspace the conversation was in |
| compacted_until | INTEGER | Messages before this timestamp were compacted into a checkpoint |

### messages
| Column | Type | Description |
|--------|------|-------------|
| id | TEXT | Message ID |
| conversation_id | TEXT | FK to conversations.id |
| role | TEXT | `user`, `assistant`, `tool` |
| content | TEXT | Message body (markdown for user/assistant, raw output for tool) |
| timestamp | INTEGER | Timestamp (ms) |
| tool_call_id | TEXT | If role=tool, the tool call this responds to |
| tool_name | TEXT | If role=tool, which tool was called (e.g. `bash`, `browser`) |
| tool_calls | TEXT | If role=assistant, JSON array of tool invocations |
| metadata | TEXT | JSON — may contain `assistantPhase: "final"` |

### conversation_checkpoints
| Column | Type | Description |
|--------|------|-------------|
| id | TEXT | Checkpoint ID |
| conversation_id | TEXT | FK to conversations.id |
| content | TEXT | Summarized/compacted content of older messages |
| compacted_until | INTEGER | Timestamp up to which messages were compacted |
| compacted_message_count | INTEGER | How many messages were summarized |

## Query Patterns

### Search conversations by title keyword
```sql
sqlite3 "$HOME/agent22.db" "
SELECT id, title, datetime(created_at/1000, 'unixepoch', 'localtime') as created
FROM conversations
WHERE title LIKE '%KEYWORD%'
ORDER BY updated_at DESC
LIMIT 20;
"
```

### Search all messages for a keyword (fast, no FTS needed for moderate DBs)
```sql
sqlite3 "$HOME/agent22.db" "
SELECT c.title, m.role, datetime(m.timestamp/1000, 'unixepoch', 'localtime') as time, substr(m.content, 1, 200)
FROM messages m
JOIN conversations c ON c.id = m.conversation_id
WHERE m.content LIKE '%KEYWORD%'
ORDER BY m.timestamp DESC
LIMIT 30;
"
```

### Search using FTS5 (best for large databases)
Create a temporary FTS table for the session, then query it:
```sql
sqlite3 "$HOME/agent22.db" "
CREATE VIRTUAL TABLE IF NOT EXISTS fts_messages USING fts5(content, content='messages', content_rowid='rowid', tokenize='porter unicode61');
INSERT INTO fts_messages(fts_messages) VALUES('rebuild');

SELECT c.title, m.role, datetime(m.timestamp/1000, 'unixepoch', 'localtime') as time, snippet(fts_messages, -1, '>>', '<<', '...', 30) as snippet
FROM fts_messages fts
JOIN messages m ON m.content = fts.content
JOIN conversations c ON c.id = m.conversation_id
WHERE fts_messages MATCH 'search terms here'
ORDER BY rank
LIMIT 30;
"
```

Note: FTS5 rebuild is fast (~1 second for 10k messages) and safe — it reads from the existing messages table, doesn't modify data. Only do it once per search session.

### Get all messages from a specific conversation
```sql
sqlite3 "$HOME/agent22.db" "
SELECT role, datetime(timestamp/1000, 'unixepoch', 'localtime') as time, substr(content, 1, 300)
FROM messages
WHERE conversation_id = 'CONV_ID'
ORDER BY timestamp ASC;
"
```

### Get full conversation with user and assistant messages only (skip tool noise)
```sql
sqlite3 "$HOME/agent22.db" "
SELECT role, datetime(timestamp/1000, 'unixepoch', 'localtime') as time, content
FROM messages
WHERE conversation_id = 'CONV_ID' AND role IN ('user', 'assistant')
ORDER BY timestamp ASC;
"
```

### Search within a time range
```sql
-- Last 7 days (timestamps in ms)
sqlite3 "$HOME/agent22.db" "
SELECT c.title, m.role, substr(m.content, 1, 200)
FROM messages m
JOIN conversations c ON c.id = m.conversation_id
WHERE m.timestamp > (strftime('%s','now') - 7*86400) * 1000
  AND m.content LIKE '%KEYWORD%'
ORDER BY m.timestamp DESC
LIMIT 30;
"
```

### Search tool outputs (bash commands, browser results)
```sql
sqlite3 "$HOME/agent22.db" "
SELECT c.title, m.tool_name, datetime(m.timestamp/1000, 'unixepoch', 'localtime') as time, substr(m.content, 1, 300)
FROM messages m
JOIN conversations c ON c.id = m.conversation_id
WHERE m.role = 'tool' AND m.content LIKE '%KEYWORD%'
ORDER BY m.timestamp DESC
LIMIT 20;
"
```

### Get compacted/summarized history for a conversation
When messages before `compacted_until` have been removed, the summary lives in checkpoints:
```sql
sqlite3 "$HOME/agent22.db" "
SELECT content, compacted_message_count
FROM conversation_checkpoints
WHERE conversation_id = 'CONV_ID'
ORDER BY created_at DESC;
"
```

### List conversations by group
Groups are stored in the metadata JSON:
```sql
sqlite3 "$HOME/agent22.db" "
SELECT id, title, datetime(created_at/1000, 'unixepoch', 'localtime') as created
FROM conversations
WHERE json_extract(metadata, '$.group') = 'GROUP_NAME'
ORDER BY updated_at DESC;
"
```

### Recent conversations
```sql
sqlite3 "$HOME/agent22.db" "
SELECT id, title, datetime(updated_at/1000, 'unixepoch', 'localtime') as updated
FROM conversations
ORDER BY updated_at DESC
LIMIT 20;
"
```

### Count messages per conversation (find the longest chats)
```sql
sqlite3 "$HOME/agent22.db" "
SELECT c.title, COUNT(*) as message_count
FROM conversations c
JOIN messages m ON m.conversation_id = c.id
GROUP BY c.id
ORDER BY message_count DESC
LIMIT 20;
"
```

## When to Use

- **"What did we discuss about X?"** → Search messages for keyword
- **"Find the conversation about Y"** → Search conversation titles
- **"What was the solution to Z?"** → Find the conversation, then get user+assistant messages, look for final answers
- **"Summarize everything about topic X"** → Search messages across conversations, aggregate findings
- **"When did we last work on X?"** → Search messages, sort by timestamp descending
- **"Show me my conversations from last week"** → Time-bounded query on conversations table

## Tips

- Always use `substr()` when selecting `content` in exploratory queries — some messages are very long (entire file contents, API responses). Use 200-500 chars for scanning, then fetch full content once you've found the right message.
- For broad searches, start with conversation titles (small dataset, fast). Then drill into specific conversations.
- Tool messages (`role='tool'`) contain raw command output and can be noisy. Filter by `role IN ('user', 'assistant')` for the conversation flow, or search tool messages separately when looking for specific outputs.
- The `metadata` column on conversations is JSON. Use `json_extract()` to access fields like `group`.
- Checkpoints contain summaries of old messages that were compacted. Always check them if the conversation has `compacted_until` set — the early messages won't be in the messages table.
