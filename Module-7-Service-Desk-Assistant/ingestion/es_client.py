# ingestion/es_client.py

import os
import warnings
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

# Suppress InsecureRequestWarning for IBM Cloud Databases
# IBM Cloud certs have non-critical Basic Constraints which Python SSL rejects
from urllib3.exceptions import InsecureRequestWarning
warnings.filterwarnings('ignore', category=InsecureRequestWarning)

load_dotenv()

def get_es_client() -> Elasticsearch:
    """
    Create an Elasticsearch client authenticated with
    username/password and a CA certificate.
    Supports both ES_CERT_PATH (file path) and ES_CERT_CONTENT (certificate string).
    """
    import tempfile
    
    host = os.getenv("ES_HOST", "")
    port = int(os.getenv("ES_PORT", 9200))
    username = os.getenv("ES_USERNAME")
    password = os.getenv("ES_PASSWORD")
    cert_content = os.getenv("ES_CERT_CONTENT")  # Certificate content as string
    cert_path = os.getenv("ES_CERT_PATH")        # Path to CA .crt file
    use_ssl = os.getenv("ES_USE_SSL", "true").lower() == "true"

    # Clean up host - remove https:// or http:// if present
    host = host.replace("https://", "").replace("http://", "").strip()
    
    if not all([host, username, password]):
        raise EnvironmentError(
            "Missing required Elasticsearch env vars: "
            "ES_HOST, ES_USERNAME, ES_PASSWORD"
        )

    # Option to disable cert verification for development (not recommended for production)
    verify_certs = os.getenv("ES_VERIFY_CERTS", "true").lower() == "true"
    
    print(f"[ES] Connecting to {host}:{port} (SSL: {use_ssl}, Verify Certs: {verify_certs})")
    
    # Build Elasticsearch client parameters
    es_params = {
        "hosts": [{"host": host, "port": port, "scheme": "https" if use_ssl else "http"}],
        "basic_auth": (username, password),
        "verify_certs": verify_certs,
        "ssl_show_warn": not verify_certs,
        "request_timeout": 30,
        "retry_on_timeout": True,
        "max_retries": 3,
    }
    
    # Handle certificate - prefer content over path
    temp_cert_file = None
    if verify_certs:
        if cert_content:
            # Write certificate content to temporary file
            temp_cert_file = tempfile.NamedTemporaryFile(mode='w', suffix='.crt', delete=False)
            temp_cert_file.write(cert_content)
            temp_cert_file.flush()
            es_params["ca_certs"] = temp_cert_file.name
            temp_cert_file.close()
            print(f"[ES] Using certificate from ES_CERT_CONTENT")
        elif cert_path:
            # Use certificate file path
            es_params["ca_certs"] = cert_path
            print(f"[ES] Using certificate from ES_CERT_PATH: {cert_path}")
        else:
            print(f"[ES] Warning: ES_VERIFY_CERTS=true but no certificate provided")
    
    client = Elasticsearch(**es_params)

    # Verify connection
    info = client.info()
    print(f"[ES] Connected to cluster: {info['cluster_name']} "
          f"(version {info['version']['number']})")
    return client


def get_es_client_with_cert_bytes() -> Elasticsearch:
    """
    Alternative: pass the certificate as bytes (useful when cert
    is stored in a secrets manager rather than on disk).
    """
    import base64
    cert_b64 = os.getenv("ES_CERT_BASE64")   # base64-encoded cert
    cert_bytes = base64.b64decode(cert_b64)

    return Elasticsearch(
        hosts=[{
            "host": os.getenv("ES_HOST"),
            "port": int(os.getenv("ES_PORT", 9200)),
            "scheme": "https"
        }],
        basic_auth=(os.getenv("ES_USERNAME"), os.getenv("ES_PASSWORD")),
        ssl_context=_build_ssl_context(cert_bytes),
        verify_certs=True,
    )


def _build_ssl_context(cert_bytes: bytes):
    import ssl, tempfile
    ctx = ssl.create_default_context()
    with tempfile.NamedTemporaryFile(suffix=".crt", delete=False) as f:
        f.write(cert_bytes)
        ctx.load_verify_locations(f.name)
    return ctx

# Made with Bob
