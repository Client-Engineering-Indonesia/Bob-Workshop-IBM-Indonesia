# Remediation Strategies for Common Vulnerabilities

## Overview

This guide provides proven fix patterns for common security vulnerabilities detected by Concert.

## SQL Injection (CWE-89)

### Vulnerability Pattern

```java
// VULNERABLE CODE
String username = request.getParameter("username");
String query = "SELECT * FROM users WHERE username='" + username + "'";
Statement stmt = connection.createStatement();
ResultSet rs = stmt.executeQuery(query);
```

### Fix Strategy

**Use PreparedStatement with parameterized queries:**

```java
// SECURE CODE
String username = request.getParameter("username");
String query = "SELECT * FROM users WHERE username=?";
PreparedStatement pstmt = connection.prepareStatement(query);
pstmt.setString(1, username);
ResultSet rs = pstmt.executeQuery();
```

### Additional Measures

1. **Input Validation**: Validate username format
2. **ORM Framework**: Consider using JPA/Hibernate
3. **Stored Procedures**: Use for complex queries
4. **Least Privilege**: Database user should have minimal permissions

## Cross-Site Scripting (XSS) (CWE-79)

### Vulnerability Pattern

```java
// VULNERABLE CODE
String userComment = request.getParameter("comment");
out.println("<div>" + userComment + "</div>");
```

### Fix Strategy

**Use output encoding:**

```java
// SECURE CODE
String userComment = request.getParameter("comment");
String safeComment = StringEscapeUtils.escapeHtml4(userComment);
out.println("<div>" + safeComment + "</div>");
```

### Framework-Specific Solutions

**JSP/JSTL:**
```jsp
<!-- Use c:out for automatic escaping -->
<c:out value="${userComment}" />
```

**Spring:**
```java
// Spring automatically escapes in Thymeleaf
<p th:text="${userComment}"></p>
```

### Additional Measures

1. **Content Security Policy**: Add CSP headers
2. **Input Validation**: Sanitize on input
3. **Context-Aware Encoding**: Different encoding for HTML, JavaScript, URL

## Path Traversal (CWE-22)

### Vulnerability Pattern

```java
// VULNERABLE CODE
String filename = request.getParameter("file");
File file = new File("/uploads/" + filename);
FileInputStream fis = new FileInputStream(file);
```

### Fix Strategy

**Validate and sanitize file paths:**

```java
// SECURE CODE
String filename = request.getParameter("file");

// Reject path traversal attempts
if (filename.contains("..") || filename.contains("/") || filename.contains("\\")) {
    throw new SecurityException("Invalid filename");
}

// Whitelist allowed characters
filename = filename.replaceAll("[^a-zA-Z0-9._-]", "");

// Use canonical path to prevent bypasses
File uploadDir = new File("/uploads/").getCanonicalFile();
File file = new File(uploadDir, filename).getCanonicalFile();

// Verify file is within upload directory
if (!file.getPath().startsWith(uploadDir.getPath())) {
    throw new SecurityException("Access denied");
}

FileInputStream fis = new FileInputStream(file);
```

### Additional Measures

1. **Whitelist Approach**: Only allow specific filenames
2. **UUID Filenames**: Generate random filenames
3. **Separate Storage**: Store files outside web root

## Insecure Deserialization (CWE-502)

### Vulnerability Pattern

```java
// VULNERABLE CODE
ObjectInputStream ois = new ObjectInputStream(request.getInputStream());
Object obj = ois.readObject();
```

### Fix Strategy

**Validate before deserializing:**

```java
// SECURE CODE
// Option 1: Use safe serialization format (JSON)
ObjectMapper mapper = new ObjectMapper();
MyObject obj = mapper.readValue(request.getInputStream(), MyObject.class);

// Option 2: If must use Java serialization, validate class
ObjectInputStream ois = new ObjectInputStream(request.getInputStream()) {
    @Override
    protected Class<?> resolveClass(ObjectStreamClass desc) 
            throws IOException, ClassNotFoundException {
        // Whitelist allowed classes
        if (!desc.getName().equals("com.myapp.SafeClass")) {
            throw new InvalidClassException("Unauthorized deserialization attempt");
        }
        return super.resolveClass(desc);
    }
};
Object obj = ois.readObject();
```

### Additional Measures

1. **Avoid Java Serialization**: Use JSON, XML, or Protocol Buffers
2. **Sign Serialized Data**: Verify integrity
3. **Network Segmentation**: Limit who can send serialized data

## Authentication Bypass (CWE-287)

### Vulnerability Pattern

```java
// VULNERABLE CODE
String username = request.getParameter("username");
String password = request.getParameter("password");

if (password.equals("admin123")) {  // Hardcoded password
    session.setAttribute("user", username);
}
```

### Fix Strategy

**Use secure authentication:**

```java
// SECURE CODE
String username = request.getParameter("username");
String password = request.getParameter("password");

// Hash password with salt
String hashedPassword = BCrypt.hashpw(password, BCrypt.gensalt());

// Verify against stored hash
User user = userRepository.findByUsername(username);
if (user != null && BCrypt.checkpw(password, user.getPasswordHash())) {
    // Create secure session
    session.setAttribute("userId", user.getId());
    session.setAttribute("authenticated", true);
    session.setMaxInactiveInterval(1800); // 30 minutes
}
```

### Additional Measures

1. **Multi-Factor Authentication**: Add second factor
2. **Rate Limiting**: Prevent brute force
3. **Account Lockout**: Lock after failed attempts
4. **Secure Session Management**: Use framework features

## Weak Cryptography (CWE-327)

### Vulnerability Pattern

```java
// VULNERABLE CODE
MessageDigest md = MessageDigest.getInstance("MD5");
byte[] hash = md.digest(password.getBytes());
```

### Fix Strategy

**Use strong algorithms:**

```java
// SECURE CODE
// For password hashing, use BCrypt
String hashedPassword = BCrypt.hashpw(password, BCrypt.gensalt(12));

// For general hashing, use SHA-256 or better
MessageDigest md = MessageDigest.getInstance("SHA-256");
byte[] hash = md.digest(data.getBytes(StandardCharsets.UTF_8));

// For encryption, use AES-256
Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
SecretKeySpec keySpec = new SecretKeySpec(key, "AES");
GCMParameterSpec gcmSpec = new GCMParameterSpec(128, iv);
cipher.init(Cipher.ENCRYPT_MODE, keySpec, gcmSpec);
byte[] encrypted = cipher.doFinal(plaintext.getBytes());
```

### Additional Measures

1. **Key Management**: Use secure key storage
2. **Regular Rotation**: Rotate keys periodically
3. **Use Libraries**: Don't implement crypto yourself

## Command Injection (CWE-78)

### Vulnerability Pattern

```java
// VULNERABLE CODE
String filename = request.getParameter("file");
Runtime.getRuntime().exec("cat " + filename);
```

### Fix Strategy

**Avoid shell execution, use APIs:**

```java
// SECURE CODE
String filename = request.getParameter("file");

// Validate filename
if (!filename.matches("[a-zA-Z0-9._-]+")) {
    throw new SecurityException("Invalid filename");
}

// Use Java API instead of shell command
Path path = Paths.get("/safe/directory", filename);
String content = Files.readString(path);
```

### If Shell Execution Required

```java
// Use ProcessBuilder with argument array (no shell interpretation)
ProcessBuilder pb = new ProcessBuilder("cat", filename);
pb.directory(new File("/safe/directory"));
Process process = pb.start();
```

### Additional Measures

1. **Avoid Shell**: Use language APIs
2. **Input Validation**: Strict whitelist
3. **Least Privilege**: Run with minimal permissions

## LDAP Injection (CWE-90)

### Vulnerability Pattern

```java
// VULNERABLE CODE
String username = request.getParameter("username");
String filter = "(uid=" + username + ")";
NamingEnumeration results = ctx.search("ou=users", filter, controls);
```

### Fix Strategy

**Escape LDAP special characters:**

```java
// SECURE CODE
String username = request.getParameter("username");

// Escape LDAP special characters
String escapedUsername = escapeLDAPSearchFilter(username);
String filter = "(uid=" + escapedUsername + ")";
NamingEnumeration results = ctx.search("ou=users", filter, controls);

// Escape function
private String escapeLDAPSearchFilter(String filter) {
    StringBuilder sb = new StringBuilder();
    for (char c : filter.toCharArray()) {
        switch (c) {
            case '\\': sb.append("\\5c"); break;
            case '*':  sb.append("\\2a"); break;
            case '(':  sb.append("\\28"); break;
            case ')':  sb.append("\\29"); break;
            case '\0': sb.append("\\00"); break;
            default:   sb.append(c);
        }
    }
    return sb.toString();
}
```

## XML External Entity (XXE) (CWE-611)

### Vulnerability Pattern

```java
// VULNERABLE CODE
DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
DocumentBuilder builder = factory.newDocumentBuilder();
Document doc = builder.parse(request.getInputStream());
```

### Fix Strategy

**Disable external entities:**

```java
// SECURE CODE
DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();

// Disable external entities
factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
factory.setFeature("http://xml.org/sax/features/external-general-entities", false);
factory.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
factory.setFeature("http://apache.org/xml/features/nonvalidating/load-external-dtd", false);
factory.setXIncludeAware(false);
factory.setExpandEntityReferences(false);

DocumentBuilder builder = factory.newDocumentBuilder();
Document doc = builder.parse(request.getInputStream());
```

## Remote Code Execution via ScriptEngine (CWE-94)

### Vulnerability Pattern

```java
// VULNERABLE CODE
String userScript = request.getParameter("script");
ScriptEngineManager manager = new ScriptEngineManager();
ScriptEngine engine = manager.getEngineByName("JavaScript");
Object result = engine.eval(userScript);
```

### Fix Strategy

**Avoid dynamic script execution entirely:**

```java
// SECURE CODE - Option 1: Remove dynamic scripting
// Replace with predefined, safe operations
Map<String, Function<String, String>> allowedOperations = new HashMap<>();
allowedOperations.put("uppercase", String::toUpperCase);
allowedOperations.put("lowercase", String::toLowerCase);

String operation = request.getParameter("operation");
String input = request.getParameter("input");

if (!allowedOperations.containsKey(operation)) {
    throw new SecurityException("Operation not allowed");
}

String result = allowedOperations.get(operation).apply(input);
```

**If scripting is absolutely required:**

```java
// SECURE CODE - Option 2: Sandboxed execution with strict validation
String userScript = request.getParameter("script");

// Whitelist allowed operations only
if (!userScript.matches("^[a-zA-Z0-9\\s+\\-*/()]+$")) {
    throw new SecurityException("Invalid script syntax");
}

// Use sandboxed environment with restricted permissions
ScriptEngineManager manager = new ScriptEngineManager();
ScriptEngine engine = manager.getEngineByName("JavaScript");

// Restrict access to Java classes
engine.getContext().setAttribute("polyglot.js.allowHostAccess", false, ScriptContext.ENGINE_SCOPE);
engine.getContext().setAttribute("polyglot.js.allowHostClassLookup", false, ScriptContext.ENGINE_SCOPE);

// Set timeout to prevent DoS
ExecutorService executor = Executors.newSingleThreadExecutor();
Future<Object> future = executor.submit(() -> engine.eval(userScript));

try {
    Object result = future.get(5, TimeUnit.SECONDS);
} catch (TimeoutException e) {
    future.cancel(true);
    throw new SecurityException("Script execution timeout");
}
```

### Additional Measures

1. **Eliminate Dynamic Execution**: Replace with predefined operations
2. **Input Validation**: Strict whitelist of allowed characters
3. **Sandboxing**: Disable access to Java classes and system resources
4. **Timeout Protection**: Prevent infinite loops and DoS
5. **Audit Logging**: Log all script execution attempts
6. **Least Privilege**: Run with minimal permissions

### Real-World Example (VulnerableSampleApp)

**Vulnerable Code:**
```java
// VulnerableApp.java:200
String expression = request.getParameter("priceFormula");
ScriptEngineManager manager = new ScriptEngineManager();
ScriptEngine engine = manager.getEngineByName("JavaScript");
Double calculatedPrice = (Double) engine.eval(expression);
```

**Secure Fix:**
```java
// VulnerableApp.java:200
String operation = request.getParameter("operation");
Double basePrice = Double.parseDouble(request.getParameter("basePrice"));
Double modifier = Double.parseDouble(request.getParameter("modifier"));

// Whitelist allowed operations
Map<String, BiFunction<Double, Double, Double>> operations = new HashMap<>();
operations.put("add", (a, b) -> a + b);
operations.put("multiply", (a, b) -> a * b);
operations.put("discount", (a, b) -> a * (1 - b / 100));

if (!operations.containsKey(operation)) {
    throw new IllegalArgumentException("Invalid operation");
}

Double calculatedPrice = operations.get(operation).apply(basePrice, modifier);
```

## General Security Principles

### Defense in Depth

Apply multiple layers of security:
1. **Input Validation**: Validate all user input
2. **Output Encoding**: Encode all output
3. **Parameterization**: Use parameterized queries/commands
4. **Least Privilege**: Minimal permissions
5. **Error Handling**: Don't leak sensitive information

### Secure Coding Checklist

Before applying any fix, verify:
- [ ] Input is validated
- [ ] Output is encoded
- [ ] Queries are parameterized
- [ ] Errors don't leak information
- [ ] Logging captures security events
- [ ] Tests cover security scenarios
- [ ] Documentation explains security measures

### Testing Security Fixes

1. **Positive Tests**: Verify normal functionality works
2. **Negative Tests**: Verify attacks are blocked
3. **Edge Cases**: Test boundary conditions
4. **Regression Tests**: Ensure no new vulnerabilities

## Resources

- **OWASP Top 10**: https://owasp.org/www-project-top-ten/
- **CWE Top 25**: https://cwe.mitre.org/top25/
- **OWASP Cheat Sheets**: https://cheatsheetseries.owasp.org/
- **Secure Coding Guidelines**: https://www.securecoding.cert.org/