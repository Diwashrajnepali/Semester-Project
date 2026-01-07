import requests
import hashlib
import hmac
import base64
import uuid

# Configuration to test
url = "https://rc-epay.esewa.com.np/api/epay/main/v2/form"
secret_key = "8gBm/:&EnhH.1/q"
product_code = "EPAYTEST"

def generate_signature(secret_key, message):
    key = secret_key.encode('utf-8')
    msg = message.encode('utf-8')
    hash_obj = hmac.new(key, msg, hashlib.sha256)
    return base64.b64encode(hash_obj.digest()).decode('utf-8')

# Permutations to try
test_cases = [
    {"desc": "Standard Integers", "amt": "100", "tx_prefix": "TXA"},
]

results = []

results.append(f"Target URL: {url}")

for test in test_cases:
    # Unique ID
    uid = f"{test['tx_prefix']}-{uuid.uuid4().hex[:6]}"
    amt = test["amt"]
    
    # Signature
    msg = f"total_amount={amt},transaction_uuid={uid},product_code={product_code}"
    sig = generate_signature(secret_key, msg)
    
    payload = {
        "amount": amt,
        "tax_amount": "0",
        "total_amount": amt,
        "transaction_uuid": uid,
        "product_code": product_code,
        "product_service_charge": "0",
        "product_delivery_charge": "0",
        "success_url": "http://example.com/success",
        "failure_url": "http://example.com/failure",
        "signed_field_names": "total_amount,transaction_uuid,product_code",
        "signature": sig
    }
    
    try:
        response = requests.post(url, data=payload, allow_redirects=True, timeout=15)
        
        status = "UNKNOWN"
        content = response.text
        
        if "unable to fetch merchant key" in content.lower():
            status = "FAILED: Merchant Key Error"
        elif "login" in content.lower() or "pay with esewa" in content.lower():
            status = "SUCCESS: Login Page Reached"
        else:
            status = f"FAILED: Other ({response.status_code})"
            
        results.append(f"Test ({uid}) -> {status}")
        if status.startswith("FAILED"):
            results.append(f"  Response Snippet: {content[:200]}")
            
    except Exception as e:
        results.append(f"Exception: {str(e)}")

with open("final_verify_result.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(results))

print("Verification run complete.")
