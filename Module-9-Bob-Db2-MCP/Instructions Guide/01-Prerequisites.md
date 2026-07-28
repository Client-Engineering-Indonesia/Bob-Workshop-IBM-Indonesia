# 01 — Prerequisites

Before building and running the Db2 MCP server, make sure the following are in place. Follow every step carefully — missing any one of these is the most common reason the setup fails.

> **What needs your action vs what Bob handles:**
> Steps 1–4 on this page require **you** to download and install software manually — Bob cannot run GUI installers or modify Windows system settings without your direct action. Once these are done, Bob handles everything else.

---

## What You Need

| Requirement | Version | Purpose |
|---|---|---|
| IBM Bob | Latest | The AI IDE that uses the MCP server |
| Node.js | v18 or later | Runs the MCP server |
| IBM Data Server Driver | 11.5+ | Allows `ibm_db` to connect to Db2 |
| IBM Db2 environment | Any | The database to connect to |

---

## 1. IBM Bob

Download and install IBM Bob from the IBM internal distribution. This module was built and tested on IBM Bob with MCP support enabled.

---

## 2. IBM Db2 Environment

You need access to an IBM Db2 instance. This module was built using an **IBM TechZone** reservation:

- **Db2 version:** v12.1.5.0 (Linux x86-64)
- **Databases available:** `demo_col`, `demo_row`, `repodb`
- **Console (Genius Hub):** accessible via `https://<VM_IP>:<CONSOLE_PORT>`

> If you are using a different Db2 environment, the server will still work — just update the connection details in `mcp.json`.

---

## 3. Node.js (v18 or later)

> ⚠️ **You need to do this manually** — download and run the installer yourself. Bob cannot run GUI installers.

The MCP server is a Node.js application.

### Check if Node.js is already installed
Open a terminal (PowerShell or Command Prompt) and run:
```bash
node --version
```

You should see something like `v18.20.0` or `v20.11.0`. If you get an error, Node.js is not installed.

### Install Node.js — step by step
1. Go to: https://nodejs.org
2. Click **"LTS"** (the left green button — recommended for most users)
3. Run the downloaded `.msi` file
4. Click **Next** through all screens — keep all default options
5. On the screen that says **"Tools for Native Modules"** — check the box ✅ (this installs build tools needed for `ibm_db`)
6. Click **Install** — Windows may ask for admin approval, click **Yes**
7. Wait for it to finish, then click **Finish**

### Verify after install
Close your terminal, open a **new** one, and run:
```bash
node --version
npm --version
```

Both should print version numbers. If they do, Node.js is ready.

---

## 4. IBM Db2 ODBC/CLI Driver

> ⚠️ **You need to do this manually** — this requires downloading a zip, extracting it, and setting a Windows environment variable. Bob cannot do this without your action.

This is the most important and most commonly missed step. The `ibm_db` npm package is a **native module** — it needs IBM's Db2 C driver installed on your machine to compile and run.

### Step 4a — Download the IBM Data Server Driver Package

1. Go to: https://www.ibm.com/support/pages/ibm-data-server-driver-package-windows
2. Download **IBM Data Server Driver Package (Windows/x86-64)**
3. The file will be named something like `ibm_data_server_driver_package_win64_v11.5.zip`

### Step 4b — Extract the Driver

1. Right-click the downloaded zip → click **"Extract All..."**
2. Set the destination path to: `C:\IBM\IBM_DATA_SERVER_DRIVER`
3. Click **Extract**
4. Do **not** put it in Downloads or a temp folder — it must stay in this location permanently

After extracting, you should see:
```
C:\IBM\IBM_DATA_SERVER_DRIVER\
├── bin\
├── lib\
├── include\
├── cfg\
└── ...
```

### Step 4c — Set the Environment Variable

> ⚠️ **You need to click through Windows System Settings for this step.**

1. Press **Windows key** → type **"environment variables"** → click **"Edit the system environment variables"**
2. Click the **"Environment Variables..."** button (bottom right)
3. Under **"System variables"** (bottom half of the window) → click **"New"**
4. Fill in:
   - **Variable name:** `IBM_DB_HOME`
   - **Variable value:** `C:\IBM\IBM_DATA_SERVER_DRIVER`
5. Click **OK**
6. Still in System variables → find **"Path"** → click **"Edit"**
7. Click **"New"** → type: `C:\IBM\IBM_DATA_SERVER_DRIVER\bin`
8. Click **OK** → **OK** → **OK** (close all dialogs)

### Step 4d — Restart Your Terminal

> ⚠️ **This step is required** — environment variables only take effect in new terminal windows.

Close **all** open terminals, PowerShell windows, and Bob. Open a new terminal.

### Step 4e — Verify

Run:
```bash
echo $env:IBM_DB_HOME
```

You should see: `C:\IBM\IBM_DATA_SERVER_DRIVER`

If you see a blank line, the variable was not set — repeat Step 4c.

---

## 5. Verify ibm_db Installs Correctly

Before building the full project, do a quick test:

```bash
mkdir test-ibmdb
cd test-ibmdb
npm init -y
npm install ibm_db
```

**Expected output:** You should see the package download and compile successfully with no errors.

### Common Errors and Fixes

| Error | Cause | Fix |
|---|---|---|
| `IBM_DB_HOME is not set` | Environment variable missing | Repeat Step 4c and restart terminal |
| `Cannot find module 'ibm_db'` | Install failed silently | Delete `node_modules`, re-run `npm install ibm_db` |
| `node-gyp rebuild failed` | Missing build tools | Install Visual Studio Build Tools (see below) |
| `MSBUILD : error MSB3428` | C++ compiler missing | Install Visual Studio Build Tools (see below) |

### If you get a node-gyp / build tools error

Install the Windows build tools:
```bash
npm install --global windows-build-tools
```

Or install **Visual Studio Build Tools 2022** from:
https://visualstudio.microsoft.com/visual-cpp-build-tools/

During install, select **"Desktop development with C++"** workload. Then retry `npm install ibm_db`.

---

## 6. Connection Details

Have the following information ready from your Db2 environment:

| Item | Description | Example |
|---|---|---|
| `DB2_HOST` | VM IP address of the Db2 server | `<YOUR_VM_IP>` |
| `DB2_PORT` | Db2 TCP port | `25010` |
| `DB2_USERNAME` | Db2 login username | `db2demo` |
| `DB2_PASSWORD` | Db2 login password | `<YOUR_PASSWORD>` |
| `DB2_DATABASE` | Default database name | `DEMO_COL` |
| `DB2_CONSOLE_PORT` | Genius Hub console port | `11101` |

> **Note:** The SSH key and API key from your TechZone reservation are for accessing the VM via SSH or the Genius Hub web UI. They are **not** needed for the MCP server connection.

---

## Summary Checklist

Go through this list before moving to the next step:

- [ ] IBM Bob installed and running
- [ ] IBM Db2 environment reserved and the VM is running
- [ ] Node.js v18+ installed — `node --version` prints a version
- [ ] npm installed — `npm --version` prints a version
- [ ] IBM Data Server Driver extracted to `C:\IBM\IBM_DATA_SERVER_DRIVER`
- [ ] `IBM_DB_HOME` environment variable set
- [ ] `IBM_DATA_SERVER_DRIVER\bin` added to PATH
- [ ] Terminal restarted after setting environment variables
- [ ] `npm install ibm_db` completes without errors
- [ ] Connection details (host, port, username, password) on hand

**All boxes checked?** Proceed to **[02-Build-MCP-Server.md](02-Build-MCP-Server.md)**.
