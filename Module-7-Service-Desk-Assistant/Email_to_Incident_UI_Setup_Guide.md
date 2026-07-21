# EmailToIncident Flow — Complete Implementation Guide

> **AI-Powered Email-to-Incident Automation using IBM watsonx Orchestrate**
>
> **Stack:** IBM watsonx Orchestrate (GUI) · watsonx Discovery (Elasticsearch) · ServiceNow · Gmail  
> **Primary Approach:** Pre-built Agents + Agentic Workflow via Orchestrate GUI  
> **Backup Approach:** Custom Python ADK (see Section 8)

---

> **📌 IMPORTANT NOTE**
>
> IBM TechZone instances (watsonx Orchestrate & watsonx Discovery) and a ServiceNow developer instance will be provided by the team.
>
> - **You only need to set up credentials/connections** for the provided instances — you do not need to provision new ones.
> - The `retrieve_resolution_notes` tool is the only component built via the Python ADK. All other steps use the Orchestrate GUI with pre-built connectors.
> - Complete **Section 1 → Section 7** in order before testing end-to-end.

---

## Table of Contents

1. [Solution Architecture](#1-solution-architecture)
2. [Prerequisites & Accounts](#2-prerequisites--accounts)
3. [Setting Up Credentials](#3-setting-up-credentials)
   - 3.1 [Gmail — Google OAuth2 Credentials](#31-gmail--google-oauth2-credentials)
   - 3.2 [ServiceNow — OAuth2 Application Registry](#32-servicenow--oauth2-application-registry)
4. [Configuring Connections in watsonx Orchestrate](#4-configuring-connections-in-watsonx-orchestrate)
   - 4.1 [Gmail — google_ibm_184bdbd3](#41-gmail--google_ibm_184bdbd3)
   - 4.2 [ServiceNow — servicenow_ibm_184bdbd3](#42-servicenow--servicenow_ibm_184bdbd3)
5. [Testing Pre-built Tools Individually](#5-testing-pre-built-tools-individually)
   - 5.1 [Test Gmail — List Emails in Gmail](#51-test-gmail--list-emails-in-gmail)
   - 5.2 [Test ServiceNow — Create an Incident](#52-test-servicenow--create-an-incident)
6. [Building the retrieve_resolution_notes Tool (ADK)](#6-building-the-retrieve_resolution_notes-tool-adk)
7. [Building the Agentic Workflow](#7-building-the-agentic-workflow)
   - 7.1 [Create a New Flow](#71-create-a-new-flow)
   - 7.2 [Step 1 — List Emails in Gmail](#72-step-1--list-emails-in-gmail)
   - 7.3 [Step 2 — For Each Loop](#73-step-2--for-each-loop)
   - 7.4 [Step 3 — User Activity (Processing Message)](#74-step-3--user-activity-processing-message)
   - 7.5 [Step 4 — retrieve_resolution_notes Tool](#75-step-4--retrieve_resolution_notes-tool)
   - 7.6 [Step 5 — Generative Prompt (AI Classification)](#76-step-5--generative-prompt-ai-classification)
   - 7.7 [Step 6 — Create an Incident in ServiceNow](#77-step-6--create-an-incident-in-servicenow)
   - 7.8 [Step 7 — User Activity (Success Message)](#78-step-7--user-activity-success-message)
8. [Testing the Flow](#8-testing-the-flow)
   - 8.1 [Send a Test Email](#81-send-a-test-email)
   - 8.2 [Run the Flow in Draft Mode](#82-run-the-flow-in-draft-mode)
   - 8.3 [Using the Flow Inspector](#83-using-the-flow-inspector)
   - 8.4 [Validating ServiceNow Output](#84-validating-servicenow-output)
9. [Prompts Reference](#9-prompts-reference)
10. [Troubleshooting](#10-troubleshooting)
11. [Backup: Custom ADK Approach](#11-backup-custom-adk-approach)

---

## 1. Solution Architecture

### What This Flow Does

1. Monitors a Gmail inbox for emails with subject containing `"incident"`
2. For each matching email, searches watsonx Discovery for similar past resolutions
3. Passes the email body + resolutions to an LLM (GPT-OSS 120B via Groq) for classification
4. The LLM extracts structured fields: category, assignment group, impact, urgency, description
5. Creates a fully populated incident in ServiceNow automatically
6. Confirms success with the incident number back to the user

### Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    watsonx Orchestrate — Agentic Flow               │
│                                                                     │
│  [Start] → [List Emails in Gmail] → [For Each Email]                │
│                                           │                         │
│                              ┌────────────▼──────────────────┐      │
│                              │  LOOP (per email)             │      │
│                              │                               │      │
│                              │  1. User Activity (notify)    │      │
│                              │  2. retrieve_resolution_notes │      │
│                              │     (watsonx Discovery/ES)    │      │
│                              │  3. Generative Prompt         │      │
│                              │     (GPT-OSS 120B via Groq)   │      │
│                              │  4. Create Incident           │      │
│                              │     (ServiceNow pre-built)    │      │
│                              │  5. User Activity (success)   │      │
│                              └───────────────────────────────┘      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

External Systems:
  Gmail API ←→ [List Emails in Gmail] pre-built tool
  watsonx Discovery (Elasticsearch) ←→ [retrieve_resolution_notes] custom tool
  ServiceNow REST API ←→ [Create Incident] pre-built tool
```

### Component Summary

| Component | Type | Where Built |
|---|---|---|
| List Emails in Gmail | Pre-built Tool | Orchestrate GUI (Connections) |
| retrieve_resolution_notes | Custom Tool | Python ADK (Section 6) |
| Generative Prompt | Built-in Node | Orchestrate Flow Builder |
| Create Incident in ServiceNow | Pre-built Tool | Orchestrate GUI (Connections) |

---

## 2. Prerequisites & Accounts

Before starting, confirm you have access to:

| Requirement | Details |
|---|---|
| IBM watsonx Orchestrate instance | Provided by team (TechZone) |
| watsonx Discovery / Elasticsearch | Provided by team (TechZone) |
| ServiceNow Developer Instance | Provided by team OR create free at developer.servicenow.com |
| Gmail Account | Personal Gmail account with 2-Step Verification enabled |
| Python 3.11+ | For building the `retrieve_resolution_notes` ADK tool only |

---

## 3. Setting Up Credentials

> **Important:** watsonx Orchestrate connects to both Gmail and ServiceNow using **OAuth2 Authorization Code** flow — not IMAP or Basic Auth. You will need to create OAuth2 application credentials in both Google Cloud Console and ServiceNow before configuring the connections in Orchestrate.

---

### 3.1 Gmail — Google OAuth2 Credentials

You need a **Google Cloud Project** with the Gmail API enabled, plus an OAuth2 Client ID and Secret.

#### Step 1 — Create a Google Cloud Project

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Click the project dropdown (top left) → **New Project**
3. Enter a name (e.g., `watsonx-orchestrate-gmail`) → click **Create**
4. Make sure the new project is selected in the dropdown

#### Step 2 — Enable the Gmail API

1. In the left menu go to **APIs & Services → Library**
2. Search for `Gmail API`
3. Click **Gmail API** → click **Enable**

#### Step 3 — Configure the OAuth Consent Screen

1. Go to **APIs & Services → OAuth consent screen**
2. Select **External** → click **Create**
3. Fill in:
   - App name: `watsonx Orchestrate`
   - User support email: your Gmail address
   - Developer contact email: your Gmail address
4. Click **Save and Continue** through the remaining screens (Scopes and Test users can be left default for now)
5. Click **Back to Dashboard**
6. Go to **Audience** → **Test users**
7. Add your Gmail address  → Save

#### Step 4 — Create OAuth2 Credentials

1. Go to **APIs & Services → Credentials**
2. Click **+ Create Credentials → OAuth client ID**
3. Application type: **Web application**
4. Name: `watsonx-orchestrate-client`
5. Under **Authorized redirect URIs**, click **+ Add URI** and enter:
   ```
   https://iam.cloud.ibm.com/identity/oauth/callback
   https://us-south.watson-orchestrate.cloud.ibm.com/mfe_connectors/api/v1/agentic/oauth/_callback
   ```
   > This is the IBM Cloud OAuth callback URL that Orchestrate uses to complete the OAuth flow.
6. Click **Create**
7. A dialog will show your credentials — **copy and save both values immediately:**

```
Client ID:      xxxxxxxxxxxxxxxx.apps.googleusercontent.com
Client Secret:  GOCSPX-xxxxxxxxxxxxxxxxxxxxxxxx
```

#### Credentials Summary (Gmail)

```
Authentication type:   OAuth2 Authorization Code
Server URL:            https://gmail.googleapis.com/
Token URL:             https://oauth2.googleapis.com/token
Authorization URL:     https://accounts.google.com/o/oauth2/v2/auth
Client ID:             (from Step 4 above)
Client Secret:         (from Step 4 above)
Scope:                 https://mail.google.com/
Token request field:   prompt = consent
Auth request fields:   base_url = https://gmail.googleapis.com/
                       access_type = offline
```

---

### 3.2 ServiceNow — OAuth2 Application Registry

You need to create an **OAuth Application** inside your ServiceNow instance to get a Client ID and Secret.

#### Option A: Using Team-Provided Instance

The team will provide the ServiceNow instance URL and OAuth credentials. Collect:
```
Instance URL:   https://devXXXXX.service-now.com
Client ID:      (provided)
Client Secret:  (provided)
```
Skip to Section 4.

#### Option B: Creating OAuth Credentials on Your Own Instance

**Step 1 — Get a ServiceNow Developer Instance (if not already done):**

1. Go to [developer.servicenow.com](https://developer.servicenow.com)
2. Sign up / log in → click **Start Building**
3. Request an instance and note your URL: `https://devXXXXX.service-now.com`

**Step 2 — Create an OAuth Application Registry:**

1. Log in to your ServiceNow instance as `admin`
2. In the search bar at the top, type `Application Registry` → click **System OAuth → Application Registry**
3. Click **New**
4. Select **New Inbound Integration Experience**
5. Click **New Integration**
6. Select **OAuth - Authorization code grant.**
7. Fill in:
   - Name: `watsonx_orchestrate`
   - Provider name: `watsonx_orchestrate`
   - Redirect URL: 
     ```
     https://us-south.watson-orchestrate.cloud.ibm.com/mfe_connectors/api/v1/agentic/oauth/_callback
     ```
   - Copy "Client ID" and "Client Secret" from the form before submitting.
   - Active: ✅ checked
   - Auth scope: useraccount
8. Click **Save**

```
Client ID:      (auto-generated, visible in the record)
Client Secret:  (auto-generated — click the lock icon to reveal)
```

#### Credentials Summary (ServiceNow) for watsonx Orchestrate

```
Authentication type:  OAuth2 Authorization Code
Server URL:           https://devXXXXX.service-now.com
Token URL:            https://devXXXXX.service-now.com/oauth_token.do
Authorization URL:    https://devXXXXX.service-now.com/oauth_auth.do
Client ID:            (from Application Registry)
Client Secret:        (from Application Registry)
Scope:                useraccount
Credential type:      Member credentials
```

---

## 4. Configuring Connections in watsonx Orchestrate

> **How connections work in Orchestrate:**  
> Pre-built tools (Gmail, ServiceNow) come with **pre-set connections** already attached — named `google_ibm_184bdbd3` and `servicenow_ibm_184bdbd3`. You do **not** create new connections. You simply open the existing connection, fill in your **Client ID and Client Secret**, and authorise via OAuth. Each connection has a **Draft tab** (for testing flows) and a **Live tab** (for production) — both must be configured.

**How to reach a connection:**  
Open any tool (e.g., **List emails in Gmail**) → click the **Connectors** tab → click the **edit pencil** (✏️) on the connection row.

---

### 4.1 Gmail — `google_ibm_184bdbd3`

#### Draft tab

1. Open **List emails in Gmail** → click **Connectors** tab
2. Click the **edit pencil** on the Google / `google_ibm_184bdbd3` row
3. Make sure the **Draft** tab is selected
4. The following fields are already pre-filled by IBM — **do not change them:**

| Field | Pre-filled value |
|---|---|
| Authentication type | `OAuth2 Authorization Code` |
| Server URL | `https://gmail.googleapis.com/` |
| Token URL | `https://oauth2.googleapis.com/token` |
| Authorization URL | `https://accounts.google.com/o/oauth2/v2/auth` |
| Scope | `https://mail.google.com/` |
| Token request field: `prompt` | `consent` |
| Auth request field: `base_url` | `https://gmail.googleapis.com/` |
| Auth request field: `access_type` | `offline` |

5. **Fill in only these two fields** with your Google OAuth credentials from Section 3.1:

| Field | Your value |
|---|---|
| Client ID | *(paste your Google OAuth Client ID)* |
| Client Secret | *(paste your Google OAuth Client Secret)* |

6. **Credential type:** confirm **Member credentials** is selected
7. Click **Save changes**

#### Authorise the Draft connection

After saving, you must complete the OAuth handshake:

1. You will see a **Connect** button appear — click it
2. A Google sign-in popup opens — sign in with the Gmail account the flow will read emails from
3. Google shows a permissions screen — click **Allow**
4. You are redirected back to Orchestrate
5. The Draft column should now show a green ✅ **OAuth2 (Authorization Code)**

#### Live tab

1. Click the **Live** tab in the same connection panel
2. Fill in the **same Client ID and Client Secret** as the Draft tab
3. All other fields are pre-filled — do not change them
4. Click **Save changes**
5. Click **Connect** → sign in with the same Gmail account → Allow
6. The Live column should show a green ✅

> Both Draft and Live must be independently authorised. The flow will fail in whichever environment has not been authorised.

---

### 4.2 ServiceNow — `servicenow_ibm_184bdbd3`

#### Draft tab

1. Open **Create an incident in ServiceNow** → click **Connectors** tab
2. Click the **edit pencil** on the ServiceNow / `servicenow_ibm_184bdbd3` row
3. Make sure the **Draft** tab is selected
4. The following fields are pre-filled — **update only the Server URL and credential fields:**

| Field | Value |
|---|---|
| Authentication type | `OAuth2 Authorization Code` *(pre-filled, do not change)* |
| Server URL | `https://devXXXXX.service-now.com` ← **update to your instance URL** |
| Token URL | `https://devXXXXX.service-now.com/oauth_token.do` ← **update to your instance** |
| Authorization URL | `https://devXXXXX.service-now.com/oauth_auth.do` ← **update to your instance** |
| Scope | `useraccount` |
| Token request field | *(leave empty)* |
| Auth request field | *(leave empty)* |

5. **Fill in only these two fields** with your ServiceNow OAuth credentials from Section 3.2:

| Field | Your value |
|---|---|
| Client ID | *(paste your ServiceNow OAuth Client ID)* |
| Client Secret | *(paste your ServiceNow OAuth Client Secret)* |

6. **Credential type:** confirm **Member credentials** is selected
7. Click **Save changes**

#### Authorise the Draft connection

1. Click **Connect**
2. A ServiceNow login popup opens — sign in with your ServiceNow admin credentials
3. ServiceNow asks to allow access — click **Allow**
4. You are redirected back to Orchestrate
5. Draft column shows green ✅ **OAuth2 (Authorization Code)**

> If the ServiceNow instance has hibernated, the popup will time out. Open `https://devXXXXX.service-now.com` in a separate browser tab first to wake it, then retry.

#### Live tab

1. Click the **Live** tab
2. Fill in the same **Server URL, Token URL, Authorization URL, Client ID, and Client Secret**
3. Click **Save changes**
4. Click **Connect** → sign in to ServiceNow → Allow
5. Live column shows green ✅

#### What a correctly configured Connectors tab looks like

Once both connections are fully set up, the **Connectors** tab on any Gmail or ServiceNow tool should show:

| Connections | Draft | Live |
|---|---|---|
| Google / `google_ibm_184bdbd3` | ✅ OAuth2 (Authorization Code) — Member credentials | ✅ OAuth2 (Authorization Code) — Member credentials |
| ServiceNow / `servicenow_ibm_184bdbd3` | ✅ OAuth2 (Authorization Code) — Member credentials | ✅ OAuth2 (Authorization Code) — Member credentials |

---

## 5. Testing Pre-built Tools Individually

Before building the flow, verify each tool works correctly in isolation. Tools in watsonx Orchestrate do not need to be "activated" — once the connection credentials are saved and authorised (Section 4), they are ready to use. Test each one from its **Parameters** tab.

---

### 5.1 Test Gmail — List Emails in Gmail

1. In Orchestrate, go to **Tools** (left navigation)
2. Search for and open **List emails in Gmail**
3. Click the **Parameters** tab
4. Click **Try it** or use the test panel to enter values:

| Parameter | Test value |
|---|---|
| `limit` | `3` |
| `subject` | `incident` |
| `to_address` | `your-email@gmail.com` |

5. Click **Run** (Draft mode)
6. **Expected output:** A JSON object with an `emails` array. Each item contains:
   - `body` — full email text
   - `subject` — email subject line
   - `from_address` — sender email
   - `date` — received date
   - `id` — email ID

If you get an `emails` array back, the Gmail connection is working correctly.

> If you get an auth error, return to Section 4.1 and re-authorise the Draft connection.

---

### 5.2 Test ServiceNow — Create an Incident

1. In Orchestrate, go to **Tools**
2. Search for and open **Create an incident in ServiceNow**
3. Click the **Parameters** tab
4. Enter test values:

| Parameter | Test value |
|---|---|
| `short_description` | `Test incident from watsonx Orchestrate` |
| `description` | `This is a connectivity test — safe to delete` |
| `caller_username` | `admin` |
| `impact_value` | `3` |
| `urgency_value` | `3` |

5. Click **Run** (Draft mode)
6. **Expected output:** A JSON object containing `incident_number` (e.g., `INC0010001`)
7. Log in to `https://devXXXXX.service-now.com` and verify the incident appears under **Incident → All**

If you see an incident number and it appears in ServiceNow, the tool is working.

> If the test fails with an auth error, return to Section 4.2 and re-authorise the Draft connection. If it fails with a 404 or instance error, the ServiceNow PDI may have hibernated — log in to the instance URL directly to wake it, then retry.

---

## 6. Building the retrieve_resolution_notes Tool (ADK)

This is the only component built with the Python ADK. It connects to watsonx Discovery (Elasticsearch) to find similar past resolutions for a given incident description.

> The full setup steps for this tool are documented by the ADK team. Follow those instructions to import and activate the tool in your Orchestrate instance. The key inputs and outputs are described below for reference when mapping data in the flow.

**Tool Inputs:**

| Parameter | Type | Description |
|---|---|---|
| `incident_description` | string | The email body text to search against |
| `top_k` | integer | Number of results to return (recommended: 5) |

**Tool Outputs:**

| Output | Type | Description |
|---|---|---|
| `resolutions` | array | List of similar resolution objects from the knowledge base |
| `total_retrieved` | integer | Count of results returned |

**Each resolution object contains fields such as:**
- `category`
- `resolution_notes`
- `resolution_type`
- `priority`
- `relevance_score`
- `incident_type`
- `detailed_description`

Once the ADK team has imported the tool, verify it appears in **Tools** in your Orchestrate instance before proceeding to Section 7.

---

## 7. Building the Agentic Workflow

Now build the complete flow in the Orchestrate GUI. Navigate to **Flows** → **Create Flow** → name it `EmailToIncident_flow`.

---

### 7.1 Create a New Flow

1. In Orchestrate, click **Flows** in the left navigation
2. Click **Create flow** (top right)
3. Enter:
   - Name: `EmailToIncident_flow`
   - Description: `Monitors Gmail for incident emails, classifies them using AI, and logs to ServiceNow`
4. Click **Create**

You will land in the **Flow Builder** canvas with a Start node and an End node.

---

### 7.2 Step 1 — List Emails in Gmail

1. Click the **+** button between Start and End
2. Search for and select **List emails in Gmail**
3. Click the node → click **Edit data mapping**
4. Map the inputs:

| Field | Value | How |
|---|---|---|
| `limit` | `10` | Type directly |
| `subject` | `"incident"` | Click `</>` and type the string in quotes |
| `to_address` | `your-email@gmail.com` | Type directly |
| `next_page_token` | *(leave blank)* | — |

5. Click **Save**

> The `subject` filter ensures only relevant emails are picked up. `"incident"` is case-insensitive and will match subjects like "Incident Report", "INCIDENT", "New incident raised", etc. Adjust to a more specific keyword later if needed.

---

### 7.3 Step 2 — For Each Loop

The Gmail tool returns a list of emails. Use a **For Each** loop to process each one individually.

1. Click **+** after the Gmail node
2. Select **For each** (under Control Flow)
3. In the For Each panel on the right:
   - **Select a list:** click the field → select `tool_output.emails` (the output from the Gmail step)
   - **Iterator variable:** this is automatically set to `current item`
   - **Index variable:** automatically set to `index`
4. All subsequent steps (7.4 through 7.8) will be added **inside** this loop

---

### 7.4 Step 3 — User Activity (Processing Message)

Add a display message inside the loop so users can see progress.

1. Inside the For Each loop, click **+** → select **User activity**
2. Inside the User activity, click **+** → select **Display message**
3. In the Message panel, compose the output message:
   - Type: `Processing email `
   - Click **{x}** → select `index` variable chip
   - Type: `: `
   - Click **{x}** → select `current_item.subject` variable chip
4. The message should read: `Processing email [index] : [current_item.subject]`
5. Click **Save**

---

### 7.5 Step 4 — retrieve_resolution_notes Tool

1. Inside the For Each loop (after User activity), click **+**
2. Search for and select **retrieve_resolution_notes**
3. Click **Edit data mapping**
4. Map inputs:

| Field | Value | How |
|---|---|---|
| `incident_description` | `current_item.body` | Click **{x}** → select from dropdown |
| `top_k` | `5` | Click **{#}** and type `5` |

5. Click **Save**

---

### 7.6 Step 5 — Generative Prompt (AI Classification)

This is the core classification step.

1. Inside the For Each loop, click **+** → select **Generative prompt**
2. The Generative Prompt editor will open

#### Configure the Model

- In the top right, set **Model** to `GPT-OSS 120B — OpenAI (via Groq)`

#### Add Input Variables

In the left **Input** panel, click **Add +** to register the three variables the prompt will use:

| Variable Name | Type |
|---|---|
| `Incident_description` | abc (string) |
| `resolutions` | abc (string) |
| `total_retrieved` | 123 (number) |

#### Map Input Variables

Click **Edit data mapping** (bottom of Input panel) and map:

| Variable | Source | How |
|---|---|---|
| `Incident_description` | `current_item.body` | Click **{x}** → select |
| `resolutions` | `retrieve_resolution_notes.resolutions` | Click **{x}** → select from dropdown |
| `total_retrieved` | `retrieve_resolution_notes.total_retrieved` | Click **{x}** → select |

#### Enter the System Prompt

Click into the **System prompt** text area and paste:

```
You are an expert IT Service Management (ITSM) analyst. Your job is to classify IT incidents by analyzing the original email description alongside historical resolution data retrieved from a knowledge base.

You will receive:
1. The raw incident email body
2. A list of similar past resolutions (from watsonx Discovery) as a JSON string
3. The total count of similar resolutions found

Using all three inputs, extract and classify the incident into a structured output with these fields:
- caller_username: infer from email sender name/signature if present, else "unknown"
- short_description: a concise 1-line summary (max 15 words)
- description: cleaned full incident description, removing email formatting/greetings
- incident_category: one of [Hardware, Software, Network, Access & Identity, Security, Service Request, Other]
- assignment_group: most appropriate support team based on category and resolution patterns (e.g., "Network Operations", "End User Computing", "Identity & Access Management", "Security Operations", "Application Support")
- impact_value: one of [1 - High, 2 - Medium, 3 - Low] — infer from urgency language and resolution patterns
- urgency_value: one of [1 - High, 2 - Medium, 3 - Low] — infer from time-sensitivity language in email

Base your classification on both the email content AND patterns observed in the similar resolutions. If resolutions consistently point to a specific team or category, weight that heavily.

Always respond ONLY with a valid JSON object matching the output schema. No preamble, no explanation, no markdown code blocks.
```

#### Enter the User Prompt

Click into the **User prompt** text area. You must **insert variable chips inline** — do not paste the variable names as plain text.

Type and insert as follows:

1. Type: `Classify the following IT incident using the email body and knowledge base context below.`
2. Press Enter twice
3. Type: `--- EMAIL BODY ---`
4. Press Enter
5. Click **{x}** → select **`Incident_description`** (the chip will appear inline)
6. Press Enter twice
7. Type: `--- SIMILAR RESOLUTIONS FROM KNOWLEDGE BASE ---`
8. Press Enter
9. Click **{x}** → select **`resolutions`** (chip appears inline)
10. Press Enter twice
11. Type: `--- NUMBER OF SIMILAR RESOLUTIONS FOUND ---`
12. Press Enter
13. Click **{x}** → select **`total_retrieved`** (chip appears inline)
14. Press Enter twice
15. Type the following JSON template exactly:

```
Based on the above, return ONLY this JSON object with no explanation:
{
  "caller_username": "",
  "short_description": "",
  "description": "",
  "incident_category": "",
  "assignment_group": "",
  "impact_value": "",
  "urgency_value": ""
}
```

> **Critical:** The three variable chips (`Incident_description`, `resolutions`, `total_retrieved`) must appear as blue pill tokens **inside** the prompt body — not floating above it. If they appear only in the Input panel on the left but not inline in the text, the model will receive no data and return empty values.

#### Configure Output as Object

1. Toggle **Output as Object** to ON (green)
2. Click **Edit object**
3. In the Simple view, set:
   - **Name:** `output_gen`
   - Click **Add +** and add each property:

| Property Name | Type |
|---|---|
| `caller_username` | String |
| `short_description` | String |
| `description` | String |
| `incident_category` | String |
| `assignment_group` | String |
| `impact_value` | String |
| `urgency_value` | String |

4. Click **Save**

#### Generate a Preview

1. In the left Input panel, enter a test value for `Incident_description`:
   ```
   Hi, this is an email regarding an Outlook incident which is severely affecting users of IBM Org. Many Thanks & Regards, Naresh
   ```
2. Click **Generate Preview** (bottom right)
3. You should see a populated JSON object on the right side with all 7 fields filled

---

### 7.7 Step 6 — Create an Incident in ServiceNow

1. Inside the For Each loop, click **+** → select **Create an incident in ServiceNow**
2. Click **Edit data mapping**
3. Map each field from `output_gen` (the Generative Prompt output):

| ServiceNow Field | Source Variable | How |
|---|---|---|
| `caller_username` | `output_gen.caller_username` | Click **{x}** → select |
| `short_description` | `output_gen.short_description` | Click **{x}** → select |
| `description` | `output_gen.description` | Click **{x}** → select |
| `incident_category` | `output_gen.incident_category` | Click **{x}** → select |
| `assignment_group` | `output_gen.assignment_group` | Click **{x}** → select |
| `impact_value` | `output_gen.impact_value` | Click **{x}** → select |
| `urgency_value` | `output_gen.urgency_value` | Click **{x}** → select |
| `current_run` | *(leave as Child attributes mapped)* | — |

4. Click **Save**

> The `current_run` field is an internal AgentRun wrapper — leave it blank or with its auto-mapped value.

---

### 7.8 Step 7 — User Activity (Success Message)

Add a final confirmation message showing the ServiceNow incident number.

1. Inside the For Each loop (after the ServiceNow step), click **+** → select **User activity**
2. Inside User activity, click **+** → select **Display message**
3. Compose the message:
   - Type: `Incident Lodged Successfully: `
   - Click **{x}** → select `tool_output.incident_number`
4. The message will read: `Incident Lodged Successfully: INC0010XXX`
5. Click **Save**

Your complete flow now looks like:

```
[Start]
  └─ [List Emails in Gmail]
       └─ [For Each: tool_output.emails]
            ├─ [User Activity 1: Processing email {index}: {subject}]
            ├─ [retrieve_resolution_notes]
            ├─ [Generative Prompt: AI Classification]
            ├─ [Create an Incident in ServiceNow]
            └─ [User Activity 2: Incident Lodged Successfully: {incident_number}]
[End]
```

---

## 8. Testing the Flow

### 8.1 Send a Test Email

Send a test email to the Gmail account configured in your connection.

**Example test email:**

```
To: your-email@gmail.com
Subject: incident - Outlook not working

Hi Team,

I am unable to access Microsoft Outlook since this morning. The application 
crashes immediately on launch. This is affecting my ability to receive 
critical client communications.

Error message: "Cannot start Microsoft Outlook. Cannot open the Outlook window."

Please treat this as urgent as I have a client presentation in 2 hours.

Many Thanks & Regards,
Naresh Olladapu
```

Wait 1–2 minutes for the email to arrive in the inbox.

---

### 8.2 Run the Flow in Draft Mode

1. In the Flow Builder, click **Run** or **Test** (top right)
2. Select **Draft** environment
3. The flow will start executing — you will see progress in the right panel
4. When it reaches **User Activity 1**, the flow pauses and asks you to confirm processing
5. Click **Continue** or **Submit** to proceed
6. Watch each step execute and check for green ticks

---

### 8.3 Using the Flow Inspector

The Flow Inspector gives detailed visibility into every step's inputs and outputs.

**To open Flow Inspector:**

1. In the top right of the flow canvas, click the **three-dot menu (⋮)**
2. Select **Open flow inspector**

OR from the Orchestrate home:
1. Go to **Flows**
2. Click the **three-dot menu** next to `EmailToIncident_flow`
3. Select **Open flow inspector**

**Reading the Flow Inspector:**

The left panel shows all flow runs with their status:
- 🔵 **Waiting for user** — flow paused at a User Activity node
- 🔄 **Running** — currently executing
- ✅ **Completed** — finished successfully
- 🔴 **Failed** — error occurred

Click **View details** on any run to see:

**Flow Events tab (left panel):**
- Each step listed with timestamp and duration
- Expand any step to see its parameters
- Click a step to see its inputs and outputs on the right

**Key things to verify at each step:**

| Step | What to Check |
|---|---|
| List Emails in Gmail | `tool_output.emails` contains your test email with correct `body`, `subject`, `from_address` |
| retrieve_resolution_notes | `resolutions` is a non-empty array; `total_retrieved` > 0 |
| Generative Prompt | `output_gen` object has all 7 fields populated with meaningful values (not empty strings) |
| Create Incident in ServiceNow | `tool_output.incident_number` contains a value like `INC0010XXX` |

**Flow Parameters tab:**
- Shows the overall input/output of the entire flow run

---

### 8.4 Validating ServiceNow Output

After a successful run:

1. Log in to your ServiceNow instance: `https://devXXXXX.service-now.com`
2. Navigate to **Incident → All** (or search for the incident number from the flow output)
3. Verify the incident contains:
   - Short description populated from the email
   - Description cleaned of email greetings/formatting
   - Correct `incident_category` (e.g., Software)
   - Correct `assignment_group` (e.g., Application Support)
   - `impact_value` and `urgency_value` as numbers (1, 2, or 3)
   - `caller_username` from the email signature

---

## 9. Prompts Reference

### System Prompt (Final Version)

```
You are an expert IT Service Management (ITSM) analyst. Your job is to classify IT incidents by analyzing the original email description alongside historical resolution data retrieved from a knowledge base.

You will receive:
1. The raw incident email body
2. A list of similar past resolutions (from watsonx Discovery) as a JSON string
3. The total count of similar resolutions found

Using all three inputs, extract and classify the incident into a structured output with these fields:
- caller_username: infer from email sender name/signature if present, else "unknown"
- short_description: a concise 1-line summary (max 15 words)
- description: cleaned full incident description, removing email formatting/greetings
- incident_category: one of [Hardware, Software, Network, Access & Identity, Security, Service Request, Other]
- assignment_group: most appropriate support team based on category and resolution patterns (e.g., "Network Operations", "End User Computing", "Identity & Access Management", "Security Operations", "Application Support")
- impact_value: one of [1 - High, 2 - Medium, 3 - Low] — infer from urgency language and resolution patterns
- urgency_value: one of [1 - High, 2 - Medium, 3 - Low] — infer from time-sensitivity language in email

Base your classification on both the email content AND patterns observed in the similar resolutions. If resolutions consistently point to a specific team or category, weight that heavily.

Always respond ONLY with a valid JSON object matching the output schema. No preamble, no explanation, no markdown code blocks.
```

### User Prompt (Final Version)

> Note: `[CHIP]` below represents an inline variable chip inserted via the `{x}` button — not plain text.

```
Classify the following IT incident using the email body and knowledge base context below.

--- EMAIL BODY ---
[CHIP: Incident_description]

--- SIMILAR RESOLUTIONS FROM KNOWLEDGE BASE ---
[CHIP: resolutions]

--- NUMBER OF SIMILAR RESOLUTIONS FOUND ---
[CHIP: total_retrieved]

Based on the above, return ONLY this JSON object with no explanation:
{
  "caller_username": "",
  "short_description": "",
  "description": "",
  "incident_category": "",
  "assignment_group": "",
  "impact_value": "",
  "urgency_value": ""
}
```

### impact_value / urgency_value Format

The ServiceNow pre-built tool may expect numeric values (`1`, `2`, `3`) rather than full label strings. If incidents are created with blank impact/urgency, update the user prompt JSON template to hint the format:

```json
"impact_value": "1 or 2 or 3 (1=High, 2=Medium, 3=Low)",
"urgency_value": "1 or 2 or 3 (1=High, 2=Medium, 3=Low)"
```

---

## 10. Troubleshooting

### Generative Prompt returns empty fields

**Cause:** Variable chips are not embedded inline in the prompt text — they are only listed in the Input panel.

**Fix:** Delete the user prompt text completely. Re-type it manually, inserting each variable chip using the **{x}** button at the correct position in the text. The chips must appear as blue pill tokens inside the prompt body.

Also check for `{self.input.` artefacts in the prompt — this is a broken auto-suggest that must be deleted.

---

### Gmail tool returns no emails

**Cause:** OAuth2 connection not authorised, token expired, or subject filter mismatch.

**Fix:**
1. Go to the Gmail tool → **Connectors** tab → check the connection shows **Connected** status
2. If it shows **Not connected**, click the edit pencil → click **Connect** → re-authorise with your Google account
3. OAuth tokens can expire — if the flow worked before but now fails, re-authorise the connection on both Draft and Live tabs
4. Check that the `subject` field value matches actual email subjects (`"incident"` is case-insensitive)
5. Test: send yourself an email with `"incident"` anywhere in the subject and run the flow again

---

### ServiceNow Create Incident fails

**Cause:** OAuth token expired, instance hibernated, or field format mismatch.

**Fix:**
1. Log in to `https://devXXXXX.service-now.com` directly — PDI instances hibernate after inactivity; click **Wake up** if prompted
2. Go to the ServiceNow tool → **Connectors** tab → re-authorise the connection if it shows **Not connected**
3. Verify `impact_value` and `urgency_value` are numeric strings (`"1"`, `"2"`, `"3"`) not label strings
4. Check that `caller_username` matches a valid user in ServiceNow — use `"admin"` for initial testing

---

### Flow stuck at "Waiting for user"

**Cause:** User Activity nodes pause the flow and require manual confirmation.

**Fix:** This is expected behaviour. Open the flow run in the Flow Inspector, click **View details**, and you will see a button to continue. For production use, consider removing User Activity 1 (the processing notification) so the loop runs automatically.

---

### Object output schema errors

**Cause:** Using the JSON view in the object editor instead of Simple view.

**Fix:** Always use **Simple view** to create new object schemas. The JSON view is for exporting already-saved objects, not creating new ones. Add fields one by one using **Add +** in Simple view.

---

### retrieve_resolution_notes returns no results

**Cause:** watsonx Discovery index is empty, or the tool is not connected to the correct index.

**Fix:**
1. Verify the Elasticsearch/watsonx Discovery instance is running
2. Confirm the resolution notes index has been populated with data (see ADK setup guide)
3. Test the tool independently with a known incident description

---

## 11. Backup: Custom ADK Approach

> This section documents the original Python ADK-based implementation. Use this only if the GUI-based approach cannot meet your requirements, or as a reference for extending the solution.

The custom ADK approach builds the same workflow using:
- Python `@tool` decorators for all tools (including Gmail IMAP and ServiceNow REST)
- YAML agent definitions for the orchestration logic
- CLI commands (`orchestrate` SDK) for deploying agents

### When to use this approach

- You need custom pre/post-processing logic not available in the GUI
- You are integrating with non-standard ServiceNow fields
- You need to batch-process large email volumes with custom retry logic
- You are running in an environment without access to the Orchestrate GUI

### Project Structure

```
Service_desk_Assistant_T3/
├── tools/
│   ├── servicenow_tools.py          # create/get/update incident
│   ├── email_tools.py               # Gmail IMAP fetch
│   ├── resolution_retrieval.py      # retrieve_resolution_notes (also used in primary)
│   └── risk_retrieval.py            # optional risk mapping
├── agents/
│   ├── incident_logging_agent.yml
│   ├── risk_mapping_agent.yml
│   └── service_desk_assistant.yml
├── scripts/
│   └── import_data.py
├── requirements.txt
└── .env
```

### Environment Variables

Create a `.env` file:

```ini
# Elasticsearch / watsonx Discovery
ES_HOST=your-elasticsearch-host.com
ES_PORT=9200
ES_USERNAME=elastic
ES_PASSWORD=your_password
ES_CERT_CONTENT="-----BEGIN CERTIFICATE----- ... -----END CERTIFICATE-----"
ES_USE_SSL=true
ES_VERIFY_CERTS=false

# IBM watsonx Orchestrate
WATSONX_ORCHESTRATE_URL=https://your-instance.ibm.com
WXO_APIKEY=your_api_key

# ServiceNow
SNOW_INSTANCE_URL=https://devXXXXX.service-now.com
SNOW_USERNAME=svc_ai_integration
SNOW_PASSWORD=your_password

# Gmail IMAP
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
IMAP_USE_SSL=true
IMAP_USERNAME=servicedesk@gmail.com
IMAP_PASSWORD=your_16_char_app_password
```

### Installation

```bash
cd Service_desk_Assistant_T3
python3 -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Deploying Tools

```bash
# Activate Orchestrate environment
orchestrate env activate servicedesk_assistant --api-key $WXO_APIKEY

# Import tools
orchestrate tools import -k tools/resolution_retrieval.py
orchestrate tools import -k tools/servicenow_tools.py
orchestrate tools import -k tools/email_tools.py

# Import agents
orchestrate agents import -f agents/incident_logging_agent.yml
orchestrate agents import -f agents/service_desk_assistant.yml
```

### Tool Pattern Reference

```python
from pydantic import Field
from ibm_watsonx_orchestrate.agent_builder.tools import tool

@tool(
    name="my_tool",
    description="What this tool does"
)
def my_tool(
    param1: str = Field(..., description="Parameter description")
) -> dict:
    try:
        # Tool logic
        return {"success": True, "result": "..."}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### Agent YAML Pattern Reference

```yaml
spec_version: v1
style: default
name: service_desk_assistant
llm: watsonx/meta-llama/llama-3-2-90b-vision-instruct

description: >
  Main orchestrator for end-to-end email-to-incident workflow

instructions: >
  ## Role
  You are a service desk automation agent.
  
  ## Workflow
  1. Fetch unread emails with subject containing "incident"
  2. For each email, retrieve similar past resolutions
  3. Create a ServiceNow incident with AI-classified fields
  4. Confirm the incident number to the user

tools:
  - fetch_service_desk_emails
  - retrieve_resolution_notes
  - create_servicenow_incident
  - get_servicenow_incident
  - update_servicenow_incident
```

### Troubleshooting (ADK)

| Error | Fix |
|---|---|
| Tool import fails | Set `PYTHONPATH="${PWD}:${PYTHONPATH}"` before running import |
| Agent import fails | Validate YAML syntax; ensure tools are imported first |
| Elasticsearch connection refused | Check `ES_HOST` has no `https://` prefix; set `ES_VERIFY_CERTS=false` for dev |
| Gmail IMAP auth error | Use 16-char App Password; verify 2FA is enabled; check IMAP is on in Gmail settings |
| ServiceNow 401 | Verify `SNOW_USERNAME`/`SNOW_PASSWORD`; confirm user has `itil` role |

---

## Resources

- [IBM watsonx Orchestrate Documentation](https://www.ibm.com/docs/en/watsonx/watson-orchestrate)
- [watsonx Orchestrate Pre-built Skills Catalog](https://www.ibm.com/products/watsonx-orchestrate/integrations)
- [ServiceNow REST API Reference](https://developer.servicenow.com/dev.do#!/reference/api/xanadu/rest/)
- [Gmail App Passwords Help](https://support.google.com/accounts/answer/185833)
- [JSONata Expression Reference](https://docs.jsonata.org/simple)
- [IBM watsonx Orchestrate ADK SDK](https://ibm.github.io/watsonx-orchestrate-sdk/)

---

*Built with IBM watsonx Orchestrate — Primary: GUI Agentic Workflow | Backup: Python ADK*
