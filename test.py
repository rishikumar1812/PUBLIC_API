import requests
import json
import socket
import time
from flask_cors import CORS

print("Starting fraud detection API test...")

# Try to get local IP address
try:
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"Local IP detected as: {local_ip}")
except Exception as e:
    print(f"Could not detect local IP: {e}")
    local_ip = "127.0.0.1"

# Test data with a specific transaction_id we want to verify
test_data = {
    "transaction_id": "ANON_287602",
    "transaction_date": "2024-12-13 11:17:53",
    "transaction_amount": 199.0,
    "transaction_channel": "mobile",
    "transaction_payment_mode": 10,
    "payment_gateway_bank": 0,
    "payer_email": "01e539d52a86183530375b04b281abda87d90f30d35c981235bb3220cb21cf51",
    "payer_mobile": "XXXXX967.0",
    "payer_browser": 517,
    "payee_id": "ANON_119",
    "payee_ip": "b298ae3f549799b26d6f95df25f28388438fe22598f3bff59fbdb489ca9d0ecf"
}

print("Test data:", json.dumps(test_data, indent=2))
print()

# Create version with _anonymous suffix for Render
render_data = test_data.copy()
render_data["transaction_payment_mode_anonymous"] = render_data.pop("transaction_payment_mode")
render_data["payment_gateway_bank_anonymous"] = render_data.pop("payment_gateway_bank")
render_data["payer_browser_anonymous"] = render_data.pop("payer_browser")

# URLs to test with their corresponding data formats
urls = [
    {
        "url": "https://public-api-nh50.onrender.com/predict",
        "data": render_data,
        "name": "Render API"
    },
    {
        "url": "http://localhost:5000/predict",
        "data": test_data,
        "name": "Local Server"
    },
    {
        "url": f"http://{local_ip}:5000/predict",
        "data": test_data,
        "name": "Local IP Server"
    }
]

# Try each URL in sequence
any_success = False
for endpoint in urls:
    url = endpoint["url"]
    data = endpoint["data"]
    name = endpoint["name"]
    
    print(f"Trying to connect to: {url}")
    print(f"Testing {name} with transaction_id: {data['transaction_id']}")
    
    try:
        # First check if the server is running
        try:
            print("Checking if server is running with a GET request...")
            base_url = url.rsplit('/', 1)[0]
            check_response = requests.get(base_url, timeout=30)
            print(f"Server is reachable - Status: {check_response.status_code}")
        except Exception as e:
            print(f"Could not reach server base URL: {str(e)}")
            continue
        
        # Send the actual request
        print(f"Sending POST request to {url} with 60 second timeout...")
        response = requests.post(url, json=data, timeout=60)
        
        print(f"Response received - Status code: {response.status_code}")
        print(f"Response content: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("\nResponse Analysis:")
            print(f"Input transaction_id:  {data['transaction_id']}")
            print(f"Output transaction_id: {result.get('transaction_id', 'Not provided')}")
            ids_match = data['transaction_id'] == result.get('transaction_id', '')
            print(f"Transaction IDs match: {'✓' if ids_match else '✗'}")
            print(f"Is Fraud: {result.get('is_fraud', 'Not provided')}")
            if ids_match:
                any_success = True
                print("✓ Success! Found a server that returns the correct transaction_id.")
                break
        else:
            print(f"\nError response from server: {response.status_code}")
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error: Could not connect to {url}")
        print(f"Details: {str(e)}")
    except requests.exceptions.Timeout as e:
        print(f"Timeout error: Server at {url} took too long to respond")
        print(f"Details: {str(e)}")
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        print(f"Error type: {type(e).__name__}")
    
    print()

if not any_success:
    print("\n=== TROUBLESHOOTING TIPS ===")
    print("1. Make sure the Flask server is running. Start it with: python app.py")
    print("2. Check that the server is running on port 5000")
    print("3. Check server console output for any errors or exceptions")
    print("4. Try increasing the timeout if the server is slow to respond")
    print("5. Verify the API endpoint URL is correct")
    
    # Try to check if the service is running
    try:
        import psutil
        python_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            if 'python' in proc.info['name'].lower() and any(cmd and ('app.py' in cmd.lower()) for cmd in (proc.info['cmdline'] or [])):
                python_processes.append(proc.info)
        
        if python_processes:
            print("\nFound potential Flask server processes:")
            for proc in python_processes:
                print(f"PID: {proc['pid']}, Command: {' '.join(proc['cmdline'] or [])}")
        else:
            print("\nNo Flask server (app.py) process found running.")
    except ImportError:
        print("\nCould not check for running processes (psutil not installed)")
    except Exception as e:
        print(f"\nError checking for running processes: {str(e)}")