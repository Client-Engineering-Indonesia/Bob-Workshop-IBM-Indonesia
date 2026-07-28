# Demo Guide — IBM Bob × IBM Db2 via MCP

This guide walks you through a complete demo of IBM Bob connected to IBM Db2. Follow these steps in order to showcase the full capability of the integration.

> **Before starting:** Make sure you have completed the setup in the Instructions Guide and Bob shows `db2-techzone` as **Connected** in the MCP panel.

---

## Demo Flow Overview

| Step | What to Show | Bob Tool Used |
|---|---|---|
| 1 | Test the connection | `db2_ping` |
| 2 | Database health check report | `db2_query` (multiple) |
| 3 | Query performance report | `db2_query` (multiple) |
| 4 | Explore schema and tables | `db2_list_tables`, `db2_describe_table` |
| 5 | Create a new table | `db2_execute` |
| 6 | Validate in Genius Hub | (browser) |

---

## Step 1 — Test the Connection

**Say to Bob:**
> *"Can you ping the Db2 database?"*

**Expected result:** Bob returns the Db2 version and confirms the host IP.

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

## Step 2 — Database Health Check Report

**Say to Bob:**
> *"Give me a database health check report"*

**What Bob will check:**
- Db2 version and build level
- Tablespace utilization (SYSCATSPACE, USERSPACE1)
- Active connections and Db2 system processes
- Transaction log configuration

**Expected result:** Bob generates a formatted HTML report card. Key things to highlight:
- All tablespaces in **NORMAL** state ✅
- SYSCATSPACE may show high usage (~90%) ⚠️ — good talking point about monitoring
- All Db2 system daemons connected ✅

---

## Step 3 — Query Performance Report

**Say to Bob:**
> *"Give me a report of queries that have been executed, average CPU usage, average memory usage, and peak CPU usage"*

**What Bob will pull:**
- Statement execution count from package cache
- Average and peak CPU time per statement
- Buffer pool memory allocation
- OS-level CPU load and RAM usage from `ENV_SYS_RESOURCES`

**Expected result:** Bob generates an HTML performance report. Key things to highlight:
- Very low CPU utilization on a fresh environment ✅
- Zero lock wait and I/O wait ✅
- Buffer pool hit ratio (if workload exists)

> **Note:** On a freshly reserved environment, only monitoring queries will appear in the cache — no user workload yet. This is expected and worth mentioning to the audience.

---

## Step 4 — Explore Schema and Tables

**Say to Bob:**
> *"List all tables in the demo_col database"*

Then:
> *"Describe the [TABLE_NAME] table"*

**What to show:**
- Bob automatically filters out system schemas
- Describes column names, types, nullability

---

## Step 5 — Create a New Table

**Say to Bob:**
> *"Create a table named TABLE_ADD_TEST in the demo_col database"*

Bob will create the table with a default structure:

```sql
CREATE TABLE DB2INST1.TABLE_ADD_TEST (
  ID         INTEGER    NOT NULL,
  LABEL      VARCHAR(50),
  CREATED_AT TIMESTAMP  DEFAULT CURRENT TIMESTAMP,
  PRIMARY KEY (ID)
)
```

**Verify it exists — ask Bob:**
> *"Give me the SQL to check the table"*

Bob will respond with:
```sql
SELECT * FROM DB2INST1.TABLE_ADD_TEST
```

---

## Step 6 — Validate in Genius Hub Console

Open the Genius Hub console in a browser:
```
https://<DB2_HOST>:11101
```

Log in with `db2demo` and your password (accept the self-signed TLS warning).

**Validate each section against Bob's reports:**

| Bob Report | Genius Hub Location |
|---|---|
| Tablespace utilization | Manage → Storage → Table Spaces |
| Active connections | Monitor → Applications |
| CPU / memory metrics | Monitor → Key Insights (demo_col) |
| New table (TABLE_ADD_TEST) | Run SQL → `SELECT * FROM DB2INST1.TABLE_ADD_TEST` |

> **Important:** Genius Hub Key Insights shows `demo_col` by default. Switch the database selector to match whichever database Bob reported on. Metric differences between Bob and Genius Hub are due to measurement scope — Bob uses point-in-time Db2 monitor views, Genius Hub aggregates over the full instance lifetime.

---

## Talking Points for the Audience

1. **No SQL client needed** — Bob writes and executes the SQL from natural language
2. **Live data** — every query hits the real Db2 instance, not a simulation
3. **DDL support** — Bob can create/drop tables, not just read data
4. **Multi-database** — one connection, three databases (`demo_row`, `demo_col`, `repodb`)
5. **Report generation** — Bob produces formatted HTML reports from raw query results
6. **Reconnection is easy** — switching environments only requires updating one IP in `mcp.json`
