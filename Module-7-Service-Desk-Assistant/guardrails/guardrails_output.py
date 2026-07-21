import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.aiopenscale.cloud.ibm.com"
POLICY_ID = os.environ["WATSON_OPENSCALE_POLICY_ID"]
INVENTORY_ID = os.environ["WATSON_OPENSCALE_INVENTORY_ID"]
GOVERNANCE_INSTANCE_ID = os.environ["WATSON_OPENSCALE_GOVERNANCE_INSTANCE_ID"]


def get_ibm_bearer_token() -> str:
    """Fetch an IBM Cloud IAM bearer token using WATSONX_APIKEY from environment."""
    api_key = os.environ["WATSONX_APIKEY"]
    response = requests.post(
        "https://iam.cloud.ibm.com/identity/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": api_key,
        },
    )
    response.raise_for_status()
    return response.json()["access_token"]


def enforce_policy(text: str) -> dict | None:
    """Run guardrail PII enforcement on the given text."""
    url = BASE_URL + f"/guardrails-manager/v1/enforce/{POLICY_ID}"
    payload = {
        "text": text,
        "direction": "output",
        "detectors_properties": {"pii": {}},
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "x-governance-instance-id": GOVERNANCE_INSTANCE_ID,
        "Authorization": f"Bearer {get_ibm_bearer_token()}",
    }

    try:
        response = requests.post(url, params={"inventory_id": INVENTORY_ID}, headers=headers, json=payload)
        if response.status_code == 200:
            result = response.json()
            print("Policy enforcement successful:")
            print(json.dumps(result, indent=2))
            return result
        else:
            print(f"Error: {response.status_code} — {response.text}")
            return None
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return None


if __name__ == "__main__":
    sample_text = (
        "Customer John Smith (SSN: 123-45-6789) called from +1-415-555-0192. "
        "His credit card number is 4111 1111 1111 1111 and email is john.smith@company.com."
    )
    enforce_policy(sample_text)
