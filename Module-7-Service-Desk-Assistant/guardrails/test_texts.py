# guardrails/test_texts.py
# Test texts for guardrails PII detection validation.
# Run: python test_texts.py

from guardrails_output import enforce_policy

PII_TEXTS = [
    # 1. SSN + name
    "Customer John Smith (SSN: 123-45-6789) reported an issue with his account.",
    # 2. Credit card
    "Payment failed for card number 4111 1111 1111 1111, expiry 12/26, CVV 123.",
    # 3. Phone + email
    "Please call Sarah at +1-415-555-0192 or email her at sarah.jones@gmail.com.",
    # 4. Passport number
    "Traveller ID verified: Passport A12345678, issued to Michael Brown.",
    # 5. Date of birth
    "User profile: Emily Davis, DOB 14/03/1985, address 42 Maple Street, Austin TX.",
    # 6. Bank account
    "Transfer $2,500 from account 000123456789 (routing 021000021) to vendor.",
    # 7. Medicare/health ID
    "Patient record for Robert Lee, Medicare ID 1EG4-TE5-MK72, admitted 2024-01-10.",
    # 8. IP address + username
    "Login attempt by user jdoe (IP: 192.168.1.105) failed 3 times.",
    # 9. Full address
    "Ship order to Lisa Wong, 88 Ocean Drive, San Francisco, CA 94102.",
    # 10. Mixed PII in a support ticket
    "INC0012345 — James Carter (james.carter@corp.com, +44 7911 123456) "
    "reported unauthorized access to his account (ID: USR-98271).",
]

NO_PII_TEXTS = [
    # 1. Generic system error
    "The application crashed with error code 500 during the nightly batch job.",
    # 2. Network issue
    "VPN connection dropped intermittently for users on the London office network.",
    # 3. Software request
    "Requesting installation of Adobe Acrobat Pro on the finance department laptops.",
    # 4. Password policy question
    "How often should users be required to rotate their passwords per our policy?",
    # 5. Hardware fault
    "Three monitors in meeting room B are showing flickering display issues.",
    # 6. Scheduled maintenance
    "Planned maintenance window: Saturday 02:00–04:00 UTC for database patching.",
    # 7. Policy question
    "What is the approved process for escalating a P1 incident outside business hours?",
    # 8. Software bug report
    "The export to CSV feature in the reporting dashboard returns an empty file.",
    # 9. Access request (no personal details)
    "Team requires read access to the shared drive folder for project documentation.",
    # 10. Incident resolution note
    "Issue resolved by restarting the authentication service on the production cluster.",
]


if __name__ == "__main__":
    print("=" * 60)
    print("TESTING TEXTS WITH PII (expect detections)")
    print("=" * 60)
    for i, text in enumerate(PII_TEXTS, 1):
        print(f"\n[{i}] {text[:80]}...")
        enforce_policy(text)

    print("\n" + "=" * 60)
    print("TESTING TEXTS WITHOUT PII (expect no detections)")
    print("=" * 60)
    for i, text in enumerate(NO_PII_TEXTS, 1):
        print(f"\n[{i}] {text[:80]}...")
        enforce_policy(text)
