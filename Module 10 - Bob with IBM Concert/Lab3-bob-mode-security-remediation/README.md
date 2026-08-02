# Bob mode to connect with concert 

This guide walks you through the process of integrate BOB with IBM Concert.

## Overview

This custom Bob mode enables automated security vulnerability remediation by:
- Connecting to IBM Concert for vulnerability data
- Analyzing CVEs (dependency vulnerabilities) and SAST exposures (code-level issues)
- Proposing and applying secure fixes
- Running tests to validate fixes
- Committing changes with proper Git workflow
- Updating Concert status after remediation

## Step-by-Step Guide

### Step 1: Check Bob Mode

We already put the Bob mode to connect with concert in the repository, take a look in the .bob directory and the custom_modes.yaml file.

``` bash
beacon-bob-concert/
├── Lab1-java-modernization 
├── Lab2-java-modernization
├── Lab3-bob-mode-security-remediation
   ├── .bob #######>>>> here
      ├── rules 
      │   ├── rules-security-remediation
      │   │   ├── README.md
      │   │   ├── concert-api-integration.md
      │   │   └── remediation-strategies.md
      ├── custom_modes.yaml
      ├── .env.example
├── README.md
└── Lab4-vulnerabilities-mitigation-using-bob
└── .gitignore
└── LICENSE
└── README.md

```
### Step 3: Copy the .bob directory
Assuming you're in the `beacon-bob-concert` directory, run:

```bash
cp -r Lab3-bob-mode-security-remediation/.bob ./
```

In order to use the Bob mode, you need to copy the .bob directory to your workspace

``` bash
beacon-bob-concert/
├── .bob #######>>>> directory copied
├── Lab1-java-modernization 
├── Lab2-java-modernization
├── Lab3-bob-mode-security-remediation
   ├── .bob
      ├── rules 
      │   ├── rules-security-remediation
      │   │   ├── README.md
      │   │   ├── concert-api-integration.md
      │   │   └── remediation-strategies.md
      ├── custom_modes.yaml
      ├── .env.example
├── README.md
└── Lab4-vulnerabilities-mitigation-using-bob
└── .gitignore
└── LICENSE
└── README.md
```

![Copy Bob](image/1-copy-bob.png)


### Step 2: Configure Concert Credentials

**Option 1: Interactive Setup (Recommended)**

Bob will guide you through credential setup on first use:
1. Activate Security Remediation mode
2. Type: "Check Concert for vulnerabilities"
3. Bob will detect no `.env` file and ask for:
   - Concert Base URL
   - API Key
   - Instance ID
4. Bob creates `.env` file automatically

**Option 2: Manual Setup**

Create a `.env` file in your workspace:

```bash
# Copy template
cp .env.example .env

# Edit with your credentials
```

Add your Concert API credentials:

```bash
# Concert API Configuration
CONCERT_BASE_URL=https://your-concert-instance.ibm.com/concert/core/api/v1
CONCERT_API_KEY=base64_encoded_username_colon_apikey
CONCERT_INSTANCE_ID=0000-0000-0000-0000
```

**How to get your credentials:**

1. **API Key**: 
   - Log into IBM Concert
   - Go to Settings → API Keys
   - Generate new key
   - Format: Base64-encoded `username:api_key`
   - Example: `concertuser:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` → `<base64-encoded-value>`

2. **Instance ID**: 
   - Provided by your Concert administrator
   - Typically `0000-0000-0000-0000`

3. **Base URL**: 
   - Your Concert instance URL + `/concert/core/api/v1`
   - Example: `https://<your-concert-host>:12443/concert/core/api/v1`


### Step 3: Reload Bob

Restart VS Code or reload the Bob extension:
- Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
- Type "Reload Window"
- Press Enter

### Step 4: Verify Mode is Loaded

1. Open Bob
2. Click the mode selector
3. Look for "🔒 Security Remediation" in the custom modes list

![Copy Bob](image/2-modes.png)

### Step 5: Testing Security Remediation Modes

Type: 

```bash
Check Concert for vulnerabilities
```
![Testing Bob](image/3-testing-bob.png)


**Bob will detect no .env file and guide you through setup**:
   - Bob: "No .env file found. Let me help you set up Concert credentials."
   - Bob: "What is your Concert Base URL?"
   - You: Enter your Concert URL (e.g., `https://<your-concert-host>:12443/concert/core/api/v1`)

   ![Testing Bob](image/3.1-testing-bob.png)

   - Bob: "What is your Concert API Key?"
   - You: Enter your base64-encoded API key
   - Bob: "What is your Concert Instance ID?"
   - You: Enter your instance ID (typically `0000-0000-0000-0000`)

   ![Testing Bob](image/3.2-testing-bob.png)

   - Bob: "✅ Created .env file with your credentials"

   ![Testing Bob](image/3.3-testing-bob.png)

``` bash
beacon-bob-concert/
├── .bob 
├── Lab1-java-modernization 
├── Lab2-java-modernization
├── Lab3-bob-mode-security-remediation
   ├── .bob
      ├── rules 
      │   ├── rules-security-remediation
      │   │   ├── README.md
      │   │   ├── concert-api-integration.md
      │   │   └── remediation-strategies.md
      ├── custom_modes.yaml
      ├── .env.example
├── README.md
└── Lab4-vulnerabilities-mitigation-using-bob
└── .env #######>>>> here
└── .gitignore
└── LICENSE
└── README.md
```

   - Bob: "Testing Concert API connection..."
   - You: Click "Approve" when Bob asks to run the health check
   - Bob: "Connected successfully!"

   ![Testing Bob](image/3.4-testing-bob.png)

   Now Bob already connected to the concert instances, you may see your application in the list of applications.

   ![Testing Bob](image/3.5-testing-bob.png)


## Conclusion

Congratulations! You have successfully configure BOB modes and connected to the concert instances.

## Next Steps
- Using Bob modes to remediate vulnerabilities in your application.

## BOB Security Remediation Features

✅ **Automated Vulnerability Discovery** - Fetches all applications and their security issues from Concert
✅ **Smart Remediation** - Uses proven fix patterns for 10+ vulnerability types
✅ **Git Flow Integration** - Creates feature branches, commits fixes, and pushes changes
✅ **Test Validation** - Runs tests after each fix to ensure no regressions
✅ **Concert Integration** - Updates vulnerability status in Concert after remediation
✅ **Interactive Workflow** - User approval required at each step