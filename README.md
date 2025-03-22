# Fraud Detection API

A Flask API that detects potentially fraudulent transactions based on input parameters and a pre-trained machine learning model.

## Setup

1. Install the required dependencies:
```
pip install -r requirements.txt
```

2. Ensure you have the model files in your project directory:
   - `model.pkl` - The trained machine learning model
   - `scaler.pkl` - The feature scaler used to normalize inputs

3. Run the application:
```
python app.py
```

The API will be available at http://your-ip-address:5000/

## API Usage

### Endpoint: `/predict`

**Method:** POST

**Input Parameters:**
- `transaction_amount`: Amount of the transaction (numeric)
- `transaction_channel`: Channel of transaction (1 for web, 2 for mobile)
  - Web options: 1, web, w, W, WEB, npm, #
  - Mobile options: 2, mobile, m, M, 5666
- `transaction_payment_mode_anonymous`: Anonymous payment mode identifier (numeric)
- `payment_gateway_bank_anonymous`: Anonymous payment gateway/bank identifier (numeric)
- `payer_browser_anonymous`: Anonymous browser identifier (numeric)

**Example Request:**
```json
{
  "transaction_amount": 1500,
  "transaction_channel": "web",
  "transaction_payment_mode_anonymous": 3,
  "payment_gateway_bank_anonymous": 2,
  "payer_browser_anonymous": 1
}
```

**Example Response:**
```json
{
  "transaction_id": "7f4c6a9b-1e2d-4b3c-8d5e-6f7a8b9c0d1e",
  "is_fraud": true
}
```

## External Access

This API is configured to be accessible over the public internet. The server listens on all available network interfaces (0.0.0.0), allowing connections from outside the local machine.

To access the API from another device, use the public IP address of your server:
```
http://your-ip-address:5000/predict
```

## Note

The API requires two pickle files to function correctly:
- `model.pkl` - The trained model
- `scaler.pkl` - The feature scaler

If these files are missing, the API will still run but will use a fallback logic (flagging transactions over $1000 as potentially fraudulent).

## Output

JSON output files are stored in the `output` directory with the naming pattern: `transaction_{transaction_id}_{timestamp}.json` 