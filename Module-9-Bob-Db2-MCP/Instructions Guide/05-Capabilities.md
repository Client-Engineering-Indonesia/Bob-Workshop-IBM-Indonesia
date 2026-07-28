# 05 — Bob's Capabilities with Db2

Once connected, IBM Bob can interact with IBM Db2 in the following ways — all from natural language chat, no SQL client needed.

---

## 1. Test Connection

Ask Bob to verify the connection is alive and get server info.

**Example prompt:**
> *"Ping the Db2 database"*

**What Bob does:** Calls `db2_ping` → connects to Db2 → returns version and status.

**Example response:**
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

## 2. Run SELECT Queries

Ask Bob any question about the data — it will write and execute the SQL for you.

**Example prompts:**
> *"Show me all tables in the DB2INST1 schema"*
> *"Query the top 10 rows from the EMPLOYEE table"*
> *"How many rows are in each table?"*

**What Bob does:** Calls `db2_query` with a SELECT statement → returns rows as JSON.

**SQL used:**
```sql
SELECT * FROM DB2INST1.EMPLOYEE FETCH FIRST 10 ROWS ONLY
```

---

## 3. Explore Schema & Metadata

Bob can inspect table structures, columns, data types, and indexes without you writing any SQL.

**Example prompts:**
> *"List all tables in demo_col"*
> *"Describe the EMPLOYEE table"*
> *"What indexes are on the SALES table?"*

**Tools used:** `db2_list_tables`, `db2_describe_table`, `db2_get_indexes`

**Example — describe table output:**
```json
{
  "columnCount": 3,
  "columns": [
    { "COLNAME": "ID",         "TYPENAME": "INTEGER",   "NULLS": "N" },
    { "COLNAME": "LABEL",      "TYPENAME": "VARCHAR",   "NULLS": "Y" },
    { "COLNAME": "CREATED_AT", "TYPENAME": "TIMESTAMP", "NULLS": "Y" }
  ]
}
```

---

## 4. Create and Manage Tables

Bob can execute DDL statements to create, modify, or drop tables.

**Example prompts:**
> *"Create a table called CUSTOMER with columns ID, NAME, and EMAIL"*
> *"Drop the TEST_TABLE table"*
> *"Add an index on the EMAIL column of CUSTOMER"*

**Tool used:** `db2_execute`

**Example SQL Bob generates and runs:**
```sql
CREATE TABLE DB2INST1.CUSTOMER (
  ID       INTEGER     NOT NULL,
  NAME     VARCHAR(100),
  EMAIL    VARCHAR(150),
  PRIMARY KEY (ID)
)
```

---

## 5. Insert, Update, and Delete Data

Bob can write and run DML statements to manage data.

**Example prompts:**
> *"Insert a test record into the CUSTOMER table"*
> *"Update the NAME where ID = 1 to 'John Doe'"*
> *"Delete all rows from the TEST_TABLE"*

**Tool used:** `db2_execute`

**Example SQL:**
```sql
INSERT INTO DB2INST1.CUSTOMER (ID, NAME, EMAIL)
VALUES (1, 'John Doe', 'john@example.com')
```

---

## 6. Database Health Check Report

Ask Bob for a full health check — it will query multiple monitor views and generate a formatted report.

**Example prompt:**
> *"Give me a database health check report"*

**What Bob checks:**
- Tablespace utilization (used/free/total, % used)
- Db2 instance version and build level
- Active connections and application status
- Transaction log configuration

**Example output:** Bob generates an HTML report card with color-coded status indicators.

---

## 7. Query Performance Report

Bob can pull execution statistics from the Db2 monitor views.

**Example prompt:**
> *"Give me a report of queries that have been executed, average CPU usage, average memory usage, peak CPU usage"*

**What Bob queries:**
- `SYSIBMADM.MON_PKG_CACHE_SUMMARY` — cached statements, avg/peak CPU, exec time
- `SYSIBMADM.MON_CURRENT_SQL` — currently executing statements
- `SYSIBMADM.SNAPBP_PART` — buffer pool memory allocation
- `SYSIBMADM.ENV_SYS_RESOURCES` — OS-level CPU and RAM

---

## 8. Multi-Database Support

The MCP server supports three databases on the same Db2 instance:

| Database | Type | Use Case |
|---|---|---|
| `demo_row` | OLTP (row-store) | Transactional workloads, DML, DDL |
| `demo_col` | Analytics (column-store) | Analytical queries, reporting |
| `repodb` | Genius Hub repo | Genius Hub internal metadata |

Bob can query any of them in the same conversation — just specify the database name.

---

## 9. Validate Against Genius Hub Console

Bob's reports can be cross-validated against the Genius Hub web console at:
```
https://<DB2_HOST>:<DB2_CONSOLE_PORT>
```

| Bob Report Section | Genius Hub Location |
|---|---|
| Tablespace utilization | Manage → Storage → Table Spaces |
| Active connections | Monitor → Applications |
| Log configuration | Manage → Configuration → Database Configuration |
| Health alerts | Monitor → Health / Dashboard |
| Query performance | Monitor → Applications / Key Insights |

---

## Summary Table

| Capability | Tool Used | Read / Write |
|---|---|---|
| Test connection | `db2_ping` | Read |
| Run SELECT queries | `db2_query` | Read |
| List tables/views | `db2_list_tables` | Read |
| Describe table columns | `db2_describe_table` | Read |
| List indexes | `db2_get_indexes` | Read |
| CREATE / DROP / ALTER | `db2_execute` | **Write** |
| INSERT / UPDATE / DELETE | `db2_execute` | **Write** |
| CALL stored procedures | `db2_execute` | **Write** |
| Health check report | `db2_query` (multiple) | Read |
| Performance report | `db2_query` (multiple) | Read |
