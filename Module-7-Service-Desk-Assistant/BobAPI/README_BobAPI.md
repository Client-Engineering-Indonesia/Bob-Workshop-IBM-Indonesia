# Service Desk UI using Bob's API

A working reference implementation that shows two things:

1. How to call the IBM Bob API from any web application
2. How Bob can call an external system's API and surface the result as a real-time dashboard

This folder is self-contained. You can embed the chat interface in any existing website, internal portal, or product by reusing the proxy pattern shown here.

---

## What is in this folder

| File | Purpose |
|---|---|
| `proxy.js` | Node.js server that receives chat requests, calls the Bob CLI, and calls ServiceNow |
| `snow.py` | Thin Python wrapper that makes direct ServiceNow API calls |
| `index.html` | Example chat UI with four service desk workflows |
| `dashboard.html` | Real-time ServiceNow metrics dashboard — Bob calls the ServiceNow API and renders live data |

---

## How the Bob API is used here

Bob is called as a CLI process from `proxy.js`. Each chat request triggers Bob twice:

1. Bob reads the user's message and returns structured data (intent and extracted fields)
2. After ServiceNow responds, Bob formats the result into a clean, human-readable reply

Bob never touches ServiceNow directly in this pattern. It handles reasoning and language only. A separate Python script handles all ServiceNow reads and writes.

This separation means you can swap ServiceNow for any other system without changing how Bob is called.

---

## Architecture

```
Browser (index.html)
        |
        | POST /chat  { prompt, workflow }
        v
  proxy.js  (Node.js, port 3456)
        |
        |-- Step 1: bob CLI  --> understands intent, returns JSON fields
        |-- Step 2: snow.py  --> calls ServiceNow API, returns result
        |-- Step 3: bob CLI  --> formats result into readable response
        |
        | { response: "..." }
        v
Browser renders the reply
```

For the dashboard, `proxy.js` exposes a `/api/dashboard` endpoint. The browser calls it on load and on a timer. `snow.py` fetches up to 200 recent incidents from ServiceNow and returns raw records. `dashboard.html` aggregates and renders them as live charts.

---

## How to use the IBM Bob API (Bob CLI)

Bob is called using the Bob Shell CLI. You authenticate it once using an API key, then call it from any script or application.

### Step 1: Generate an API key

**Via the CLI** (inside an authenticated Bob session):

```bash
grdapi create_api_key name=your_key_name
```

**Via the portal:** Log into your IBM Admin portal, go to account settings, and generate a new API key. Copy both the key ID and the encoded key from the response.

### Step 2: Export the key to your environment

```bash
export BOBSHELL_API_KEY="your_encoded_api_key_here"
```

You can add this to your shell profile or pass it inline when starting the proxy:

```bash
BOBSHELL_API_KEY="your_encoded_api_key_here" node ui/proxy.js
```

### Step 3: Call Bob from your application

Bob is invoked as a subprocess with a prompt. The `-y` flag skips confirmations and `-o text` returns plain text output:

```javascript
const { execFile } = require('child_process')

execFile('bob', ['-y', '-o', 'text', yourPrompt], (err, stdout) => {
  // stdout contains Bob's response
})
```

You can use this pattern in Node.js, Python, or any language that can spawn a child process. Bob returns whatever you ask for -- structured JSON, plain text, formatted markdown -- depending on how you write the prompt.

### Step 4: Optional -- MCP server integration

If Bob needs to connect to additional data platforms such as watsonx, add the endpoint to Bob's MCP settings. Inside Bob, go to Settings, open MCP, and add your server configuration:

```json
"your-data-platform": {
  "type": "streamable-http",
  "url": "https://your-platform-host/mcp/",
  "headers": {
    "x-api-key": "YOUR_API_KEY",
    "username": "YOUR_USERNAME"
  },
  "disabled": false,
  "alwaysAllow": []
}
```

Save the file and refresh all servers to apply.

---

## Running the UI locally

### Prerequisites

- Node.js 18 or later
- Python 3.9 or later with `requests` installed
- IBM Bob CLI installed and authenticated
- ServiceNow credentials in a `.env` file at the project root (see `.env.example`)

### Start the server

```bash
BOBSHELL_API_KEY="your_encoded_api_key_here" node ui/proxy.js
```

Then open `http://127.0.0.1:3456` in your browser.

The dashboard is available at `http://127.0.0.1:3456/dashboard`.

---

## Embedding in your own application

The proxy exposes two endpoints you can call from any frontend:

**Chat**
```
POST http://127.0.0.1:3456/chat
Content-Type: application/json

{ "prompt": "Log a ticket for a VPN issue", "workflow": "A" }
```

Response:
```json
{ "response": "Ticket INC0012345 created..." }
```

**Dashboard data**
```
GET http://127.0.0.1:3456/api/dashboard
```

Response: a JSON array of recent ServiceNow incidents ready to aggregate and render.

You can point any webpage, React app, mobile app, or internal tool at these endpoints. The proxy, Bob, and ServiceNow stay entirely in the background.

---

## Bob's modes for building and extending this

When using Bob to extend or customise this application:

| Mode | Use it for |
|---|---|
| Ask | Describing requirements, understanding how the proxy or snow.py works |
| Plan | Designing new workflows, mapping out changes before writing code |
| Agent | Writing new tool files, modifying the proxy, adding new API integrations |

---

## Notes

- Credentials are never stored in this folder. All secrets are read from the `.env` file at the project root or from environment variables at runtime.
- The `snow.py` script reads credentials from `.env` automatically. Do not commit `.env` to version control.
- Bob handles reasoning only. It does not store conversation history or send data to ServiceNow directly.
