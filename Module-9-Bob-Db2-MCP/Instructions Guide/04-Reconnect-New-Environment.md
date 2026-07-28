# 04 — Reconnect to a New Db2 Environment

IBM TechZone environments have a limited reservation period. When your reservation expires and you reserve a new one, the **VM IP address changes**. This guide shows you how to update the connection in Bob.

---

## What Changes Between Environments

When you get a new TechZone Db2 reservation, only the **VM IP address** changes. Everything else stays the same:

| Setting | Changes? |
|---|---|
| `DB2_HOST` | ✅ **Yes — new IP address** |
| `DB2_PORT` | ❌ No |
| `DB2_USERNAME` | ❌ No |
| `DB2_PASSWORD` | ❌ No |
| `DB2_DATABASE` | ❌ No |
| `DB2_CONSOLE_PORT` | ❌ No |

> **Note:** Your TechZone reservation also gives you an SSH key and an API key. These are for accessing the VM via SSH or the Genius Hub web UI — they are **not used** by the MCP server. Only the IP address matters here.

---

## Step 1 — Get the New VM IP Address

From your TechZone reservation details page, find the new **VM IP address**.

Example: `<YOUR_NEW_VM_IP>`

---

## Step 2 — Update the Global Config

Open the global MCP config file:
```
C:\Users\<YourUsername>\.bob\settings\mcp.json
```

Find the `DB2_HOST` line and replace the old IP with the new one:

**Before:**
```json
"DB2_HOST": "<YOUR_OLD_VM_IP>",
```

**After:**
```json
"DB2_HOST": "<YOUR_NEW_VM_IP>",
```

Save the file.

> **Important:** Also check your workspace config at `.bob/mcp.json` if you have one — it may also need updating if both files exist.

---

## Step 3 — Restart the MCP Server in Bob

Saving the file alone is not enough — the MCP server process needs to be restarted to pick up the new environment variable.

1. Open the **MCP panel** in Bob (bottom status bar → MCP icon)
2. Find `db2-techzone`
3. Click **Restart** (or toggle Disable → Enable)
4. Wait for the status to show **Connected** (green)

> If restarting doesn't work, do a **full restart of IBM Bob** to ensure the server process is killed and relaunched fresh.

---

## Step 4 — Verify the Connection

Ask Bob to ping the database:

> *"Can you ping the Db2 database?"*

A successful response confirms the new environment is live:

```json
{
  "status": "connected",
  "host": "<YOUR_NEW_VM_IP>",
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
| Still connecting to old IP after restart | Bob not fully restarted | Close and reopen Bob completely |
| `db2-techzone` shows as Inactive | Config file not saved, or wrong scope | Check both workspace and global `mcp.json` |
| Connection timeout error | New VM not yet running | Wait a few minutes and try again — TechZone VMs take time to boot |
| Authentication error | Password changed on new environment | Update `DB2_PASSWORD` in `mcp.json` as well |
