# 03 — Configure Bob to Connect to Db2

This guide registers the Db2 MCP server in IBM Bob so Bob can use its tools.

> **Before starting:** Make sure `npm run build` completed successfully in the previous step and you have the full path to `build/index.js` ready.

---

## How MCP Configuration Works in Bob

Bob reads a config file called `mcp.json` at startup. This file tells Bob:
- Where your MCP server program is (`args`)
- How to start it (`command`)
- What credentials to pass to it (`env`)

There are two scopes:

| Scope | File Location | When to Use |
|---|---|---|
| **Global** | `C:\Users\<YourUsername>\.bob\settings\mcp.json` | Available in all workspaces — recommended |
| **Workspace** | `.bob\mcp.json` inside your project folder | Only available in that specific project |

> This module uses the **Global** config so the Db2 connection is available everywhere in Bob.

---

## Step 1 — Open the Global Config File

Navigate to:
```
C:\Users\<YourUsername>\.bob\settings\
```

- If `mcp.json` **already exists**: open it — you will add your server to the existing file
- If it **does not exist**: create a new file named `mcp.json` in that folder

> **Warning:** If the file already has other servers, do NOT delete them. Add your new server alongside them inside the `mcpServers` object.

---

## Step 2 — Add the Db2 Server Entry

Paste the following into `mcp.json`. Replace the two placeholder values:

```json
{
  "mcpServers": {
    "db2-techzone": {
      "command": "node",
      "args": ["C:/Users/<YourUsername>/path/to/db2-mcp-server/build/index.js"],
      "env": {
        "DB2_HOST": "<YOUR_DB2_VM_IP>",
        "DB2_PORT": "25010",
        "DB2_USERNAME": "db2demo",
        "DB2_PASSWORD": "<YOUR_DB2_PASSWORD>",
        "DB2_DATABASE": "DEMO_COL",
        "DB2_CONSOLE_PORT": "11101"
      },
      "disabled": false,
      "alwaysAllow": [
        "db2_ping",
        "db2_query",
        "db2_list_tables",
        "db2_describe_table",
        "db2_get_indexes",
        "db2_execute"
      ]
    }
  }
}
```

---

## Field-by-Field Explanation

### Top-level fields

| Field | What to put here |
|---|---|
| `"db2-techzone"` | The server name — this is what appears in Bob's MCP panel. Can be any name you choose. |
| `"command"` | Always `"node"` — this tells Bob to run the server using Node.js. |
| `"args"` | The **absolute path** to `build/index.js`. Use **forward slashes** even on Windows. Get this from Step 7 of the build guide. |
| `"disabled"` | `false` = server is active. `true` = server is registered but not started (useful for temporarily disabling). |

### `env` block — Db2 connection details

These values are passed to the MCP server as environment variables at startup:

| Key | What to fill in |
|---|---|
| `DB2_HOST` | The **IP address** of your Db2 VM. This is the only value you need to change when switching TechZone environments. |
| `DB2_PORT` | Db2 TCP port. Default for TechZone: `25010`. |
| `DB2_USERNAME` | Db2 login username. Default for TechZone: `db2demo`. |
| `DB2_PASSWORD` | Your Db2 password. **The server will refuse to start if this is empty.** |
| `DB2_DATABASE` | Default database. Options: `DEMO_COL`, `DEMO_ROW`, `REPODB`. |
| `DB2_CONSOLE_PORT` | Genius Hub console port. Default: `11101`. |

### `alwaysAllow` list

This tells Bob to run these tools **without showing an approval prompt** every time. All 6 tools are listed for a smooth experience. You can remove any tool from this list to require manual approval.

| Tool | What it does |
|---|---|
| `db2_ping` | Test connection + get server version |
| `db2_query` | Run SELECT queries |
| `db2_list_tables` | List tables and views in a schema |
| `db2_describe_table` | Show column definitions of a table |
| `db2_get_indexes` | List indexes on a table |
| `db2_execute` | Run INSERT, UPDATE, DELETE, CREATE, DROP, CALL |

---

## Step 3 — Save and Reload Bob

> ❌ **This step always requires your manual action** — Bob cannot click its own UI buttons.

1. **Save** `mcp.json`
2. Look at the **bottom status bar** of Bob — find the **MCP icon** (plug/connector symbol) and click it
   - Alternatively: go to **Settings → MCP**
3. The MCP panel will open showing a list of servers
4. Find **`db2-techzone`** in the list
5. Click the **Restart** button next to it (or toggle the switch OFF then ON)
6. Wait 3–5 seconds — the status indicator should turn **green** and show **Connected**

### What to look for in the MCP panel

```
MCP Servers
─────────────────────────────────────
● db2-techzone          Connected    ← GREEN dot = working ✅
  db2_ping, db2_query, db2_execute...

○ db2-techzone          Inactive     ← GREY dot = not started
○ db2-techzone          Failed       ← RED = error, check troubleshooting below
─────────────────────────────────────
```

> If `db2-techzone` does not appear in the list at all, the JSON in `mcp.json` may be malformed. Check for missing commas or brackets — then save and check again.

---

## Step 4 — Test the Connection

In Bob chat, type:

> *"Can you ping the Db2 database?"*

Bob should call `db2_ping` and return:

```json
{
  "status": "connected",
  "host": "<YOUR_VM_IP>",
  "port": "25010",
  "database": "demo_row",
  "serverInfo": {
    "SERVICE_LEVEL": "DB2 v12.1.5.0",
    "FIXPACK_NUM": 0
  }
}
```

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| `db2-techzone` not in MCP panel | `mcp.json` has invalid JSON | Validate JSON syntax — check for missing commas, quotes, or brackets |
| Server shows as **Failed** | Wrong path in `args` | Make sure the path points to `build/index.js` and uses forward slashes |
| Server shows as **Failed** | `DB2_PASSWORD` is empty | Fill in the password in the `env` block |
| Server shows as **Inactive** | `"disabled": true` | Change to `"disabled": false` and restart |
| Ping returns `Connection failed` | Db2 VM is not running or wrong IP | Check the VM is started in TechZone and verify `DB2_HOST` |
| Server connects but ping fails | Wrong port | Confirm `DB2_PORT` matches your TechZone environment (default: `25010`) |
| `node: command not found` | Node.js not in PATH | Reinstall Node.js and ensure it is added to PATH |

---

## Final Setup Checklist

Go through this before running the demo. Each item has a clear action:

| # | Check | How to verify |
|---|---|---|
| 1 | `mcp.json` saved with correct path in `args` | Open the file and confirm the path points to `build/index.js` |
| 2 | `DB2_HOST` is the correct VM IP | Check your TechZone reservation page |
| 3 | `DB2_PASSWORD` is filled in | Open `mcp.json` — the field must not be empty or a placeholder |
| 4 | `db2-techzone` shows as **Connected** | Look at the MCP panel — green dot next to the server name |
| 5 | Bob ping returns `"status": "connected"` | Type *"ping the Db2 database"* in Bob chat |
| 6 | Ping shows correct host IP | The `"host"` field in the response matches your VM IP |
| 7 | Ping shows `"SERVICE_LEVEL": "DB2 v12.x.x.x"` | The `"serverInfo"` field in the ping response |

**All 7 checked?** You are ready. Proceed to **[DEMO-GUIDE.md](../DEMO-GUIDE.md)**.
