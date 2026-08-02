# Security Remediation Mode - Rules

This directory contains the rules and guidelines for Bob's Security Remediation mode, which integrates with IBM Concert for automated vulnerability remediation.

## Mode Availability

This mode is configured as a **Global Mode**, which means:
- ✅ Available in all VS Code workspaces
- ✅ Same mode behavior everywhere
- ✅ Each workspace has its own `.env` file with Concert credentials

### Using in Different Workspaces

When you open a new workspace and activate Security Remediation mode:

1. **`.env` file present**: Bob will read credentials and proceed directly to connection test
2. **No `.env` file**: Bob will stop and ask you to create one — refer to Lab 3 Step 2

### Example Workflow

```
Module 10 - Bob with IBM Concert/
├── .env  ← created in Lab 3 Step 2
└── .bob/ ← already included in the workshop repo
```

## Files

### 1. concert-api-integration.md
Complete guide for interacting with Concert's REST API:
- **Authentication**: Custom `C_API_KEY` format (NOT Bearer token)
- **API endpoints**: Applications, CVEs, SAST exposures, status updates
- **Error handling**: HTTP status codes and error responses
- **Best practices**: Rate limiting, caching, validation
- **Working examples**: Tested curl commands with real Concert instance

### 2. remediation-strategies.md
Proven fix patterns for 10 common vulnerabilities:
- SQL Injection (CWE-89)
- Cross-Site Scripting (XSS) (CWE-79)
- Path Traversal (CWE-22)
- Insecure Deserialization (CWE-502)
- Authentication Bypass (CWE-287)
- Weak Cryptography (CWE-327)
- Command Injection (CWE-78)
- LDAP Injection (CWE-90)
- XML External Entity (XXE) (CWE-611)
- **Remote Code Execution via ScriptEngine (CWE-94)** - NEW!

Each vulnerability type includes:
- Vulnerable code pattern
- Secure fix strategy (with real-world examples)
- Additional security measures
- Testing recommendations

## How Bob Uses These Rules

When you activate the Security Remediation mode, Bob follows a **5-phase workflow**:

### Phase 1: Test Connection (First Use)
- Verifies Concert API connectivity
- Tests authentication with correct `C_API_KEY` format
- Validates environment variables

### Phase 2: Discover Applications
- Lists all applications in Concert
- Shows criticality, CVE count, and exposure count
- Presents results in a markdown table

### Phase 3: Clone Repository
- Attempts HTTPS clone first (requires token)
- Falls back to SSH (uses existing keys)
- Prepares codebase for analysis

### Phase 4: Choose Scope
- Asks user: CVEs or SAST Exposures?
- **CVEs**: Dependency vulnerabilities (Log4j, Spring, etc.)
- **Exposures**: Code-level issues (SQL injection, XSS, RCE, etc.)

### Phase 5: Remediate
- Shows all issues sorted by priority
- Fetches detailed information for selected issue
- Analyzes affected code
- Proposes secure fix
- Applies fix with user approval
- Runs tests and updates Concert status

**Bob's Tools:**
- `execute_command` - Call Concert APIs via curl, run tests
- `read_file` / `search_files` - Analyze code
- `apply_diff` - Apply surgical security fixes

## Quick Start

1. **Configure Concert credentials** in `.env`:
   ```bash
   CONCERT_BASE_URL=https://<your-concert-host>:12443/concert/core/api/v1
   CONCERT_API_KEY=<base64-encoded-value>
   CONCERT_INSTANCE_ID=0000-0000-0000-0000
   ```
   
   **Important**:
   - API key must be base64-encoded `username:api_key`
   - Base URL must end with `/concert/core/api/v1`
   - Instance ID typically `0000-0000-0000-0000`

2. **Activate Security Remediation mode** in Bob

3. **Ask Bob to check for vulnerabilities**:
   ```
   "Check Concert for vulnerabilities"
   ```

4. **Bob will execute the 5-phase workflow**:
   - Test API connection
   - List all applications
   - Clone selected repository
   - Ask: CVEs or Exposures?
   - Show issues and fix them one by one

## Example Workflow

```
User: "Check Concert for vulnerabilities"

Bob:
🔍 Testing Concert API connection...
✅ Connected successfully!

📋 Applications in Concert:

| # | Application Name         | Criticality | CVEs | Exposures | Repository |
|---|-------------------------|-------------|------|-----------|------------|
| 1 | VulnerableSampleApp     | 3           | 0    | 15        | github.com/Client-Engineering-Indonesia/... |
| 2 | payment-service         | 5           | 3    | 8         | github.com/... |

Which application would you like to remediate? (Enter number)

User: "1"

Bob:
📦 Cloning VulnerableSampleApp...
✅ Repository cloned successfully

What would you like to fix?
1. CVEs (Dependency vulnerabilities)
2. SAST Exposures (Code-level issues)

User: "2"

Bob:
🔍 Fetching SAST exposures...

Found 15 exposures (3 Priority 1, 7 Priority 2, 5 Priority 3):

Priority 1 (Critical):
1. [RCE] rce.java.script-engine-eval - VulnerableApp.java:200
2. [SQL Injection] sqli.java.method-param-sql-concat - VulnerableApp.java:41
3. [XSS] xss.java.servlet-writer - VulnerableApp.java:120

Which exposure would you like to fix? (Enter number)

User: "1"

Bob:
📖 Analyzing exposure: rce.java.script-engine-eval

**Vulnerability**: Remote Code Execution via ScriptEngine
**File**: VulnerableApp.java:67
**Root Cause**: User input directly evaluated as JavaScript code

**Current Code**:
```java
String expression = request.getParameter("priceFormula");
ScriptEngine engine = manager.getEngineByName("JavaScript");
Double calculatedPrice = (Double) engine.eval(expression);
```

**Proposed Fix**:
Replace dynamic script execution with predefined operations:
- Add whitelist of allowed operations (add, multiply, discount)
- Use BiFunction map instead of eval()
- Validate operation parameter

Shall I apply this fix?

User: "Yes"

Bob:
✅ Fix applied to VulnerableApp.java
🧪 Running tests... All tests passed!
📝 Updating Concert status to "Resolved"

Exposure rce.java.script-engine-eval is now resolved.

Would you like to fix another exposure?
```

## Customization

You can customize these rules by:
- Adding new vulnerability types to remediation-strategies.md
- Updating Concert API patterns for your environment
- Adding organization-specific security guidelines

## Support

For questions or issues:
- Review the rules in this directory
- Check Concert API documentation
- Contact your Concert administrator for API access