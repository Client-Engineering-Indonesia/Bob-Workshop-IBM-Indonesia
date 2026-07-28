#!/usr/bin/env node
/**
 * IBM Db2 MCP Server — Direct connection via ibm_db
 * Connects IBM Bob directly to IBM Db2 database
 *
 * Environment Variables (set these in mcp.json — do NOT hardcode credentials here):
 *   DB2_HOST         - Db2 VM IP address        (required)
 *   DB2_PORT         - Db2 TCP port              (default: 25010)
 *   DB2_USERNAME     - Db2 login username        (default: db2demo)
 *   DB2_PASSWORD     - Db2 login password        (required)
 *   DB2_DATABASE     - Default database name     (default: DEMO_COL)
 *   DB2_CONSOLE_PORT - Genius Hub console port   (default: 11101)
 */
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { Agent, fetch as undiciFetch } from "undici";
import ibmdb from "ibm_db";

// ---------------------------------------------------------------------------
// Config — reads from environment variables injected by Bob via mcp.json
// ---------------------------------------------------------------------------
const DB2_HOST         = process.env.DB2_HOST         ?? "YOUR_DB2_HOST";
const DB2_PORT         = process.env.DB2_PORT         ?? "25010";
const DB2_USERNAME     = process.env.DB2_USERNAME     ?? "db2demo";
const DB2_PASSWORD     = process.env.DB2_PASSWORD;           // required — no default
const DB2_DATABASE     = process.env.DB2_DATABASE     ?? "DEMO_COL";
const DB2_CONSOLE_PORT = process.env.DB2_CONSOLE_PORT ?? "11101";

// Exit immediately if no password is provided — prevents silent auth failures
if (!DB2_PASSWORD) {
  console.error("[db2-mcp] ERROR: DB2_PASSWORD environment variable is required.");
  process.exit(1);
}

// Genius Hub REST API base URL — used by the ping tool
const BASE_URL = `https://${DB2_HOST}:${DB2_CONSOLE_PORT}/dbapi/v4`;

// TLS agent that skips certificate verification
// TechZone Db2 environments use self-signed certificates
const tlsAgent = new Agent({ connect: { rejectUnauthorized: false } });

// ---------------------------------------------------------------------------
// Core function: runSQL
// Opens a Db2 connection, executes SQL, closes the connection, returns rows.
// All 6 tools call this function internally.
// ---------------------------------------------------------------------------
async function runSQL(sql: string, database: string, limit = 100): Promise<any[]> {
  // Build the Db2 connection string using TCPIP protocol
  const connStr = `DATABASE=${database.toUpperCase()};HOSTNAME=${DB2_HOST};PORT=${DB2_PORT};PROTOCOL=TCPIP;UID=${DB2_USERNAME};PWD=${DB2_PASSWORD};`;

  return new Promise((resolve, reject) => {
    ibmdb.open(connStr, (err: any, conn: any) => {
      if (err) return reject(new Error(`Connection failed: ${err.message}`));

      // Automatically append FETCH FIRST to SELECT queries to prevent huge result sets
      let limitedSql = sql.trim();
      const upper = limitedSql.toUpperCase();
      if (upper.startsWith("SELECT") && !upper.includes("FETCH FIRST")) {
        limitedSql = `${limitedSql} FETCH FIRST ${limit} ROWS ONLY`;
      }

      conn.query(limitedSql)
        .then((data: any[]) => {
          conn.close(() => {});
          resolve(data ?? []);
        })
        .catch((queryErr: any) => {
          conn.close(() => {});
          reject(new Error(`Query failed: ${queryErr.message}`));
        });
    });
  });
}

// ---------------------------------------------------------------------------
// Genius Hub REST helper: getToken
// Authenticates against the Genius Hub API and returns a bearer token.
// Used internally by ping to check the console connection.
// ---------------------------------------------------------------------------
async function getToken(): Promise<string> {
  const res = await undiciFetch(`${BASE_URL}/auth/tokens`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ userid: "admin", password: DB2_PASSWORD }),
    dispatcher: tlsAgent,
  });
  if (!res.ok) throw new Error(`Auth failed (${res.status}): ${await res.text()}`);
  const json = (await res.json()) as any;
  if (!json.token) throw new Error("Auth response missing token");
  return json.token;
}

// ---------------------------------------------------------------------------
// MCP Server instance
// The server name and version are shown in Bob's MCP panel
// ---------------------------------------------------------------------------
const server = new McpServer({ name: "db2-mcp-server", version: "0.1.0" });

// ── Tool 1: db2_ping ────────────────────────────────────────────────────────
// Tests the Db2 connection and returns the server version.
// Use this first to confirm Bob can reach the Db2 environment.
server.registerTool("db2_ping", {
  description: "Test the connection to IBM Db2 and return server version info.",
  inputSchema: z.object({
    database: z
      .enum(["demo_col", "demo_row", "repodb"])
      .optional()
      .describe("Database to ping (default: demo_row)"),
  }),
}, async ({ database }) => {
  const db = database ?? "demo_row";
  try {
    const rows = await runSQL(
      "SELECT SERVICE_LEVEL, FIXPACK_NUM FROM TABLE(SYSPROC.ENV_GET_INST_INFO()) AS T",
      db, 1
    );
    return {
      content: [{
        type: "text",
        text: JSON.stringify({
          status: "connected",
          host: DB2_HOST,
          port: DB2_PORT,
          database: db,
          serverInfo: rows[0] ?? {}
        }, null, 2),
      }],
    };
  } catch (error) {
    return {
      content: [{
        type: "text",
        text: JSON.stringify({
          status: "failed",
          host: DB2_HOST,
          database: db,
          error: error instanceof Error ? error.message : String(error)
        }, null, 2),
      }],
      isError: true,
    };
  }
});

// ── Tool 2: db2_query ───────────────────────────────────────────────────────
// Executes a read-only SELECT query and returns rows as a JSON array.
// Only SELECT / WITH / VALUES statements are permitted — write operations are blocked.
server.registerTool("db2_query", {
  description: "Execute a read-only SQL SELECT query against IBM Db2. Returns rows as a JSON array.",
  inputSchema: z.object({
    sql: z.string().describe("SELECT SQL statement to execute"),
    database: z
      .enum(["demo_col", "demo_row", "repodb"])
      .optional()
      .describe("Target database. demo_col=column-store analytics, demo_row=OLTP, repodb=Genius Hub repo. Default: demo_row"),
    max_rows: z
      .number().int().min(1).max(1000)
      .optional()
      .describe("Maximum rows to return (default 100, max 1000)"),
  }),
}, async ({ sql, database, max_rows }) => {
  const db = database ?? "demo_row";
  try {
    const trimmed = sql.trim().toUpperCase();
    // Safety check: only allow read statements
    if (!trimmed.startsWith("SELECT") && !trimmed.startsWith("WITH") && !trimmed.startsWith("VALUES")) {
      return {
        content: [{ type: "text", text: "Only SELECT / WITH / VALUES statements are allowed in db2_query." }],
        isError: true,
      };
    }
    const rows = await runSQL(sql, db, max_rows ?? 100);
    return {
      content: [{ type: "text", text: JSON.stringify({ rowCount: rows.length, rows }, null, 2) }],
    };
  } catch (error) {
    return {
      content: [{ type: "text", text: `Error: ${error instanceof Error ? error.message : String(error)}` }],
      isError: true,
    };
  }
});

// ── Tool 3: db2_execute ─────────────────────────────────────────────────────
// Executes data-modifying or DDL statements.
// Supports: INSERT, UPDATE, DELETE, CREATE TABLE, DROP TABLE, ALTER TABLE, CALL
server.registerTool("db2_execute", {
  description: "Execute a data-modifying SQL statement (INSERT, UPDATE, DELETE, CREATE, DROP, CALL) against IBM Db2.",
  inputSchema: z.object({
    sql: z.string().describe("SQL statement to execute"),
    database: z
      .enum(["demo_col", "demo_row", "repodb"])
      .optional()
      .describe("Target database (default: demo_row)"),
  }),
}, async ({ sql, database }) => {
  const db = database ?? "demo_row";
  try {
    const rows = await runSQL(sql, db, 0);
    return {
      content: [{ type: "text", text: JSON.stringify({ success: true, rowsAffected: rows.length }, null, 2) }],
    };
  } catch (error) {
    return {
      content: [{ type: "text", text: `Error: ${error instanceof Error ? error.message : String(error)}` }],
      isError: true,
    };
  }
});

// ── Tool 4: db2_list_tables ─────────────────────────────────────────────────
// Lists all user tables and views in a schema.
// Automatically excludes Db2 system schemas (SYS*, NULLID, SQLJ, etc.)
server.registerTool("db2_list_tables", {
  description: "List all user tables and views in a Db2 database schema.",
  inputSchema: z.object({
    database: z
      .enum(["demo_col", "demo_row", "repodb"])
      .optional()
      .describe("Target database (default: demo_row)"),
    schema: z
      .string()
      .optional()
      .describe("Filter by schema/owner name (e.g. DB2INST1). Omit for all user schemas."),
  }),
}, async ({ database, schema }) => {
  const db = database ?? "demo_row";
  try {
    const schemaFilter = schema
      ? `AND UPPER(t.TABSCHEMA) = UPPER('${schema.replace(/'/g, "''")}')`
      : `AND t.TABSCHEMA NOT LIKE 'SYS%' AND t.TABSCHEMA NOT IN ('NULLID','SQLJ','SYSCAT','SYSFUN','SYSIBM','SYSIBMADM','SYSIBMINTERNAL','SYSIBMTS','SYSPROC','SYSSTAT','SYSTOOLS')`;
    const sql = `SELECT t.TABSCHEMA, t.TABNAME, t.TYPE, t.CARD AS ROW_COUNT, t.REMARKS
                 FROM SYSCAT.TABLES t WHERE 1=1 ${schemaFilter}
                 ORDER BY t.TABSCHEMA, t.TABNAME`;
    const rows = await runSQL(sql, db, 500);
    return {
      content: [{ type: "text", text: JSON.stringify({ tableCount: rows.length, tables: rows }, null, 2) }],
    };
  } catch (error) {
    return {
      content: [{ type: "text", text: `Error: ${error instanceof Error ? error.message : String(error)}` }],
      isError: true,
    };
  }
});

// ── Tool 5: db2_describe_table ──────────────────────────────────────────────
// Returns all column definitions for a given table.
// Supports both SCHEMA.TABLE and TABLE name formats.
server.registerTool("db2_describe_table", {
  description: "Describe the columns, data types, and constraints of a Db2 table.",
  inputSchema: z.object({
    table_name: z.string().describe("Table name (e.g. EMPLOYEE or DB2INST1.EMPLOYEE)"),
    database: z
      .enum(["demo_col", "demo_row", "repodb"])
      .optional()
      .describe("Target database (default: demo_row)"),
  }),
}, async ({ table_name, database }) => {
  const db = database ?? "demo_row";
  try {
    const parts = table_name.toUpperCase().split(".");
    const schemaClause = parts.length === 2
      ? `UPPER(c.TABSCHEMA) = '${parts[0].replace(/'/g, "''")}' AND UPPER(c.TABNAME) = '${parts[1].replace(/'/g, "''")}'`
      : `UPPER(c.TABNAME) = '${parts[0].replace(/'/g, "''")}'`;
    const sql = `SELECT c.TABSCHEMA, c.TABNAME, c.COLNAME, c.COLNO, c.TYPENAME,
                        c.LENGTH, c.SCALE, c.NULLS, c.DEFAULT, c.REMARKS
                 FROM SYSCAT.COLUMNS c WHERE ${schemaClause} ORDER BY c.COLNO`;
    const rows = await runSQL(sql, db, 500);
    if (rows.length === 0) {
      return {
        content: [{ type: "text", text: `Table '${table_name}' not found in database '${db}'.` }],
        isError: true,
      };
    }
    return {
      content: [{ type: "text", text: JSON.stringify({ columnCount: rows.length, columns: rows }, null, 2) }],
    };
  } catch (error) {
    return {
      content: [{ type: "text", text: `Error: ${error instanceof Error ? error.message : String(error)}` }],
      isError: true,
    };
  }
});

// ── Tool 6: db2_get_indexes ─────────────────────────────────────────────────
// Lists all indexes defined on a table.
// Useful for understanding query performance and schema design.
server.registerTool("db2_get_indexes", {
  description: "List all indexes defined on a Db2 table.",
  inputSchema: z.object({
    table_name: z.string().describe("Table name (e.g. EMPLOYEE or DB2INST1.EMPLOYEE)"),
    database: z
      .enum(["demo_col", "demo_row", "repodb"])
      .optional()
      .describe("Target database (default: demo_row)"),
  }),
}, async ({ table_name, database }) => {
  const db = database ?? "demo_row";
  try {
    const parts = table_name.toUpperCase().split(".");
    const schemaClause = parts.length === 2
      ? `UPPER(i.TABSCHEMA) = '${parts[0].replace(/'/g, "''")}' AND UPPER(i.TABNAME) = '${parts[1].replace(/'/g, "''")}'`
      : `UPPER(i.TABNAME) = '${parts[0].replace(/'/g, "''")}'`;
    const sql = `SELECT i.INDSCHEMA, i.INDNAME, i.TABSCHEMA, i.TABNAME,
                        i.UNIQUERULE, i.INDEXTYPE, i.COLNAMES
                 FROM SYSCAT.INDEXES i WHERE ${schemaClause} ORDER BY i.INDNAME`;
    const rows = await runSQL(sql, db, 200);
    return {
      content: [{ type: "text", text: JSON.stringify({ indexCount: rows.length, indexes: rows }, null, 2) }],
    };
  } catch (error) {
    return {
      content: [{ type: "text", text: `Error: ${error instanceof Error ? error.message : String(error)}` }],
      isError: true,
    };
  }
});

// ---------------------------------------------------------------------------
// Start the MCP server
// Uses stdio transport — Bob communicates with the server via stdin/stdout.
// This is the entry point. Bob runs this file automatically via mcp.json.
// ---------------------------------------------------------------------------
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error(`[db2-mcp] Server started — ${DB2_HOST}:${DB2_PORT}/${DB2_DATABASE} | User: ${DB2_USERNAME}`);
}

main().catch((error) => {
  console.error("[db2-mcp] Fatal error:", error);
  process.exit(1);
});
