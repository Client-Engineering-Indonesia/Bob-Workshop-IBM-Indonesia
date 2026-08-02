import java.io.*;
import java.net.*;
import java.sql.*;
import java.util.*;
import javax.servlet.http.*;
import javax.crypto.*;
import javax.crypto.spec.*;
import java.security.*;
import java.util.logging.*;
import javax.xml.parsers.*;
import org.w3c.dom.*;
import java.nio.file.*;
import javax.script.*;

/**
 * VULNERABLE JAVA APPLICATION - FOR DEMO PURPOSES ONLY
 * This application contains intentional security vulnerabilities
 * DO NOT USE IN PRODUCTION
 */
public class VulnerableApp {
    
    // Hardcoded credentials (CWE-798)
    private static final String DB_PASSWORD = "admin123";
    private static final String API_KEY = "sk-1234567890abcdef";
    private static final String SECRET_KEY = "MySecretKey123!";
    
    // Insecure random number generator (CWE-330)
    private static Random random = new Random();
    
    // SQL Injection vulnerability (CWE-89)
    public User authenticateUser(String username, String password) throws SQLException {
        Connection conn = DriverManager.getConnection(
            "jdbc:mysql://localhost:3306/mydb", 
            "root", 
            DB_PASSWORD
        );
        
        // Vulnerable to SQL injection
        String query = "SELECT * FROM users WHERE username='" + username + 
                      "' AND password='" + password + "'";
        Statement stmt = conn.createStatement();
        ResultSet rs = stmt.executeQuery(query);
        
        if (rs.next()) {
            return new User(rs.getString("username"), rs.getString("email"));
        }
        return null;
    }
    
    // Command Injection vulnerability (CWE-78)
    public String executeSystemCommand(String userInput) throws IOException {
        // Vulnerable to command injection
        Process process = Runtime.getRuntime().exec("ping -c 4 " + userInput);
        BufferedReader reader = new BufferedReader(
            new InputStreamReader(process.getInputStream())
        );
        
        StringBuilder output = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            output.append(line).append("\n");
        }
        return output.toString();
    }
    
    // Path Traversal vulnerability (CWE-22)
    public String readFile(String filename) throws IOException {
        // Vulnerable to path traversal
        File file = new File("/var/www/uploads/" + filename);
        BufferedReader reader = new BufferedReader(new FileReader(file));
        
        StringBuilder content = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            content.append(line).append("\n");
        }
        reader.close();
        return content.toString();
    }
    
    // XXE (XML External Entity) vulnerability (CWE-611)
    public Document parseXML(String xmlContent) throws Exception {
        DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
        // XXE vulnerability - external entities not disabled
        DocumentBuilder builder = factory.newDocumentBuilder();
        return builder.parse(new ByteArrayInputStream(xmlContent.getBytes()));
    }
    
    // Insecure Deserialization (CWE-502)
    public Object deserializeObject(byte[] data) throws Exception {
        ByteArrayInputStream bis = new ByteArrayInputStream(data);
        ObjectInputStream ois = new ObjectInputStream(bis);
        // Vulnerable to deserialization attacks
        return ois.readObject();
    }
    
    // Weak Cryptography (CWE-327)
    public String encryptData(String data) throws Exception {
        // Using weak DES encryption
        KeyGenerator keyGen = KeyGenerator.getInstance("DES");
        keyGen.init(56);
        SecretKey key = keyGen.generateKey();
        
        Cipher cipher = Cipher.getInstance("DES/ECB/PKCS5Padding");
        cipher.init(Cipher.ENCRYPT_MODE, key);
        byte[] encrypted = cipher.doFinal(data.getBytes());
        return Base64.getEncoder().encodeToString(encrypted);
    }
    
    // Weak Hash Function (CWE-328)
    public String hashPassword(String password) throws Exception {
        // Using weak MD5 hash
        MessageDigest md = MessageDigest.getInstance("MD5");
        byte[] hash = md.digest(password.getBytes());
        return Base64.getEncoder().encodeToString(hash);
    }
    
    // LDAP Injection (CWE-90)
    public String searchLDAP(String username) {
        String filter = "(uid=" + username + ")";
        // Vulnerable to LDAP injection
        return "cn=users,dc=example,dc=com?" + filter;
    }
    
    // XSS vulnerability (CWE-79)
    public void displayUserInput(HttpServletResponse response, String userInput) 
            throws IOException {
        PrintWriter out = response.getWriter();
        // Vulnerable to XSS - no output encoding
        out.println("<html><body>");
        out.println("<h1>Welcome " + userInput + "</h1>");
        out.println("</body></html>");
    }
    
    // CSRF vulnerability (CWE-352)
    public void transferMoney(HttpServletRequest request) throws SQLException {
        String amount = request.getParameter("amount");
        String toAccount = request.getParameter("to");
        // No CSRF token validation
        
        Connection conn = DriverManager.getConnection(
            "jdbc:mysql://localhost:3306/bank", "root", DB_PASSWORD
        );
        String query = "UPDATE accounts SET balance = balance - " + amount;
        Statement stmt = conn.createStatement();
        stmt.executeUpdate(query);
    }
    
    // Insecure Random Token Generation (CWE-338)
    public String generateSessionToken() {
        // Using insecure random for security-sensitive operation
        return String.valueOf(random.nextInt(999999));
    }
    
    // Information Exposure (CWE-209)
    public void handleError(Exception e, HttpServletResponse response) 
            throws IOException {
        PrintWriter out = response.getWriter();
        // Exposing stack trace to user
        out.println("Error occurred: " + e.getMessage());
        e.printStackTrace(out);
    }
    
    // Unrestricted File Upload (CWE-434)
    public void uploadFile(HttpServletRequest request) throws Exception {
        String filename = request.getParameter("filename");
        InputStream fileContent = request.getInputStream();
        
        // No file type validation
        FileOutputStream fos = new FileOutputStream("/var/www/uploads/" + filename);
        byte[] buffer = new byte[1024];
        int bytesRead;
        while ((bytesRead = fileContent.read(buffer)) != -1) {
            fos.write(buffer, 0, bytesRead);
        }
        fos.close();
    }
    
    // Server-Side Request Forgery (SSRF) (CWE-918)
    public String fetchURL(String url) throws IOException {
        // No URL validation - vulnerable to SSRF
        URL targetURL = new URL(url);
        HttpURLConnection conn = (HttpURLConnection) targetURL.openConnection();
        
        BufferedReader reader = new BufferedReader(
            new InputStreamReader(conn.getInputStream())
        );
        
        StringBuilder response = new StringBuilder();
        String line;
        while ((line = reader.readLine()) != null) {
            response.append(line);
        }
        return response.toString();
    }
    
    // Code Injection (CWE-94)
    public Object evaluateExpression(String expression) throws Exception {
        // Vulnerable to code injection
        ScriptEngineManager manager = new ScriptEngineManager();
        ScriptEngine engine = manager.getEngineByName("JavaScript");
        return engine.eval(expression);
    }
    
    // Race Condition (CWE-362)
    private int balance = 1000;
    
    public void withdraw(int amount) {
        // Race condition - not thread-safe
        if (balance >= amount) {
            try {
                Thread.sleep(100); // Simulate processing
            } catch (InterruptedException e) {}
            balance -= amount;
        }
    }
    
    // Null Pointer Dereference (CWE-476)
    public String getUserEmail(String username) {
        Map<String, String> users = new HashMap<>();
        users.put("admin", "admin@example.com");
        
        // Potential null pointer dereference
        String email = users.get(username);
        return email.toLowerCase(); // NPE if username not found
    }
    
    // Resource Leak (CWE-404)
    public String readFileWithLeak(String path) throws IOException {
        FileInputStream fis = new FileInputStream(path);
        // Resource not closed - memory leak
        byte[] data = new byte[1024];
        fis.read(data);
        return new String(data);
    }
    
    // Insecure Cookie (CWE-614)
    public void setSessionCookie(HttpServletResponse response, String sessionId) {
        Cookie cookie = new Cookie("SESSIONID", sessionId);
        // Not setting Secure and HttpOnly flags
        cookie.setMaxAge(3600);
        response.addCookie(cookie);
    }
    
    // Trust Boundary Violation (CWE-501)
    public void storeUserData(HttpSession session, String userData) {
        // Storing untrusted data in session without validation
        session.setAttribute("userData", userData);
    }
    
    // Integer Overflow (CWE-190)
    public int calculateTotal(int price, int quantity) {
        // Potential integer overflow
        return price * quantity;
    }
    
    // Use of Hard-coded Password (CWE-259)
    public boolean authenticateAdmin(String password) {
        return password.equals("admin123");
    }
    
    // Improper Certificate Validation (CWE-295)
    public void makeHTTPSRequest(String url) throws Exception {
        // Disable SSL certificate validation
        TrustManager[] trustAllCerts = new TrustManager[] {
            new X509TrustManager() {
                public java.security.cert.X509Certificate[] getAcceptedIssuers() {
                    return null;
                }
                public void checkClientTrusted(
                    java.security.cert.X509Certificate[] certs, String authType) {
                }
                public void checkServerTrusted(
                    java.security.cert.X509Certificate[] certs, String authType) {
                }
            }
        };
        
        SSLContext sc = SSLContext.getInstance("SSL");
        sc.init(null, trustAllCerts, new java.security.SecureRandom());
        HttpsURLConnection.setDefaultSSLSocketFactory(sc.getSocketFactory());
    }
    
    // Logging Sensitive Data (CWE-532)
    private static final Logger logger = Logger.getLogger(VulnerableApp.class.getName());
    
    public void logUserCredentials(String username, String password) {
        // Logging sensitive information
        logger.info("User login attempt: " + username + " with password: " + password);
    }
    
    // Missing Authentication (CWE-306)
    public void deleteUser(String userId) throws SQLException {
        // No authentication check
        Connection conn = DriverManager.getConnection(
            "jdbc:mysql://localhost:3306/mydb", "root", DB_PASSWORD
        );
        String query = "DELETE FROM users WHERE id=" + userId;
        Statement stmt = conn.createStatement();
        stmt.executeUpdate(query);
    }
    
    // Insufficient Session Expiration (CWE-613)
    public void createSession(HttpServletRequest request, String username) {
        HttpSession session = request.getSession(true);
        session.setAttribute("username", username);
        // Session never expires
        session.setMaxInactiveInterval(-1);
    }
}

class User {
    private String username;
    private String email;
    
    public User(String username, String email) {
        this.username = username;
        this.email = email;
    }
    
    public String getUsername() { return username; }
    public String getEmail() { return email; }
}