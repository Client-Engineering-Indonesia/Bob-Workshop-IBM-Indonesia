# Vulnerable Java Application - Demo Script

⚠️ **WARNING: This application contains intentional security vulnerabilities for demonstration and educational purposes only. DO NOT use in production environments!**

## Overview

This Java application demonstrates common security vulnerabilities, SAST (Static Application Security Testing) issues, and SCA (Software Composition Analysis) problems that can be detected by security scanning tools. It's designed for:
- Security training and education
- Testing SAST and SCA tools
- Demonstrating vulnerability detection
- Security awareness demonstrations
- Software composition analysis testing

## Vulnerabilities Included

### 1. **SQL Injection (CWE-89)** - CRITICAL
- **Location**: `authenticateUser()` method
- **Issue**: User input directly concatenated into SQL query
- **Impact**: Database compromise, data theft, authentication bypass
- **Example**: `username = "admin' OR '1'='1"`

### 2. **Command Injection (CWE-78)** - CRITICAL
- **Location**: `executeSystemCommand()` method
- **Issue**: User input passed directly to system command
- **Impact**: Remote code execution, system compromise
- **Example**: `userInput = "google.com; rm -rf /"`

### 3. **Path Traversal (CWE-22)** - HIGH
- **Location**: `readFile()` method
- **Issue**: No validation of file paths
- **Impact**: Unauthorized file access
- **Example**: `filename = "../../etc/passwd"`

### 4. **XXE - XML External Entity (CWE-611)** - HIGH
- **Location**: `parseXML()` method
- **Issue**: XML parser allows external entities
- **Impact**: File disclosure, SSRF, DoS
- **Example**: XML with `<!ENTITY xxe SYSTEM "file:///etc/passwd">`

### 5. **Insecure Deserialization (CWE-502)** - CRITICAL
- **Location**: `deserializeObject()` method
- **Issue**: Deserializing untrusted data
- **Impact**: Remote code execution
- **CVE Reference**: Similar to CVE-2015-7501, CVE-2017-5638

### 6. **Weak Cryptography (CWE-327)** - HIGH
- **Location**: `encryptData()` method
- **Issue**: Using deprecated DES encryption
- **Impact**: Data can be easily decrypted
- **Recommendation**: Use AES-256-GCM

### 7. **Weak Hash Function (CWE-328)** - HIGH
- **Location**: `hashPassword()` method
- **Issue**: Using MD5 for password hashing
- **Impact**: Passwords can be cracked via rainbow tables
- **Recommendation**: Use bcrypt, scrypt, or Argon2

### 8. **LDAP Injection (CWE-90)** - HIGH
- **Location**: `searchLDAP()` method
- **Issue**: Unvalidated user input in LDAP query
- **Impact**: Unauthorized access, data disclosure

### 9. **Cross-Site Scripting - XSS (CWE-79)** - HIGH
- **Location**: `displayUserInput()` method
- **Issue**: Unescaped user input in HTML output
- **Impact**: Session hijacking, defacement
- **Example**: `userInput = "<script>alert('XSS')</script>"`

### 10. **Cross-Site Request Forgery - CSRF (CWE-352)** - MEDIUM
- **Location**: `transferMoney()` method
- **Issue**: No CSRF token validation
- **Impact**: Unauthorized actions on behalf of user

### 11. **Insecure Random (CWE-338)** - MEDIUM
- **Location**: `generateSessionToken()` method
- **Issue**: Using `java.util.Random` for security tokens
- **Impact**: Predictable tokens, session hijacking
- **Recommendation**: Use `SecureRandom`

### 12. **Information Exposure (CWE-209)** - MEDIUM
- **Location**: `handleError()` method
- **Issue**: Stack traces exposed to users
- **Impact**: Information leakage about system internals

### 13. **Unrestricted File Upload (CWE-434)** - CRITICAL
- **Location**: `uploadFile()` method
- **Issue**: No file type or content validation
- **Impact**: Malicious file upload, code execution

### 14. **Server-Side Request Forgery - SSRF (CWE-918)** - HIGH
- **Location**: `fetchURL()` method
- **Issue**: No URL validation
- **Impact**: Internal network scanning, data exfiltration
- **Example**: `url = "http://169.254.169.254/latest/meta-data/"`

### 15. **Code Injection (CWE-94)** - CRITICAL
- **Location**: `evaluateExpression()` method
- **Issue**: Evaluating user-supplied code
- **Impact**: Remote code execution

### 16. **Race Condition (CWE-362)** - MEDIUM
- **Location**: `withdraw()` method
- **Issue**: Non-thread-safe balance check
- **Impact**: Double-spending, data corruption

### 17. **Null Pointer Dereference (CWE-476)** - LOW
- **Location**: `getUserEmail()` method
- **Issue**: No null check before method call
- **Impact**: Application crash, DoS

### 18. **Resource Leak (CWE-404)** - MEDIUM
- **Location**: `readFileWithLeak()` method
- **Issue**: FileInputStream not closed
- **Impact**: Memory leak, resource exhaustion

### 19. **Insecure Cookie (CWE-614)** - MEDIUM
- **Location**: `setSessionCookie()` method
- **Issue**: Missing Secure and HttpOnly flags
- **Impact**: Session hijacking via XSS or network sniffing

### 20. **Trust Boundary Violation (CWE-501)** - MEDIUM
- **Location**: `storeUserData()` method
- **Issue**: Storing untrusted data without validation
- **Impact**: Data integrity issues

### 21. **Integer Overflow (CWE-190)** - MEDIUM
- **Location**: `calculateTotal()` method
- **Issue**: No overflow protection
- **Impact**: Incorrect calculations, financial loss

### 22. **Hard-coded Credentials (CWE-798)** - CRITICAL
- **Location**: Class constants and `authenticateAdmin()` method
- **Issue**: Passwords and API keys in source code
- **Impact**: Unauthorized access
- **Examples**: `DB_PASSWORD`, `API_KEY`, `SECRET_KEY`

### 23. **Improper Certificate Validation (CWE-295)** - HIGH
- **Location**: `makeHTTPSRequest()` method
- **Issue**: Disabled SSL certificate validation
- **Impact**: Man-in-the-middle attacks
- **CVE Reference**: Similar to CVE-2014-3566 (POODLE)

### 24. **Logging Sensitive Data (CWE-532)** - MEDIUM
- **Location**: `logUserCredentials()` method
- **Issue**: Passwords logged in plaintext
- **Impact**: Credential exposure in log files

### 25. **Missing Authentication (CWE-306)** - CRITICAL
- **Location**: `deleteUser()` method
- **Issue**: No authentication check before deletion
- **Impact**: Unauthorized data deletion

### 26. **Insufficient Session Expiration (CWE-613)** - MEDIUM
- **Location**: `createSession()` method
- **Issue**: Session never expires
- **Impact**: Increased window for session hijacking

## Usage for Testing

### Compile the Application
```bash
javac VulnerableApp.java
```

### Run SAST Tools

#### Using Semgrep
```bash
semgrep --config=auto VulnerableApp.java --json > semgrep-results.json
```

#### Using SpotBugs
```bash
spotbugs -textui -effort:max VulnerableApp.class
```

#### Using SonarQube
```bash
sonar-scanner -Dsonar.projectKey=vulnerable-java-demo \
  -Dsonar.sources=. \
  -Dsonar.host.url=http://localhost:9000
```

#### Using Checkmarx
Upload the file to your Checkmarx instance for scanning.

#### Using Snyk Code
```bash
snyk code test VulnerableApp.java
```

## Expected SAST Findings

A comprehensive SAST tool should detect:
- 26+ security vulnerabilities
- Multiple CWE categories
- Critical, High, Medium, and Low severity issues
- OWASP Top 10 violations
- PCI-DSS compliance violations
- SANS Top 25 issues

## Remediation Examples

### SQL Injection Fix
```java
// VULNERABLE
String query = "SELECT * FROM users WHERE username='" + username + "'";

// SECURE - Use PreparedStatement
String query = "SELECT * FROM users WHERE username=?";
PreparedStatement pstmt = conn.prepareStatement(query);
pstmt.setString(1, username);
```

### Command Injection Fix
```java
// VULNERABLE
Runtime.getRuntime().exec("ping -c 4 " + userInput);

// SECURE - Use ProcessBuilder with argument list
ProcessBuilder pb = new ProcessBuilder("ping", "-c", "4", userInput);
Process process = pb.start();
```

### Weak Cryptography Fix
```java
// VULNERABLE
KeyGenerator keyGen = KeyGenerator.getInstance("DES");

// SECURE
KeyGenerator keyGen = KeyGenerator.getInstance("AES");
keyGen.init(256);
```

## Software Composition Analysis (SCA) Issues

The `pom.xml` file includes 30+ vulnerable and outdated dependencies:

### Critical Vulnerabilities

1. **Log4j 2.14.1** - Log4Shell
   - CVE-2021-44228 (CVSS 10.0)
   - CVE-2021-45046 (CVSS 9.0)
   - Remote Code Execution

2. **Apache Struts 2.3.20**
   - CVE-2017-5638 (CVSS 10.0)
   - Remote Code Execution
   - End of Life

3. **Apache Commons Collections 3.2.1**
   - CVE-2015-7501 (CVSS 7.5)
   - Insecure Deserialization

4. **H2 Database 1.4.197**
   - CVE-2018-10054 (CVSS 9.8)
   - CVE-2021-42392 (CVSS 9.8)
   - Remote Code Execution

5. **XStream 1.4.10**
   - CVE-2020-26217 (CVSS 8.5)
   - Multiple deserialization CVEs

### High Severity Vulnerabilities

6. **Spring Framework 4.3.0**
   - CVE-2018-1258, CVE-2018-1270
   - End of Life

7. **Jackson Databind 2.9.8**
   - Multiple deserialization CVEs
   - CVE-2019-12384, CVE-2019-14540

8. **MySQL Connector 5.1.39**
   - Multiple CVEs
   - End of Life

9. **Apache Tomcat 8.5.31**
   - CVE-2019-0199, CVE-2019-0221

10. **Jetty 9.3.8**
    - CVE-2017-7656, CVE-2017-7657

11. **SnakeYAML 1.26**
    - CVE-2022-25857, CVE-2022-38749

12. **Apache Shiro 1.4.0**
    - CVE-2020-11989

13. **Netty 4.1.42**
    - CVE-2021-21290, CVE-2021-21295

14. **PostgreSQL JDBC 42.2.5**
    - CVE-2020-13692

### Medium Severity & End-of-Life

15. **Apache Commons FileUpload 1.3.1** - CVE-2016-1000031
16. **Apache Commons Compress 1.18** - CVE-2019-12402
17. **Hibernate 4.3.6** - CVE-2019-14900
18. **Apache HttpClient 4.3.6** - CVE-2015-5262
19. **Gson 2.8.5** - CVE-2022-25647
20. **Apache POI 3.17** - CVE-2019-12415
21. **JUnit 4.12** - CVE-2020-15250
22. **Apache Velocity 1.7** - CVE-2020-13936
23. **Apache CXF 3.2.5** - CVE-2019-12406
24. **Apache Kafka 2.3.0** - CVE-2019-12399
25. **Apache Ant 1.9.9** - CVE-2020-1945
26. **Bouncy Castle 1.60** - CVE-2020-15522
27. **Apache Santuario 2.1.3** - CVE-2019-12400
28. **Undertow 2.0.26** - CVE-2020-10687
29. **Apache Tika 1.20** - CVE-2020-9489
30. **Servlet API 3.1.0** - End of Life
31. **JSP API 2.3.1** - End of Life

## Usage for Testing

### Build with Maven
```bash
mvn clean compile
```

### Run SAST Tools

#### Using Semgrep
```bash
semgrep --config=auto VulnerableApp.java --json > semgrep-results.json
```

#### Using SpotBugs
```bash
mvn spotbugs:check
```

#### Using SonarQube
```bash
mvn sonar:sonar \
  -Dsonar.projectKey=vulnerable-java-demo \
  -Dsonar.host.url=http://localhost:9000
```

#### Using Checkmarx
Upload the project to your Checkmarx instance for scanning.

#### Using Snyk Code (SAST)
```bash
snyk code test
```

### Run SCA Tools

#### Using OWASP Dependency-Check
```bash
mvn org.owasp:dependency-check-maven:check
```

#### Using Snyk Open Source (SCA)
```bash
snyk test --all-projects
```

#### Using JFrog Xray
```bash
jfrog rt mvn-config
jfrog rt mvn clean install
```

#### Using Mend (WhiteSource)
```bash
java -jar wss-unified-agent.jar -c wss-unified-agent.config
```

#### Using Sonatype Nexus IQ
```bash
mvn com.sonatype.clm:clm-maven-plugin:evaluate
```

## Expected Findings

### SAST Findings
A comprehensive SAST tool should detect:
- 26+ security vulnerabilities
- Multiple CWE categories
- Critical, High, Medium, and Low severity issues
- OWASP Top 10 violations
- PCI-DSS compliance violations
- SANS Top 25 issues

### SCA Findings
A comprehensive SCA tool should detect:
- 30+ vulnerable dependencies
- 50+ CVEs across all dependencies
- Multiple CVSS 9.0+ critical vulnerabilities
- End-of-life components
- License compliance issues
- Transitive dependency vulnerabilities


## Related CVEs

This application demonstrates vulnerabilities similar to:
- **CVE-2021-44228** (Log4Shell) - Code injection patterns
- **CVE-2017-5638** (Apache Struts) - Deserialization
- **CVE-2014-0160** (Heartbleed) - Information disclosure patterns
- **CVE-2015-7501** (JBoss) - Insecure deserialization
- **CVE-2019-11358** (jQuery) - XSS patterns

## Disclaimer

This code is intentionally vulnerable and should NEVER be used in production. It is designed solely for:
- Educational purposes
- Security tool testing
- Vulnerability demonstration
- Security awareness training

## License

This demo code is provided as-is for educational purposes only.

## Author

Created for security demonstration and SAST tool testing purposes.
