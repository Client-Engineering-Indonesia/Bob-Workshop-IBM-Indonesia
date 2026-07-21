# ServiceNow OAuth2 (Authorization Code) Setup for watsonx Orchestrate

This guide explains how to configure ServiceNow OAuth2 using the **Authorization Code grant type** and connect it to watsonx Orchestrate.

---

## 1. Overview

This integration enables watsonx Orchestrate to securely authenticate with ServiceNow and perform actions (e.g. creating or retrieving incidents) using a governed user identity.

**Architecture:**


watsonx Orchestrate → OAuth2 (Authorization Code) → ServiceNow → API access (e.g. incidents)


---

## 2. Create OAuth Application in ServiceNow

### Navigate to OAuth setup

In your ServiceNow instance:


System OAuth → Application Registry


Or use search:


Application Registry


---

### Create new OAuth application

Click:


New → New Inbound Integration Experience → OAuth - Authorization code grant


---

### Fill required fields

#### Basic configuration


Name:
watsonx-orchestrate

Provider name:
servicenow


---

#### Redirect URL (Required)

In watsonx Orchestrate, copy the **callback URL** and paste it here.

**Example:**


https://us-south.watson-orchestrate.cloud.ibm.com/mfe_connectors/api/v1/agentic/oauth/_callback


**Important:**
- Use only the callback URL
- Do NOT paste the full authorization request URL
- Must match exactly (including no trailing slash differences)

---

#### Other settings


Client ID:
(auto-generated)

Client Secret:
(auto-generated)

This is a public client:
unchecked

Active:
checked


---

## 3. Access Configuration

Uncheck "Allow access only to APIs in selected scope"

If that did not work for your use case, try:
Add Auth scope option "useraccount" to grant access to all resources (risky).

---

## 4. Save and Retrieve Credentials

After saving, note the following:


Client ID
Client Secret


These will be used in watsonx Orchestrate.

---

## 5. ServiceNow OAuth Endpoints

Use the following endpoints (replace with your instance URL):


Authorization URL:
https://<instance>.service-now.com/oauth_auth.do

Token URL:
https://<instance>.service-now.com/oauth_token.do

Server URL:
https://<instance>.service-now.com


---

## 6. Configure watsonx Orchestrate Connection

### Create new connection

Select:


Authentication Type:
OAuth2 - Authorization Code


---

### Enter connection details


Server URL:
https://<instance>.service-now.com

Authorization URL:
https://<instance>.service-now.com/oauth_auth.do

Token URL:
https://<instance>.service-now.com/oauth_token.do

Client ID:
<from ServiceNow>

Client Secret:
<from ServiceNow>


---

### Authorize

1. Click **Connect**
2. Log in to ServiceNow
3. Click **Allow**

---

## 7. Required ServiceNow Roles

The authenticated user must have appropriate roles to perform actions.

Minimum for incident operations:


itil


For testing only:


admin


---

## 8. Creating and Viewing Tickets

### Correct table for incidents

To create ServiceNow incidents, use:

```
/api/now/table/incident
```

Example payload:

```json
{
  "short_description": "Search app went down",
  "description": "Detailed issue description",
  "priority": "1"
}
```

### Viewing incidents

In ServiceNow: **Incident → All**

Or directly:

```
https://<instance>.service-now.com/incident_list.do
```

### Important note

ServiceNow has multiple record types:

| Table | Prefix | Description |
|---|---|---|
| `incident` | `INC` | IT incidents |
| `task` | `TASK` / `TKT` | Generic tasks |

Ensure your integration is writing to the `incident` table if you expect tickets to appear in the Incident view.

## 9. Common Issues

**Redirect URI mismatch**
- Ensure the redirect URL matches exactly between ServiceNow and Orchestrate

**Authentication succeeds but API fails**
- Check user roles (e.g. `itil`)
- Ensure scopes are not restricting access

**Tickets not visible in Incident list**
- Verify the correct table (`incident`) is being used
- Check ticket prefix (should be `INC`)

## 10. Summary

| Setting | Value |
|---|---|
| OAuth Flow | Authorization Code |
| Authentication | via ServiceNow login |
| Authorization | controlled by ServiceNow roles |
| API Access | via ServiceNow tables (e.g. `incident`) |

This setup enables secure, governed integration between watsonx Orchestrate and ServiceNow for enterprise workflows.
