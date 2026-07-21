# Service Desk Assistant — Complete Implementation Guide

> **AI-Powered Service Desk Automation with IBM Watsonx Orchestrate**
> 
> **Stack:** IBM Watsonx Orchestrate · Elasticsearch · ServiceNow · Gmail IMAP  
> **Approach:** Agent Builder with Tools (@tool decorator) and YAML Agent Definitions

---

## Prerequisites: Install the Watsonx Orchestrate ADK

Before anything else, install the IBM Watsonx Orchestrate ADK (Python 3.11+ required):

```bash
# Verify Python version
python --version

# Install (or upgrade) the ADK
pip install --upgrade ibm-watsonx-orchestrate
```

Or using `uv`:

```bash
uv add ibm-watsonx-orchestrate
```

Then add and activate your environment:

```bash
orchestrate env add -n <environment-name> -u <service-instance-url>
orchestrate env activate <environment-name>
```

Full installation guide: https://developer.watson-orchestrate.ibm.com/getting_started/installing

---

**Important Note:**

**IBM TechZone instances (Watsonx Orchestrate & Watsonx Discovery) and ServiceNow developer instance will be provided by the team.**

**Therefore:**
- **Section 3 (Environment Setup):** Only complete **Section 3.1** (Environment Variables) to configure credentials for the provided instances
- **Section 3.2-3.5:** These are **OPTIONAL** - only needed if you want to provision your own instances
- **Section 4 (ServiceNow Configuration):** Follow this section to configure the your own ServiceNow instance. It is optional if you are using the provided instances.

**You can skip the instance provisioning steps and jump directly to configuration using the credentials provided by your team.**

---

## Table of Contents

1. [Solution Architecture](#1-solution-architecture)
2. [Quick Start (15 minutes)](#2-quick-start-15-minutes)
3. [Environment Setup](#3-environment-setup)
4. [ServiceNow Configuration](#4-servicenow-configuration) (Optional)
5. [Data Setup, Import & Testing](#5-data-setup-import--testing)
6. [Tools Reference](#6-tools-reference) (Optional)
7. [Agents Reference](#7-agents-reference) (Optional)
8. [Development Patterns](#8-development-patterns) (Optional)
9. [Troubleshooting](#9-troubleshooting) (Optional)
10. [Production Deployment](#10-production-deployment) (Optional)

---

## 1. Solution Architecture

### Overview

The Service Desk Assistant automates service desk operations by processing emails, creating ServiceNow incidents, performing risk assessments using RAG, and providing resolution recommendations.

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│              IBM Watsonx Orchestrate                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │    Service Desk Assistant (Main Orchestrator)            │  │
│  └──┬──────────┬─────────────┬──────────────┬───────────────┘  │
│     │          │             │              │                   │
│  ┌──▼──────┐ ┌─▼─────────┐ ┌─▼──────────┐ ┌─▼──────────────┐  │
│  │ Email   │ │ Incident  │ │   Risk     │ │   ServiceNow   │  │
│  │ Tools   │ │ Logging   │ │  Mapping   │ │     Tools      │  │
│  │(1 tool) │ │  Agent    │ │   Agent    │ │   (3 tools)    │  │
│  └──┬──────┘ └─┬─────────┘ └─┬──────────┘ └─┬──────────────┘  │
└─────┼──────────┼─────────────┼────────────────┼─────────────────┘
      │          │             │                │
┌─────▼──┐  ┌───▼──────┐ ┌────▼────────────────▼──────────┐
│ Gmail  │  │ServiceNow│ │    Elasticsearch (RAG)          │
│ IMAP   │  │ Instance │ │  • risk_mapping_index           │
└────────┘  └──────────┘ │  • resolution_notes_index       │
                         └─────────────────────────────────┘
```

### Components

**6 Tools:**
- `create_servicenow_incident` - Creates incidents with AI fields
- `get_servicenow_incident` - Retrieves incident details
- `update_servicenow_incident` - Updates incidents
- `retrieve_risk_documents` - RAG search over governance docs
- `retrieve_resolution_notes` - Finds similar past resolutions
- `fetch_service_desk_emails` - Fetches emails via Gmail IMAP

**3 Agents:**
- **Incident Logging Agent** - Processes emails, creates incidents
- **Risk Mapping Agent** - Maps incidents to risk categories using RAG
- **Service Desk Assistant** - Main orchestrator

### Workflow

```
Email → Fetch → Extract Fields → Create Incident → Risk Assessment → 
Find Resolutions → Update Incident → Complete
```

### Technology Stack

| Component | Technology |
|---|---|
| **Orchestration** | IBM Watsonx Orchestrate |
| **LLM** | groq/openai/gpt-oss-120b |
| **Knowledge Base** | Elasticsearch 8.x |
| **Embeddings** | intfloat/multilingual-e5-large (WatsonxEmbeddings) |
| **Sparse Search** | ELSER (.elser_model_2_linux-x86_64) |
| **ITSM** | ServiceNow |
| **Email** | Gmail IMAP |
| **Language** | Python 3.13+ |

---

## 2. Quick Start (15 minutes)

### Prerequisites
- Python 3.13+
- Elasticsearch instance with certificate
- ServiceNow developer instance
- IBM Watsonx Orchestrate account
- Gmail account with App Password

### Installation

#### Option 1: Using Existing Python 3.13+

```bash
# 1. Navigate to project
cd Service_desk_Assistant_T3

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

#### Option 2: Install Python 3.13 on macOS (if needed)

**Using Homebrew:**
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.13
brew install python@3.13

# Verify installation
python3.13 --version

# Navigate to project
cd Service_desk_Assistant_T3

# Create virtual environment with Python 3.13
python3.13 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Using pyenv (recommended for managing multiple Python versions):**
```bash
# Install pyenv
brew install pyenv

# Add to shell profile (~/.zshrc or ~/.bash_profile)
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc

# Reload shell
source ~/.zshrc

# Install Python 3.13
pyenv install 3.13.5

# Set as global version (optional)
pyenv global 3.13.5

# Navigate to project
cd Service_desk_Assistant_T3

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Download from python.org:**
1. Go to https://www.python.org/downloads/macos/
2. Download Python 3.13.x macOS installer
3. Run the installer
4. Open Terminal and verify: `python3.13 --version`
5. Follow Option 1 steps above using `python3.13` command

### Configuration

1. **Create `.env` file** (see Section 3 for details)
2. **Complete Data Setup, Import & Testing** (see Section 5 for complete guide)

---

## 3. Environment Setup

### 3.1 Environment Variables

Create `.env` file at project root with the following variables:

```ini
# Elasticsearch (Knowledge Base)
ES_HOST=your-elasticsearch-host.com    # No https:// prefix
ES_PORT=9200
ES_USERNAME=elastic
ES_PASSWORD=your_password
ES_CERT_CONTENT="-----BEGIN CERTIFICATE----- ....... -----END CERTIFICATE-----"
ES_CERT_PATH=./certs/ca.crt # optional
ES_USE_SSL=true
ES_VERIFY_CERTS=false                  # false for dev/testing

# IBM Watsonx Orchestrate
WATSONX_ORCHESTRATE_URL=https://your-instance.ibm.com
WXO_APIKEY=your_api_key

# ServiceNow (Basic Authentication)
SNOW_INSTANCE_URL=https://your-instance.service-now.com
SNOW_USERNAME=svc_servicedesk_ai
SNOW_PASSWORD=your_password

# Gmail IMAP
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
IMAP_USE_SSL=true
IMAP_USERNAME=servicedesk@gmail.com
IMAP_PASSWORD=your_16_char_app_password       # Gmail App Password

SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=servicedesk@gmail.com
SMTP_PASSWORD=your_16_char_app_password
```

**Important Notes:**
- `ES_HOST`: Just hostname, no `https://` prefix
- `ES_VERIFY_CERTS`: Set to `false` for dev if certificate has issues
- `IMAP_PASSWORD`: Use Gmail App Password (16 chars), not regular password

---

### 3.2 ServiceNow Instance Setup

#### Get Developer Instance

1. **Sign Up for ServiceNow Developer Account**
   - Go to: https://developer.servicenow.com/
   - Click **"Sign Up"** or **"Log In"**
   - Complete registration with your email

2. **Request Personal Developer Instance (PDI)**
   - After login, go to **"Manage"** → **"Instance"**
   - Click **"Request Instance"**
   - Select release version (e.g., Vancouver, Washington DC)
   - Wait 2-5 minutes for provisioning

3. **Access Your Instance**

    **Option A: Access via ServiceNow SSO**
   1. Go to: https://signon.servicenow.com/x_snc_sso_auth.do?pageId=login
   2. Log in with your ServiceNow Developer account credentials
   3. Click on **"ServiceNow Developer Portal"** → **"Developer Program"**
   4. Click the **"Start Building"** icon at the top right corner
   5. You'll be redirected to your developer instance: `https://devXXXXX.service-now.com`
   6. You're now logged in as admin

   **Option B: Direct Access from Developer Portal**
   - You'll receive an instance URL: `https://devXXXXX.service-now.com`
   - Username: `admin`
   - Password: Provided in the instance details page
   - **Save these credentials securely**
   
4. **Find Your Instance Variables**
   ```
   SNOW_INSTANCE_URL: https://devXXXXX.service-now.com
   SNOW_USERNAME: svc_servicedesk_ai (create this user - see section 4.2)
   SNOW_PASSWORD: (password you set for the service account)
   ```

5. **Test Connection**
   - Log in to your instance using admin credentials
   - Verify you can access the Incident module
   - Navigate to: **All → Incident → All**

**Note:** Developer instances hibernate after 10 days of inactivity. Wake them up from the developer portal.

---

### 3.3 Gmail Setup (IMAP + SMTP)

This setup enables both **receiving emails** (IMAP) and **sending notifications** (SMTP) using Gmail.

#### Step 1: Enable 2-Step Verification

Gmail requires 2-Step Verification (2FA) to use app passwords.

1. **Go to Google Account Security**
   - Visit: https://myaccount.google.com/security
   - Sign in with your Gmail account
   - Scroll to **"How you sign in to Google"**

2. **Enable 2-Step Verification**
   - Click **"2-Step Verification"**
   - Click **"Get Started"**
   - Follow the prompts:
     - Enter your phone number
     - Verify with SMS code
     - Confirm setup

✅ 2-Step Verification is now enabled!

#### Step 2: Generate App Password

1. **Create App Password**
   - Go to: https://myaccount.google.com/apppasswords
   - Or: Google Account → Security → 2-Step Verification → App passwords
   
2. **Generate Password**
   - Click **"Select app"** → Choose **"Mail"**
   - Click **"Select device"** → Choose **"Other (Custom name)"**
   - Enter name: **"Service Desk Assistant"**
   - Click **"Generate"**

3. **Copy App Password**
   - You'll see a 16-character password like: `abcd efgh ijkl mnop`
   - **Important**:
     - Copy this password immediately
     - You won't be able to see it again
     - Remove spaces when using it: `abcdefghijklmnop`
     - **This same password works for both IMAP and SMTP**

#### Step 3: Enable IMAP in Gmail

1. **Open Gmail Settings**
   - Go to: https://mail.google.com
   - Click the **⚙️ Settings** icon (top right)
   - Click **"See all settings"**

2. **Enable IMAP**
   - Go to **"Forwarding and POP/IMAP"** tab
   - In the **"IMAP access"** section:
     - Select **"Enable IMAP"**
   - Click **"Save Changes"** at the bottom

✅ IMAP is now enabled!

**Note:** SMTP is automatically enabled when you have an app password. No additional configuration needed.

#### Find Your Gmail Variables

**For Receiving Emails (IMAP):**
```
IMAP_SERVER: imap.gmail.com
IMAP_PORT: 993
IMAP_USE_SSL: true
IMAP_USERNAME: your-email@gmail.com
IMAP_PASSWORD: abcdefghijklmnop (16-char app password, no spaces)
```

**For Sending Notifications (SMTP):**
```
SMTP_SERVER: smtp.gmail.com
SMTP_PORT: 587
SMTP_USERNAME: your-email@gmail.com
SMTP_PASSWORD: abcdefghijklmnop (same 16-char app password)
```

💡 **Tip:** You can use the same Gmail account for both IMAP and SMTP, or use different accounts if preferred.

---

### 3.4 Watsonx Discovery Setup (Elasticsearch)

> **📝 NOTE:** In this tutorial, "Watsonx Discovery" refers to **Elasticsearch** as the knowledge base. Variable names use `WATSONX_DISCOVERY_*` prefix for consistency, but they connect to an Elasticsearch instance provisioned from IBM TechZone.

#### Provision from IBM TechZone

1. **Access IBM TechZone**
   - Go to: https://techzone.ibm.com/
   - Sign in with your IBM ID
   - If you don't have an IBM ID, create one at: https://www.ibm.com/account/reg/us-en/signup

2. **Search for Watsonx Discovery**
   - Use search bar and type: `Watsonx Discovery`
   - Look for: **"Watson Discovery"**
   - Verify it's marked as "Available"

3. **Reserve Discovery Instance**
   - Click on the Discovery resource
   - Click **"Reserve"** or **"Request"**
   - Fill reservation form:
     ```
     Purpose: Service Desk AI Assistant - Knowledge Base
     Duration: 30 days (or as needed)
     Region: Select closest to your location
       - Dallas (us-south)
       - Frankfurt (eu-de)
       - London (eu-gb)
       - Tokyo (jp-tok)
       - Sydney (au-syd)
     
     Environment Type: Development
     ```
   - Add notes:
     ```
     Project: Service Desk Assistant Tutorial
     Use Case: AI-powered incident management with RAG
     Expected Load: ~1000 queries/day
     ```
   - Click **"Submit"**
   - Wait for approval (usually 5-15 minutes)

4. **Access Provisioned Instance**
   - Check email for: "Your TechZone reservation is ready"
   - Click "Please go HERE to accept your invitation" and join the account
   - Click **"View My Reservations"** button in email

5. **Save Credentials from TechZone**
   
   **⚠️ IMPORTANT:** TechZone provides these credentials in the reservation email:
   
   ```bash
   # Add to your .env file - FROM TECHZONE RESERVATION EMAIL
   WATSONX_DISCOVERY_URL=https://your-discovery-instance.cloud.ibm.com
   WATSONX_DISCOVERY_USERNAME=your_username_here
   WATSONX_DISCOVERY_PASSWORD=your_password_here
   WATSONX_DISCOVERY_PORT=443
   ```

6. **Find Your Watsonx Discovery Variables**
   ```bash
   # From TechZone Reservation Email
   WATSONX_DISCOVERY_URL=https://your-discovery-instance.cloud.ibm.com
   WATSONX_DISCOVERY_USERNAME=your_username_here
   WATSONX_DISCOVERY_PASSWORD=your_password_here
   WATSONX_DISCOVERY_PORT=443
   
   # Optional: Certificate path if using SSL verification
   WATSONX_DISCOVERY_CERT_PATH=/path/to/certificate.pem
   ```

7. **Update Your `.env` File**
---

### 3.5 IBM Watsonx Orchestrate Setup

#### Reserve Watsonx Orchestrate from TechZone

**Option 1: Direct Reservation Link (Fastest)**

   1. **Go Directly to Watsonx Orchestrate Reservation**
      - Visit: https://techzone.ibm.com/my/reservations/create/685009de78b93ca5d1eba052
      - Sign in with your IBM ID (or create one if needed)
      - This takes you directly to the Watsonx Orchestrate reservation page

**Option 2: Manual Search Method**
   - **Go to IBM TechZone**
      - Visit: https://techzone.ibm.com/
      - Sign in with your IBM ID (or create one if needed)
      - In the search bar, type: **"Watsonx Orchestrate"**
      - Look for **"IBM watsonx Orchestrate SaaS"** or similar environment

2. **Fill in Reservation Details**
   - **Purpose**: Development/Testing
   - **Purpose Description**: "Service Desk Assistant Development"
   - **Preferred Geography**: Select closest region
   - **End Date**: Select duration (typically 2-4 weeks)
   - Click **"Submit"**

3. **Wait for Provisioning**
   - Provisioning typically takes 15-30 minutes
   - You'll receive an email when ready
   - Check TechZone dashboard for status

4. **Access Your Instance**
   - Once provisioned, go to **"My Reservations"** in TechZone
   - Click on your Watsonx Orchestrate reservation
   - Find the **"Access Details"** section
   - Note down:
     - **Instance URL**: `https://your-instance.ibm.com`
     - **API Key**: Provided in reservation details
     - **Username/Password**: If applicable

5. **Find Your Watsonx Variables**
   ```
   WATSONX_ORCHESTRATE_URL: https://your-instance.ibm.com (from reservation)
   WXO_APIKEY: (API key from reservation details)
   ```

**Important Notes:**
- TechZone reservations are temporary (typically 2-4 weeks)
- Extend reservation before expiry if needed
- Save all credentials immediately after provisioning

#### Configure Watsonx Orchestrate CLI

```bash
# Install CLI (if not already installed)
pip install ibm-watsonx-orchestrate

# Activate environment
export WXO_APIKEY="your_api_key"
orchestrate env activate servicedesk_assistant --api-key $WXO_APIKEY

# Verify connection
orchestrate tools list
```

---

### 3.6 Complete .env File Example

After completing all instance setups, your `.env` file should look like:

```ini
# Elasticsearch (Knowledge Base)
ES_HOST=xxxxx.es.us-east-1.aws.found.io
ES_PORT=9243
ES_USERNAME=elastic
ES_PASSWORD=YourElasticPassword123
ES_CERT_CONTENT="-----BEGIN CERTIFICATE-----\nMIID...\n-----END CERTIFICATE-----"
ES_USE_SSL=true
ES_VERIFY_CERTS=false

# IBM Watsonx Orchestrate
WATSONX_ORCHESTRATE_URL=https://your-instance.ibm.com
WXO_APIKEY=your_ibm_cloud_api_key_here

# ServiceNow (Basic Authentication)
SNOW_INSTANCE_URL=https://dev12345.service-now.com
SNOW_USERNAME=svc_servicedesk_ai
SNOW_PASSWORD=YourServiceAccountPassword

# Gmail IMAP (Receiving Emails)
IMAP_SERVER=imap.gmail.com
IMAP_PORT=993
IMAP_USE_SSL=true
IMAP_USERNAME=servicedesk@gmail.com
IMAP_PASSWORD=abcdefghijklmnop

# Gmail SMTP (Sending Notifications)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=servicedesk@gmail.com
SMTP_PASSWORD=abcdefghijklmnop
```

**Security Reminder:**
- Never commit `.env` file to version control
- Add `.env` to `.gitignore`
- Store credentials in a password manager
- Use different credentials for dev/staging/production

---

## 4. ServiceNow Configuration

**Prerequisites:**
- Complete Section 3.2 (ServiceNow Instance Setup) to get your developer instance
- Have admin access to your ServiceNow instance

This section covers configuring ServiceNow for AI integration: creating a service account, adding custom AI fields, and configuring the incident form.

---

### 4.1 Create Integration User

#### Step 1: Navigate to User Administration

```
Filter Navigator: All → User Administration → Users
```

#### Step 2: Create New User

1. Click **"New"** button
2. Fill in the following details:
   ```
   User ID: svc_servicedesk_ai
   First name: Service Desk
   Last name: AI Integration
   Email: servicedesk-ai@yourcompany.com
   Active: ✓ (checked)
   ```
   
   **Note:** The "Web service access only" field is not available in all ServiceNow versions. If you don't see it, skip this field.

3. **Set Password**
   - Click **"Set Password"** button
   - Enter a strong password (save it securely)
   - Password: ________________ (record this in your password manager)

4. Click **"Submit"** to create the user

#### Step 3: Assign Roles

1. **Open the user record** you just created
   - Search for user: `svc_servicedesk_ai`
   - Click to open the user record

2. **Navigate to Roles section**
   - Scroll down to the **"Roles"** related list
   - Click **"Edit"** button

3. **Add Required Roles**
   
   **Core Roles (Required):**
   ```
   ✓ rest_service       - REST API access
   ✓ itil               - ITIL user role for incident management
   ✓ incident_manager   - Incident management permissions
   ```
   
   **Additional Recommended Roles:**
   ```
   ✓ sn_incident_read   - Read access to incident table
   ✓ sn_incident_write  - Write access to incident table
   ✓ rest_api_explorer  - Access to REST API Explorer for testing
   ```
   
   **Optional (for advanced features):**
   ```
   ✓ web_service_admin  - Web service administration
   ✓ import_admin       - Import set administration (if using imports)
   ```
   
   **Note:** The roles `sn_incident_read` and `sn_incident_write` provide granular access control for incident operations and are recommended for production environments.

4. **Save Changes**
   - Click **"Update"** button to save the role assignments

5. **Verify Roles**
   - Confirm all required roles are listed in the "Roles" section
   - User should now have API access and incident management permissions

---

### 4.2 Add Custom AI Fields

#### Step 1: Navigate to Incident Table Dictionary

```
All → Filter Navigator (Search) → System Definition → Tables
Search: incident
Click on "incident" table
```

#### Step 2: Add Custom Fields

Click on the **"Columns"** tab, then click **"New"** to add each field:

**Field 1: AI Risk Category**
```
Column label: AI Risk Category
Column name: u_ai_risk_category
Type: String
Max length: 100
```
Click **"Submit"**

**Field 2: AI Risk Severity**
```
Column label: AI Risk Severity
Column name: u_ai_risk_severity
Type: Choice
Max length: 40
```
After creating, add choices from "Advanced view" option:
- Low
- Medium
- High
- Critical

Click **"Submit"**

**Field 3: AI Recommended Resolution**
```
Column label: AI Recommended Resolution
Column name: u_ai_recommended_resolution
Type: String (HTML)
Max length: 4000
```
Click **"Submit"**

**Field 4: AI Confidence Score**
```
Column label: AI Confidence Score
Column name: u_ai_confidence_score
Type: Decimal
```
Click **"Submit"**

**Field 5: AI Processing Status** (Optional)
```
Column label: AI Processing Status
Column name: u_ai_processing_status
Type: Choice
Max length: 40
```
After creating, add choices from "Advanced view" option:
- Pending
- Processing
- Completed
- Failed

Click **"Submit"**

### 4.3 Add Fields to Form Layout

#### Step 1: Navigate to Form Designer

```
All → Filter Navigator (Search) → Incident → All
Open any incident record
Right-click on the form header → Configure → Form Layout
```

#### Step 2: Add AI Fields Section

1. **Create New Section** (Optional but recommended)
   - In the Form Layout editor, you can create a new section called "AI Analysis"
   - This groups all AI fields together for better organization

2. **Add Custom Fields to Form**
   - In the left panel, find "Available" fields
   - Search for your custom fields (u_ai_*)
   - Drag and drop each field to the form:
     - u_ai_risk_category
     - u_ai_risk_severity
     - u_ai_recommended_resolution
     - u_ai_confidence_score
     - u_ai_processing_status (if created)

3. **Arrange Fields**
   - Position the AI fields in a logical order
   - Recommended placement: After standard incident fields

4. **Save Layout**
   - Click **"Save"** button
   - The fields will now appear on all incident forms

---

### 4.4 OAuth Setup

> For a full walkthrough of ServiceNow instance setup including OAuth, see [ServiceNow Dev Instance Setup](./service_now_dev_instance_setup.md).

1. Navigate to **System OAuth > Application Registry**
2. Click **New** > **New Inbound Integration Experience** > **OAuth - Authorization code grant**
3. Fill in:
   - Name: `Watsonx Integration`
   - Copy Client ID and Client Secret
4. Add to `.env`

---

## 5. Data Setup, Import & Testing

This section covers the complete workflow from data preparation to testing your deployed agents in Watsonx Orchestrate.

**Important Note:**

**Sample data is already available in the `data/` directory and ready to use!**

**You can:**
- ✅ **Use the provided sample data** - Risk documents and resolution notes are already included
- ✅ **Add more data** - You can add additional documents on top of the existing samples if needed
- ✅ **Skip data preparation** - If the sample data is sufficient, proceed directly to data ingestion (Section 5.3)

**Data Locations:**
- `data/risk_docs/sample_risk_documents.json` - Governance and risk documents
- `data/resolution_notes/sample_servicedesk_notes.json` - Past incident resolutions

---

**What you'll do:**
1. Prepare and ingest knowledge base data (sample data provided)
2. Test all service connections
3. Import tools and agents to Watsonx Orchestrate
4. Test the system end-to-end

---

### 5.1 Prepare Sample Data

The project includes sample data files that you can use for testing:

**Risk Documents Location:**
```
data/risk_docs/sample_risk_documents.json
```

**Resolution Notes Location:**
```
data/resolution_notes/sample_servicedesk_notes.json
```

You can use these sample files or create your own following the formats below.

---

### 5.2 Data Formats

**Risk Documents** (`data/risk_docs/*.json`):
```json
[
  {
    "risk_id": "RISK-001",
    "risk_category": "Operational Risk",
    "risk_description": "Risk of system downtime...",
    "severity_level": "High",
    "keywords": ["downtime", "availability"],
    "mitigation_strategies": "Implement redundancy...",
    "compliance_requirements": "ISO 27001, SOC 2"
  }
]
```

**Resolution Notes** (`data/resolution_notes/*.json`):
```json
[
  {
    "incident_number": "INC0010001",
    "incident_type": "Email Access Issue",
    "short_description": "Cannot access email",
    "detailed_description": "User unable to access Outlook email. Error message: 'Cannot connect to server'",
    "category": "Software",
    "priority": "Medium",
    "resolution_notes": "Issue caused by corrupted Outlook profile. Recreated profile and restored settings.",
    "resolution_steps": "1. Close Outlook\n2. Open Control Panel > Mail\n3. Click 'Show Profiles'\n4. Create new profile\n5. Configure email account\n6. Set as default profile",
    "resolution_time_hours": 0.5,
    "tags": ["email", "outlook", "profile"]
  }
]
```

---

### 5.3 Create Elasticsearch Indices

Create the required indices in Elasticsearch:

```bash
# Activate virtual environment
source venv/bin/activate

# Create indices with proper mappings
python ingestion/create_indices.py
```

**Expected Output:**
```
Creating index: risk_mapping_index
✓ Index created successfully
Creating index: resolution_notes_index
✓ Index created successfully
```

**What this does:**
- Creates `risk_mapping_index` for governance documents
- Creates `resolution_notes_index` for past incident resolutions
- Sets up proper field mappings for text search
- Configures BM25 similarity for keyword-based retrieval

---

### 5.4 Ingest Data into Elasticsearch

Now ingest your sample data:

```bash
# Ingest risk documents
python ingestion/ingest_risk_docs.py

# Ingest resolution notes
python ingestion/ingest_resolution_notes.py
```

**Expected Output:**
```
Ingesting risk documents...
✓ Ingested 15 documents into risk_mapping_index

Ingesting resolution notes...
✓ Ingested 25 documents into resolution_notes_index
```

---

### 5.5 Verify Data Ingestion

Test that data was ingested correctly:

```bash
# Search for a test query
python ingestion/search.py
```

Or use the Elasticsearch API directly:

```bash
# Count documents in risk index
curl -u elastic:password https://your-host:9200/risk_mapping_index/_count

# Count documents in resolution notes index
curl -u elastic:password https://your-host:9200/resolution_notes_index/_count
```

**Expected Response:**
```json
{
  "count": 15,
  "_shards": {...}
}
```

---

### 5.6 Test All Connections

After data ingestion, verify all your service connections are working:

```bash
# Activate virtual environment
source venv/bin/activate

# Test all connections
python test_connections.py
```

**Expected Output:**
```
✓ Elasticsearch connection successful
✓ ServiceNow connection successful
✓ Gmail IMAP connection successful
✓ All connections verified!
```

**If any connection fails:**
- Check your `.env` file for typos
- Verify credentials in the respective service
- Review the error message for specific issues
- See Troubleshooting section (Section 9)

---

### 5.7 Data Setup Checklist

Before proceeding to import agents, verify:

- [ ] `.env` file created with all credentials
- [ ] Virtual environment activated
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Elasticsearch indices created (`python ingestion/create_indices.py`)
- [ ] Risk documents ingested (`python ingestion/ingest_risk_docs.py`)
- [ ] Resolution notes ingested (`python ingestion/ingest_resolution_notes.py`)
- [ ] Data verified in Elasticsearch
- [ ] All connections tested successfully (`python test_connections.py`)

✅ Once all items are checked, proceed to import agents below.

---

### 5.8 Import to Watsonx Orchestrate

Now that your data is ready, import the tools and agents to Watsonx Orchestrate.

#### Automated Import (Recommended)

```bash
bash import_to_orchestrate.sh
```

The import scripts will:
1. Configure the Watsonx Orchestrate environment
2. Import and set credentials for `elasticsearch-service-desk` and `watsonx-ai-service-desk` connections (draft + live)
3. Import tools bound to their connections
4. Import agents

**Manual Agent Configuration (If Needed):**
If `incident_logging_agent` and `risk_mapping_agent` are not displayed in the **Agents** section of the `Service_Desk_Agent_Example` agent in the Watsonx Orchestrate UI, add them manually:

1. Open the `Service_Desk_Agent_Example` agent in Watsonx Orchestrate UI
2. Navigate to the **Agents** section
3. Click **"Add agent"** → **"Local Instance"**
4. Add both agents:
   - `incident_logging_agent`
   - `risk_mapping_agent`
5. Save the configuration

**Note about Risk Tools:**
- The risk tools use **hybrid search** combining ELSER sparse search and WatsonX dense embeddings (`intfloat/multilingual-e5-large`)
- Credentials are managed via Watsonx Orchestrate connections — no credential injection required
- Two connections must be imported and configured before importing risk tools: `elasticsearch-service-desk` and `watsonx-ai-service-desk`

#### Verify Imports

```bash
# List tools (expect 6)
orchestrate tools list

# List agents (expect 3)
orchestrate agents list
```

**Expected Output:**
```
Tools (2):
- retrieve_risk_documents
- retrieve_resolution_notes

```

---

### 5.9 Test in Watsonx Orchestrate UI

Open the Watsonx Orchestrate UI and test your deployed agents.

#### Test Scenario 1: Process Service Desk Emails

**User Input:**
> "I need help processing service desk emails"

**Expected System Behavior:**
1. Asks how many emails to fetch
2. Fetches emails from Gmail IMAP
3. Processes each email:
   - Extracts incident details
   - Creates ServiceNow incident
   - Performs risk assessment using RAG
   - Finds similar past resolutions
   - Updates incident with AI recommendations
4. Provides summary of all processed emails

**Expected Result:**
- Multiple incidents created in ServiceNow
- Each incident has AI-generated risk assessment
- Each incident has resolution recommendations
- All incidents updated with confidence scores

#### Test Scenario 2: Risk Assessment for Existing Incident

**User Input:**
> "Assess the risk for incident INC0010023"

**Expected System Behavior:**
1. Retrieves incident details from ServiceNow
2. Performs risk assessment using RAG over governance documents
3. Provides:
   - Risk category (e.g., "Cybersecurity Risk")
   - Risk severity (Low/Medium/High/Critical)
   - Justification based on retrieved documents
4. Updates incident with AI fields

#### Test Scenario 3: Batch Processing

**User Input:**
> "Process all high-priority emails from today"

**Expected System Behavior:**
1. Fetches today's emails
2. Filters for high-priority keywords
3. Processes critical incidents first
4. Escalates appropriately based on risk severity

#### Natural Language Commands to Try

- "Process emails"
- "Create an incident for [description]"
- "Assess risk for INC0010023"
- "Find similar incidents to [description]"
- "Show me high-priority tickets"
- "Update incident with resolution"
- "Fetch 5 service desk emails"

---

### 5.10 Troubleshooting Import & Testing

**Import Fails:**
- Verify `WXO_APIKEY` is set correctly
- Check `PYTHONPATH` includes current directory
- Ensure all dependencies are installed
- See Section 9 (Troubleshooting) for details

**Agent Not Responding:**
- Check agent was imported successfully: `orchestrate agents list`
- Verify tools are available: `orchestrate tools list`
- Check Watsonx Orchestrate UI for error messages

**Tools Not Working:**
- Test connections: `python test_connections.py`
- Verify credentials in `.env` file
- Check service availability (ServiceNow, Elasticsearch, Gmail)

---

## 6. Tools Reference

### 6.1 ServiceNow Tools

#### `create_servicenow_incident`
Creates incident with AI fields.

**Parameters:**
- `short_description` (str): Summary (max 100 chars)
- `description` (str): Full details
- `caller_email` (str): Reporter email
- `urgency` (str): 1=Critical, 2=High, 3=Medium, 4=Low
- `category` (str): Hardware, Software, Network, Access, Security, Other
- `risk_category` (str, optional): AI-mapped risk
- `risk_severity` (str, optional): AI severity
- `resolution_recommendation` (str, optional): AI recommendation

**Returns:**
```json
{
  "success": true,
  "ticket_number": "INC0010023",
  "sys_id": "abc123...",
  "url": "https://..."
}
```

#### `get_servicenow_incident`
Retrieves incident by ticket number.

**Parameters:**
- `ticket_number` (str): e.g., INC0010023

#### `update_servicenow_incident`
Updates incident with notes/state.

**Parameters:**
- `sys_id` (str): ServiceNow sys_id
- `work_notes` (str, optional): Notes to add
- `state` (str, optional): 1=New, 2=InProgress, 6=Resolved, 7=Closed
- `resolution_notes` (str, optional): Resolution description

### 6.2 Risk Tools

#### `retrieve_risk_documents`
RAG search over governance documents.

**Parameters:**
- `incident_description` (str): Incident text
- `top_k` (int, default=5): Number of docs

**Returns:**
```json
{
  "success": true,
  "documents": [
    {
      "content": "IT Infrastructure Risk Policy...",
      "title": "Infrastructure Risk Management",
      "category": "Infrastructure Risk",
      "relevance_score": 0.85
    }
  ]
}
```

#### `retrieve_resolution_notes`
Finds similar past resolutions.

**Parameters:**
- `incident_description` (str): Incident text
- `top_k` (int, default=3): Number of resolutions

### 6.3 Email Tools

#### `fetch_service_desk_emails`
Fetches unread emails from Gmail IMAP.

**Parameters:**
- `max_emails` (int, default=10): Max emails to fetch

**Returns:**
```json
{
  "success": true,
  "emails": [
    {
      "sender": "user@example.com",
      "subject": "Laptop not working",
      "body": "...",
      "received_at": "2024-01-15 10:30:00"
    }
  ],
  "total_fetched": 1
}
```

**Configuration:**
- Uses IMAP credentials from `.env`:
  - `IMAP_SERVER` (default: imap.gmail.com)
  - `IMAP_PORT` (default: 993)
  - `IMAP_USERNAME`
  - `IMAP_PASSWORD`

---

#### `send_incident_notification_email`
Sends professional HTML email notifications about incident processing completion.

**Parameters:**
- `recipient_emails` (str, required): Comma-separated email addresses (e.g., "manager@company.com, team@company.com")
- `incident_number` (str, required): ServiceNow incident number (e.g., "INC0010023")
- `subject` (str, required): Email subject line
- `incident_summary` (str, required): Brief summary of the incident
- `risk_assessment` (str, required): AI-generated risk assessment including category and severity
- `resolution_recommendation` (str, required): AI-generated resolution recommendation
- `incident_url` (str, required): ServiceNow incident URL for direct access

**Returns:**
```json
{
  "success": true,
  "message": "✅ Email notification sent successfully to 2 recipient(s)",
  "recipients": ["manager@company.com", "team@company.com"],
  "incident_number": "INC0010023",
  "subject": "Incident INC0010023 Processed - Cannot access VPN"
}
```

**Email Features:**
- 📧 Professional HTML formatting with IBM branding
- 📱 Mobile-responsive design
- 🔗 Direct ServiceNow incident link button
- ⚠️ Color-coded risk assessment section
- 💡 Formatted resolution recommendations
- 📄 Plain text fallback for email clients

**Configuration:**
- Uses SMTP credentials from `.env`:
  - `SMTP_SERVER` (default: smtp.gmail.com)
  - `SMTP_PORT` (default: 587)
  - `SMTP_USERNAME`
  - `SMTP_PASSWORD`

**Example Usage in Workflow:**
```yaml
# After updating incident, send notification
- tool: send_incident_notification_email
  parameters:
    recipient_emails: "manager@company.com, team@company.com"
    incident_number: "INC0010023"
    subject: "Incident INC0010023 Processed - Cannot access VPN"
    incident_summary: "User reported laptop not connecting to VPN"
    risk_assessment: "Risk Category: Infrastructure Risk | Severity: Medium"
    resolution_recommendation: "1. Verify VPN client\n2. Check network\n3. Reset credentials"
    incident_url: "https://dev12345.service-now.com/incident.do?sys_id=abc123"
```

---

## 7. Agents Reference

### 7.1 Incident Logging Agent

**File:** `agents/incident_logging_agent.yml`

**Purpose:** Process emails and create ServiceNow incidents

**LLM:** groq/openai/gpt-oss-120b

**Tools:** `create_servicenow_incident`

**Urgency Logic:**
- **Critical (1)**: System down, data loss, security breach
- **High (2)**: Major functionality impaired, multiple users affected
- **Medium (3)**: Partial functionality loss, workaround available
- **Low (4)**: Minor issue, cosmetic, feature request

**Category Logic:**
- **Hardware**: Physical equipment issues
- **Software**: Application errors, crashes
- **Network**: Connectivity, VPN, Wi-Fi
- **Access**: Login, permissions, passwords
- **Security**: Suspicious activity, malware
- **Other**: Doesn't fit above

### 7.2 Risk Mapping Agent

**File:** `agents/risk_mapping_agent.yml`

**Purpose:** Map incidents to risk categories using RAG

**LLM:** groq/openai/gpt-oss-120b

**Tools:** `retrieve_risk_documents`

**Risk Categories:**
- Operational Risk
- Cybersecurity Risk
- Compliance Risk
- Infrastructure Risk
- Data Privacy Risk
- Third-Party Risk
- Business Continuity Risk

**Risk Severity:**
- **Critical**: Immediate threat to business
- **High**: Significant impact, urgent attention
- **Medium**: Moderate impact, address soon
- **Low**: Minor impact, normal course

### 7.3 Service Desk Assistant

**File:** `lab_exports/Service_Desk_Agent_Example/agents/native/Service_Desk_Agent_Example.yaml`

**Purpose:** Main orchestrator for end-to-end workflow with email notifications

**LLM:** groq/openai/gpt-oss-120b

**Tools:** All 7 tools
- `fetch_service_desk_emails`
- `create_servicenow_incident`
- `get_servicenow_incident`
- `update_servicenow_incident`
- `retrieve_risk_documents`
- `retrieve_resolution_notes`
- `send_incident_notification_email`

**Complete Workflow:**
1. **Fetch emails** from Gmail IMAP
2. **For each email:**
   - 2.1 Create ServiceNow incident
   - 2.2 Perform AI risk assessment
   - 2.3 Find resolution recommendations
   - 2.4 Update incident with AI insights
   - 2.5 **Send email notification** to stakeholders
   - 2.6 Ask before processing next email
3. **Summary** of all processed incidents

**Email Notification Feature:**
- Sends professional HTML emails after incident processing
- Includes incident details, risk assessment, and resolutions
- Configurable recipients (comma-separated)
- Optional step - user can skip if not needed

---

## 8. Development Patterns

### 8.1 Tool Pattern

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

### 8.2 Agent Pattern

```yaml
spec_version: v1
style: default
name: my_agent
llm: watsonx/meta-llama/llama-3-2-90b-vision-instruct

description: Brief description

instructions: >
  ## Role
  Agent's role
  
  ## Guidelines
  - Guideline 1
  - Guideline 2

tools:
  - tool_name_1
  - tool_name_2
```

### 8.3 Error Handling

All tools return consistent format:
- Success: `{"success": true, ...data}`
- Failure: `{"success": false, "error": "...", "message": "..."}`

---

## 9. Troubleshooting

### Tool Import Fails
**Solution:** Set `PYTHONPATH="${PWD}:${PYTHONPATH}"`

### Agent Import Fails
**Solution:** 
1. Validate YAML syntax
2. Ensure tools imported first
3. Check LLM model name

### Risk Tools Import Hangs
**Solution:** Wait 1-2 minutes (loading 420MB model is normal)

### Elasticsearch Connection Issues
**Solution:**
1. Verify `ES_HOST` has no `https://` prefix
2. Check credentials
3. Set `ES_VERIFY_CERTS=false` for dev

### ServiceNow Auth Failures
**Solution:**
1. Verify credentials in ServiceNow UI
2. Check user has correct roles
3. Test basic auth before OAuth

### Gmail IMAP Issues
**Solution:**
1. Use App Password (16 chars), not regular password
2. Verify 2FA enabled
3. Check `IMAP_SERVER=imap.gmail.com`

### Watsonx Orchestrate Connection
**Solution:**
1. Verify `WXO_APIKEY`
2. Check network connectivity
3. Try: `orchestrate env activate servicedesk_assistant --api-key $WXO_APIKEY`

---

## 10. Production Deployment

### Security Checklist

- [ ] Never commit `.env` file
- [ ] Store certificates securely
- [ ] Use OAuth for ServiceNow
- [ ] Enable all guardrails
- [ ] Review PII masking patterns
- [ ] Set `ES_VERIFY_CERTS=true`
- [ ] Use strong passwords
- [ ] Enable audit logging
- [ ] Set up monitoring

### Guardrails

The `guardrails/` directory contains PII enforcement scripts powered by the IBM Watson OpenScale Guardrails API.

#### Files

| File | Direction | Purpose |
|---|---|---|
| `guardrails_input.py` | `input` | Screens user messages before agent processes them |
| `guardrails_output.py` | `output` | Screens agent responses before returning to user |
| `test_texts.py` | — | 10 PII + 10 non-PII test cases |

#### Standalone testing

```bash
python guardrails/guardrails_input.py
python guardrails/guardrails_output.py
python guardrails/test_texts.py
```

Requires `WATSONX_APIKEY` in `.env`. A bearer token is fetched automatically from IBM Cloud IAM.

#### Deploy as Watsonx Orchestrate plugins

Plugins intercept agent input/output automatically — no agent tool call needed.

> **Note:** `guardrails_plugin.py` is not included in this repo. To deploy the guardrails as a plugin, adapt the scripts using the plugin decorator pattern. See [WxGov_plugin.py](https://github.ibm.com/jerome-joubert/WxO-Plugins/blob/main/WxGov_plugin.py) for a reference implementation.

Import and register:

```bash
orchestrate tools import -k python -f guardrails/guardrails_plugin.py
```

Add to your agent YAML:

```yaml
plugins:
  agent_pre_invoke:
    - guardrail_pii_check
```

**References:**
- [Plugin documentation](https://developer.watson-orchestrate.ibm.com/plugins/plugins)
- [Plugin reference examples](https://github.ibm.com/jerome-joubert/WxO-Plugins)

### RBAC

Role-based access control for agents can be implemented using Watsonx Orchestrate **pre-invoke plugins**. A plugin can intercept every agent request, inspect the caller's identity or role, and block or allow execution accordingly — without modifying the agent itself.

See reference implementation: [RBAC_plugin.py](https://github.ibm.com/jerome-joubert/WxO-Plugins/blob/main/RBAC_plugin.py)

### Monitoring Metrics

- Email processing rate
- Incident creation success rate
- Risk assessment accuracy
- Resolution recommendation relevance
- Average processing time
- Error rates

### Scaling

For high-volume:
- Use Elasticsearch cluster
- Implement rate limiting
- Cache frequently accessed data
- Use async processing
- Implement retry logic with exponential backoff

---

## Resources

- [IBM Watsonx Orchestrate Docs](https://www.ibm.com/docs/en/watsonx/watson-orchestrate)
- [Agent Builder Tools Reference](https://ibm.github.io/watsonx-orchestrate-sdk/)
- [ServiceNow REST API](https://developer.servicenow.com/dev.do#!/reference/api/vancouver/rest/)
- [Elasticsearch Python Client](https://elasticsearch-py.readthedocs.io/)
