from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import uuid
import json
import os
import pickle
from datetime import datetime
import traceback

app = Flask(__name__)

# Define the output directory for JSON files
OUTPUT_DIR = 'output'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load the model and scaler from pickle files
try:
    MODEL_PATH = 'model.pkl'
    SCALER_PATH = 'scaler.pkl'
    
    with open(MODEL_PATH, 'rb') as model_file:
        model = pickle.load(model_file)
    
    with open(SCALER_PATH, 'rb') as scaler_file:
        scaler = pickle.load(scaler_file)
    
    print(f"Model and scaler loaded successfully from {MODEL_PATH} and {SCALER_PATH}")
except Exception as e:
    print(f"Error loading model or scaler: {str(e)}")
    print("API will run, but predictions will not be accurate without the model files.")
    model = None
    scaler = None

@app.route('/')
def hello_world():
    return "Fraud Detection API is running. Send POST requests to /predict endpoint."

@app.route('/predict', methods=['POST'])
def predict_fraud():
    try:
        # Get JSON data from request
        data = request.get_json()
        print(f"Received data: {data}")
        
        # Check if all required parameters are present
        required_params = ["transaction_amount", "transaction_channel", 
                           "transaction_payment_mode_anonymous", 
                           "payment_gateway_bank_anonymous", 
                           "payer_browser_anonymous"]
        
        for param in required_params:
            if param not in data:
                return jsonify({'error': f'Missing required parameter: {param}'}), 400
        
        # Parse and validate transaction_amount
        try:
            amount = float(data['transaction_amount'])
        except ValueError:
            return jsonify({'error': f"Invalid transaction_amount: {data['transaction_amount']}. Must be a number."}), 400
        
        # Handle transaction_channel - explicitly process and convert to integer
        channel_input = str(data['transaction_channel']).lower()
        print(f"Processing channel input: '{channel_input}'")
        
        # Web options (code 1): 1, web, w, W, WEB, npm, #
        web_options = ['1', 'web', 'w', 'npm', '#']
        # Mobile options (code 2): 2, mobile, m, M, 5666
        mobile_options = ['2', 'mobile', 'm', '5666']
        
        if any(opt == channel_input for opt in web_options):
            channel_code = 1
            print(f"Channel '{channel_input}' matched web option, code = 1")
        elif any(opt == channel_input for opt in mobile_options):
            channel_code = 2
            print(f"Channel '{channel_input}' matched mobile option, code = 2")
        else:
            # Default to 1 if unrecognized
            channel_code = 1
            print(f"Channel '{channel_input}' not recognized, using default code = 1")
        
        # Parse and validate remaining parameters
        try:
            payment_mode = float(data['transaction_payment_mode_anonymous'])
            gateway_bank = float(data['payment_gateway_bank_anonymous'])
            browser = float(data['payer_browser_anonymous'])
        except ValueError as e:
            return jsonify({'error': f"Invalid numeric parameter: {str(e)}"}), 400
        
        # Generate a unique transaction ID
        transaction_id = str(uuid.uuid4())
        
        # Create feature array with explicit numeric values only
        features = np.array([
            amount,
            int(channel_code),
            payment_mode,
            gateway_bank,
            browser
        ]).reshape(1, -1)
        
        print(f"Feature array shape: {features.shape}, values: {features}")
        
        # Make prediction
        if model is not None and scaler is not None:
            try:
                # Scale the features
                scaled_features = scaler.transform(features)
                # Make prediction
                prediction = model.predict(scaled_features)
                is_fraud = bool(prediction[0])
                print(f"Model prediction: {is_fraud}")
            except Exception as e:
                print(f"Error during prediction: {str(e)}")
                traceback.print_exc()
                # Fallback
                is_fraud = amount > 1000
                print(f"Using fallback prediction: {is_fraud}")
        else:
            # Fallback logic if model is not available
            is_fraud = amount > 1000
            print(f"Model not available, using fallback prediction: {is_fraud}")
        
        # Create result dictionary
        result = {
            'transaction_id': transaction_id,
            'is_fraud': is_fraud
        }
        
        # Save the result to a JSON file
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{OUTPUT_DIR}/transaction_{transaction_id}_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(result, f)
        
        print(f"Result saved to {filename}")
        
        # Return the result as JSON response
        return jsonify(result)
    
    except ValueError as e:
        print(f"ValueError: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': f'Error processing input data: {str(e)}'}), 400
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

if __name__ == '__main__':
    # Run the application on all available network interfaces (0.0.0.0)
    # This makes it accessible from outside the local machine
    app.run(host='0.0.0.0', port=5000, debug=True)


