import requests
import json
import socket
import time

print("Starting fraud detection API test...")

# Try to get local IP address
try:
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"Local IP detected as: {local_ip}")
except Exception as e:
    print(f"Could not detect local IP: {e}")
    local_ip = "127.0.0.1"

# List of URLs to try
urls = ["https://public-api-nh50.onrender.com/predict",
        f"http://localhost:5000/predict",
        f"http://{local_ip}:5000/predict"]

# Test data with required parameters
data = {
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

print(f"Test data: {json.dumps(data, indent=2)}")

# Try each URL in sequence
success = False
for url in urls:
    print(f"\nTrying to connect to: {url}")
    try:
        # First check if the server is reachable
        try:
            print("Checking if server is running with a GET request...")
            base_url = url.rsplit('/', 1)[0]  # Get the base URL without the endpoint
            check_response = requests.get(base_url, timeout=30)  # Increased timeout
            print(f"Server is reachable - Status: {check_response.status_code}")
        except Exception as e:
            print(f"Could not reach server base URL: {str(e)}")
        
        # Increased timeout to 60 seconds to account for model loading and cold starts
        print(f"Sending POST request to {url} with 60 second timeout...")
        response = requests.post(url, json=data, timeout=60)
        
        print(f"Response received - Status code: {response.status_code}")
        print(f"Response content: {response.text}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("\nSuccessful prediction:")
                print(f"Transaction ID: {result.get('transaction_id', 'Not provided')}")
                print(f"Is Fraud: {result.get('is_fraud', 'Not provided')}")
                if 'transaction_id' in result and 'is_fraud' in result:
                    success = True
                    break
                else:
                    print("Response was status 200 but didn't contain expected fields.")
            except json.JSONDecodeError:
                print("Response was not valid JSON")
        else:
            print(f"Error response from server: {response.status_code}")
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error: Could not connect to {url}")
        print(f"Details: {str(e)}")
    except requests.exceptions.Timeout as e:
        print(f"Timeout error: Server at {url} took too long to respond")
        print(f"Details: {str(e)}")
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        print(f"Error type: {type(e).__name__}")

if not success:
    print("\n=== TROUBLESHOOTING TIPS ===")
    print("1. Make sure the Flask server is running. Start it with: python app_fixed.py")
    print("2. Check that the server is running on port 5000")
    print("3. Check server console output for any errors or exceptions")
    print("4. Try increasing the timeout if the server is slow to respond")
    print("5. Verify the API endpoint URL is correct")
    
    # Try to check if the service is running
    try:
        import psutil
        python_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            if 'python' in proc.info['name'].lower() and any(cmd and ('app.py' in cmd.lower() or 'app_fixed.py' in cmd.lower()) for cmd in proc.info['cmdline']):
                python_processes.append(proc.info)
        
        if python_processes:
            print("\nFound potential Flask server processes:")
            for proc in python_processes:
                print(f"PID: {proc['pid']}, Command: {' '.join(proc['cmdline'])}")
        else:
            print("\nNo Flask server (app.py or app_fixed.py) process found running.")
    except ImportError:
        print("\nCould not check for running processes (psutil not installed)")
    except Exception as e:
        print(f"\nError checking for running processes: {str(e)}")
