# Fraud Detection API

This API provides fraud detection capabilities for financial transactions.

## API Endpoints

### GET /
Health check endpoint that returns API status.

### POST /predict
Predicts whether a transaction is fraudulent.

#### Request Format
```json
{
    "transaction_id": "ANON_287602",
    "transaction_date": "2024-12-13 11:17:53",
    "transaction_amount": 199.0,
    "transaction_channel": "mobile",
    "transaction_payment_mode": 10,
    "payment_gateway_bank": 0,
    "payer_email": "example@email.com",
    "payer_mobile": "XXXXX967.0",
    "payer_browser": 517,
    "payee_id": "ANON_119",
    "payee_ip": "xxx.xxx.xxx.xxx"
}
```

#### Response Format
```json
{
    "transaction_id": "ANON_287602",
    "is_fraud": true
}
```

## Deployment

### Local Development
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the server:
   ```bash
   python app.py
   ```

### Render Deployment
1. Push code to GitHub
2. Create new Web Service on Render
3. Connect to GitHub repository
4. Use the following settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

## Required Files
- model.pkl: Trained machine learning model
- scaler.pkl: Feature scaler

## Environment Variables
None required

## Testing
Run the test script:
```bash
python test.py 