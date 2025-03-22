import requests
import json

# API endpoint - use localhost for direct testing
url = "http://127.0.0.1:5000/predict"

print(f"Sending request to: {url}")

# Test data with 'npm' as transaction_channel (which was causing the error)
test_data = {
    "transaction_amount": 1200,
    "transaction_channel": "npm",
    "transaction_payment_mode_anonymous": 2,
    "payment_gateway_bank_anonymous": 3,
    "payer_browser_anonymous": 4
}

print("Testing with data:")
print(json.dumps(test_data, indent=2))

try:
    # Send POST request to the API
    response = requests.post(url, json=test_data)
    
    # Print response information
    print(f"\nResponse status code: {response.status_code}")
    print(f"Response content: {response.text}")
    
    # If successful, parse and show the JSON response
    if response.status_code == 200:
        result = response.json()
        print("\nSuccessful prediction:")
        print(f"Transaction ID: {result['transaction_id']}")
        print(f"Is Fraud: {result['is_fraud']}")
    else:
        print("\nError in response from server.")
        
except Exception as e:
    print(f"\nError occurred: {str(e)}")
    print("\nTroubleshooting tips:")
    print("1. Ensure the Flask server is running (python app.py)")
    print("2. Check server logs for detailed error information") 