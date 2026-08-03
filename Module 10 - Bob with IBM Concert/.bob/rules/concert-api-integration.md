# Concert API Integration Patterns

## Overview

This guide explains how to interact with IBM Concert's REST API to fetch vulnerability data, CVE details, and update remediation status.

## Authentication

Concert uses a **custom authentication format** with `C_API_KEY` prefix (NOT standard Bearer token).

### Environment Variables

Configure these environment variables in your `.env` file:

```bash
# Required
CONCERT_BASE_URL=https://your-concert-instance.ibm.com/concert/core/api/v1
CONCERT_API_KEY=base64_encoded_username_colon_apikey
CONCERT_INSTANCE_ID=0000-0000-0000-0000
```

**Where to get your credentials:**
- **API Key**: Log into IBM Concert → Settings → API Keys → Generate new key
  - Format: Base64-encoded `username:api_key`
  - Example: `concertuser:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` → `<base64-encoded-value>`
- **Instance ID**: Provided by your Concert administrator (typically `0000-0000-0000-0000`)
- **Base URL**: Your Concert instance URL + `/concert/core/api/v1`
  - Example: `https://<your-concert-host>:12443/concert/core/api/v1`

### Authentication Headers

**CRITICAL**: Concert uses a custom authentication format that differs from standard REST APIs:

```bash
-H "Authorization: C_API_KEY ${CONCERT_API_KEY}"
-H "InstanceId: ${CONCERT_INSTANCE_ID}"
-H "Content-Type: application/json"
```

**Important Notes:**
- Authorization header uses `C_API_KEY` prefix (NOT `Bearer`)
- InstanceId header is required for all API calls
- Always use HTTPS with `-k` flag if using self-signed certificates
- API key must be base64-encoded `username:api_key`

### Working Example

```bash
# Load environment variables
source .env

# Test API connection
curl -s -k -X GET "${CONCERT_BASE_URL}/applications?page_size=1" \
  -H "Authorization: C_API_KEY ${CONCERT_API_KEY}" \
  -H "InstanceId: ${CONCERT_INSTANCE_ID}"
```

## API Endpoints

### 1. List Applications

Fetch all applications monitored by Concert.

**Endpoint:** `GET /applications`

**Query Parameters:**
- `page_size`: Number of results per page (default: 20, max: 100)
- `page`: Page number (default: 1)

**Example:**

```bash
curl -s -k -X GET "${CONCERT_BASE_URL}/applications?page_size=100" \
  -H "Authorization: C_API_KEY ${CONCERT_API_KEY}" \
  -H "InstanceId: ${CONCERT_INSTANCE_ID}"
```

**Response:**

```json
{
  "applications": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "VulnerableSampleApp",
      "criticality": 3,
      "cve_count": 0,
      "exposure_count": 15,
      "repository_url": "https://github.com/Client-Engineering-Indonesia/VulnerableSampleApp",
      "last_scan": "2024-05-22T10:30:00Z"
    }
  ],
  "total": 25,
  "page": 1,
  "page_size": 100
}
```

**Key Fields:**
- `criticality`: Business importance (0-5, manual) - INDEPENDENT of CVE/exposure counts
- `cve_count`: Number of known dependency vulnerabilities
- `exposure_count`: Number of SAST findings in source code

### 2. Get Application CVEs

Fetch CVEs (dependency vulnerabilities) for a specific application.

**Endpoint:** `GET /applications/{application-id}/cves`

**Example:**

```bash
curl -s -k -X GET "${CONCERT_BASE_URL}/applications/550e8400-e29b-41d4-a716-446655440000/cves" \
  -H "Authorization: C_API_KEY ${CONCERT_API_KEY}" \
  -H "InstanceId: ${CONCERT_INSTANCE_ID}"
```

**Response:**

```json
{
  "cves": [
    {
      "cve_id": "CVE-2024-1234",
      "severity": "critical",
      "cvss_score": 9.8,
      "priority": "Priority 1",
      "affected_component": "log4j-core",
      "affected_version": "2.14.1",
      "fixed_version": "2.17.1",
      "description": "Remote code execution via JNDI lookup"
    }
  ],
  "total": 5
}
```

### 3. Get Application Exposures

Fetch SAST exposures (code-level vulnerabilities) for a specific application.

**Endpoint:** `GET /applications/{application-id}/exposures`

**Example:**

```bash
curl -s -k -X GET "${CONCERT_BASE_URL}/applications/550e8400-e29b-41d4-a716-446655440000/exposures" \
  -H "Authorization: C_API_KEY ${CONCERT_API_KEY}" \
  -H "InstanceId: ${CONCERT_INSTANCE_ID}"
```

**Response:**

```json
{
  "exposures": [
    {
      "id": "8bf0d5cc-321d-41c6-a876-8266869873ee",
      "rule_id": "sqli.java.method-param-sql-concat",
      "severity": "error",
      "priority": "Priority 1",
      "exposure_object_id": "https://github.com/Client-Engineering-Indonesia/VulnerableSampleApp",
      "solution": "Method parameter concatenated into SQL query string. Use PreparedStatement instead.",
      "occurrence_count": 2,
      "assessment_status": "Open",
      "file_path": "src/main/java/com/vulnerableapp/VulnerableApp.java",
      "line_number": 45
    }
  ],
  "total": 15
}
```

**Assessment Status Values:**
- `Open`: Not yet addressed
- `In Progress`: Currently being fixed
- `Resolved`: Fixed and verified
- `False Positive`: Not a real vulnerability

### 4. Get CVE Details

Fetch detailed information about a specific CVE.

**Endpoint:** `GET /vulnerability/cves?cve_id={cve-id}`

**Example:**

```bash
curl -s -k -X GET "${CONCERT_BASE_URL}/vulnerability/cves?cve_id=CVE-2024-1234" \
  -H "Authorization: C_API_KEY ${CONCERT_API_KEY}" \
  -H "InstanceId: ${CONCERT_INSTANCE_ID}"
```

**Response:**

```json
{
  "cves": [
    {
      "cve_id": "CVE-2024-1234",
      "description": "Remote code execution vulnerability in Log4j",
      "published_date": "2024-04-01T00:00:00Z",
      "cvss_v3_score": 9.8,
      "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
      "cwe": ["CWE-502"],
      "references": [
        "https://nvd.nist.gov/vuln/detail/CVE-2024-1234"
      ],
      "remediation": "Upgrade to Log4j 2.17.1 or later"
    }
  ]
}
```

### 5. Get Exposure Details

Fetch detailed information about a specific SAST exposure.

**Endpoint:** `GET /vulnerability/exposures/{exposure-id}`

**Example:**

```bash
curl -s -k -X GET "${CONCERT_BASE_URL}/vulnerability/exposures/8bf0d5cc-321d-41c6-a876-8266869873ee" \
  -H "Authorization: C_API_KEY ${CONCERT_API_KEY}" \
  -H "InstanceId: ${CONCERT_INSTANCE_ID}"
```

**Response:**

```json
{
  "id": "8bf0d5cc-321d-41c6-a876-8266869873ee",
  "rule_id": "sqli.java.method-param-sql-concat",
  "rule_name": "SQL Injection via String Concatenation",
  "severity": "error",
  "priority": "Priority 1",
  "cwe": "CWE-89",
  "description": "User input is concatenated directly into SQL query, allowing SQL injection attacks",
  "solution": "Use PreparedStatement with parameterized queries instead of string concatenation",
  "file_path": "src/main/java/com/vulnerableapp/VulnerableApp.java",
  "line_number": 45,
  "code_snippet": "String query = \"SELECT * FROM products WHERE id=\" + productId;",
  "remediation_example": "PreparedStatement pstmt = conn.prepareStatement(\"SELECT * FROM products WHERE id=?\");\npstmt.setString(1, productId);",
  "assessment_status": "Open",
  "occurrence_count": 2
}
```

### 6. Update Exposure Status

Update the assessment status of an exposure after remediation.

**Endpoint:** `PATCH /vulnerability/exposures/{exposure-id}`

**Example:**

```bash
curl -s -k -X PATCH "${CONCERT_BASE_URL}/vulnerability/exposures/8bf0d5cc-321d-41c6-a876-8266869873ee" \
  -H "Authorization: C_API_KEY ${CONCERT_API_KEY}" \
  -H "InstanceId: ${CONCERT_INSTANCE_ID}" \
  -H "Content-Type: application/json" \
  -d '{
    "assessment_status": "Resolved",
    "resolution_notes": "Fixed SQL injection by replacing string concatenation with PreparedStatement. All tests passing.",
    "resolved_by": "bob-security-remediation-mode",
    "resolved_date": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"
  }'
```

**Response:**

```json
{
  "success": true,
  "exposure_id": "8bf0d5cc-321d-41c6-a876-8266869873ee",
  "assessment_status": "Resolved",
  "updated_at": "2024-05-22T14:30:00Z"
}
```

## Error Handling

### Common HTTP Status Codes

- **200 OK**: Request successful
- **400 Bad Request**: Invalid request parameters
- **401 Unauthorized**: Invalid or expired API key
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Concert server error

### Error Response Format

```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid API key or expired token",
    "details": "Please check your CONCERT_API_KEY in .env file"
  }
}
```

### Handling Errors in Bob

When calling Concert API via `execute_command`, always check the response:

1. **Check HTTP status code** in the curl output
2. **Parse JSON response** to check for error field
3. **Provide helpful error messages** to the user
4. **Suggest fixes** (e.g., "Check your API key in .env")

Example error handling:

```bash
# Add -w "\n%{http_code}" to get status code
response=$(curl -s -k -w "\n%{http_code}" -X GET "${CONCERT_BASE_URL}/applications?page_size=1" \
  -H "Authorization: C_API_KEY ${CONCERT_API_KEY}" \
  -H "InstanceId: ${CONCERT_INSTANCE_ID}")

# Extract status code (last line)
status_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$status_code" != "200" ]; then
  echo "Error: Concert API returned status $status_code"
  echo "$body"
  exit 1
fi
```

## Best Practices

### 1. Use Silent Mode

Always use `-s` flag with curl to suppress progress output:

```bash
curl -s -X GET ...
```

### 2. Parse JSON Responses

Use `jq` to parse JSON responses when available:

```bash
curl -s ... | jq '.vulnerabilities[] | select(.severity == "critical")'
```

### 3. Handle Rate Limits

Concert may rate-limit API calls. Implement exponential backoff:

- First retry: Wait 1 second
- Second retry: Wait 2 seconds
- Third retry: Wait 4 seconds
- After 3 retries: Report error to user

### 4. Cache CVE Details

CVE details don't change frequently. Consider caching them to reduce API calls.

### 5. Batch Updates

When fixing multiple vulnerabilities, update Concert status in batches rather than one at a time.

### 6. Validate Environment Variables

Before making API calls, verify that required environment variables are set:

```bash
if [ -z "$CONCERT_BASE_URL" ] || [ -z "$CONCERT_API_KEY" ]; then
  echo "Error: Concert credentials not configured"
  echo "Please set CONCERT_BASE_URL and CONCERT_API_KEY in .env file"
  exit 1
fi
```

## Testing API Connectivity

Before starting vulnerability remediation, test Concert API connectivity:

```bash
# Test API connectivity
curl -s -k -X GET "${CONCERT_BASE_URL}/applications?page_size=1" \
  -H "Authorization: C_API_KEY ${CONCERT_API_KEY}" \
  -H "InstanceId: ${CONCERT_INSTANCE_ID}"
```

Expected response:

```json
{
  "applications": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "VulnerableSampleApp",
      "criticality": 3,
      "cve_count": 0,
      "exposure_count": 15
    }
  ],
  "total": 25
}
```

## Security Considerations

1. **Never log API keys** - They should only be in environment variables
2. **Use HTTPS** - Always use https:// for Concert API calls
3. **Validate responses** - Don't trust API responses blindly
4. **Timeout requests** - Use `--max-time 30` to prevent hanging
5. **Audit trail** - Log all API interactions for compliance

## Example: Complete Workflow

Here's a complete example of fetching and processing vulnerabilities:

```bash
#!/bin/bash

# Load environment variables
source .env

# Fetch all applications
echo "Fetching applications from Concert..."
response=$(curl -s -k -X GET "${CONCERT_BASE_URL}/applications?page_size=100" \
  -H "Authorization: C_API_KEY ${CONCERT_API_KEY}" \
  -H "InstanceId: ${CONCERT_INSTANCE_ID}")

# Parse and display
echo "$response" | jq -r '.applications[] | "[\(.criticality)] \(.name) - v\(.version) (updated: \(.last_updated_on))"'

# Get first application ID
app_id=$(echo "$response" | jq -r '.applications[0].id')

echo "Fetching exposures for application $app_id..."
exposures=$(curl -s -k -X GET "${CONCERT_BASE_URL}/applications/${app_id}/exposures" \
  -H "Authorization: C_API_KEY ${CONCERT_API_KEY}" \
  -H "InstanceId: ${CONCERT_INSTANCE_ID}")

# Show Priority 1 exposures
echo "$exposures" | jq -r '.exposures[] | select(.priority == "Priority 1") | "[\(.severity)] \(.rule_id)"'
```

This workflow demonstrates proper error handling, JSON parsing, and API interaction patterns with the correct Concert authentication.