import pandas as pd
import numpy as np
from flask import Flask, render_template, jsonify
import nids
import random

app = Flask(__name__)

# --- NIDS Integration ---
# Using the trained model and test data from nids.py
# nids.py runs training on import, so we have access to:
# nids.rf (the model)
# nids.X_test (test features)
# nids.y_test (true labels)
# nids.test_data (features + target + other cols from preprocessing if available, 
#                 but nids.py overwrites test_data with preprocess() result which has dropped cols)

# Let's inspect what we have in nids.X_test
# It's a DataFrame with the processed features.

# We'll simulate "live" traffic by sampling from the test set.
# We'll keep a history of "recent" alerts.
recent_alerts = []
TOTAL_PACKETS_SIMULATED = 0
THREAT_COUNT = 0
SIMULATION_RUNNING = True

def simulate_traffic():
    """
    Simulates traffic by picking a random row from X_test,
    predicting it, and updating stats.
    Returns the prediction and details.
    """
    global TOTAL_PACKETS_SIMULATED, THREAT_COUNT, recent_alerts
    
    # Pick a random index
    idx = random.randint(0, len(nids.X_test) - 1)
    
    # Extract the row
    row = nids.X_test.iloc[[idx]]
    
    # Predict
    prediction = nids.rf.predict(row)[0] # 0 or 1
    # prediction proba for "confidence" or "severity" approximation
    proba = nids.rf.predict_proba(row)[0][1] # probability of class 1 (attack)
    
    TOTAL_PACKETS_SIMULATED += 1
    
    is_attack = (prediction == 1)
    if is_attack:
        THREAT_COUNT += 1
        
        # Construct alert object
        # We don't have the original raw features easily mapped back because of LabelEncoding 
        # in nids.py without the encoders being saved. 
        # But we can show the processed values or just generic info.
        # For a PRETTY dashboard, we might want to say "TCP / HTTP" etc.
        # But we only have encoded values in X_test.
        # To make it look better, we'll just mock the protocol/service names 
        # based on randomness or generic labels for this demo, 
        # OR we could try to look at the original df_test if we read it again.
        
        # Let's just use generic "Packet #{ID}" and the probability score.
        alert = {
            "id": TOTAL_PACKETS_SIMULATED,
            "severity": "High" if proba > 0.8 else "Medium",
            "score": float(f"{proba:.2f}"),
            "type": "Malicious Activity", # We don't have multi-class labels in nids.py, just 0/1
            "timestamp": pd.Timestamp.now().strftime("%H:%M:%S")
        }
        recent_alerts.insert(0, alert)
        recent_alerts = recent_alerts[:50] # Keep last 50
        
    return is_attack

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats')
def get_stats():
    # Simulate some traffic on every poll to make it alive
    # Simulate a burst of packets
    if SIMULATION_RUNNING:
        for _ in range(random.randint(1, 5)):
            simulate_traffic()
        
    stats = {
        "total_packets": TOTAL_PACKETS_SIMULATED,
        "threats_detected": THREAT_COUNT,
        "threat_level": "Critical" if THREAT_COUNT > 100 else ("Elevated" if THREAT_COUNT > 20 else "Normal"),
        "threat_level_normalized": "Normal" if THREAT_COUNT / (TOTAL_PACKETS_SIMULATED or 1) < 0.1 else "High",
        "simulation_running": SIMULATION_RUNNING
    }
    return jsonify(stats)

@app.route('/api/alerts')
def get_alerts():
    return jsonify(recent_alerts)

@app.route('/api/control/start', methods=['POST'])
def start_simulation():
    global SIMULATION_RUNNING
    SIMULATION_RUNNING = True
    return jsonify({"status": "started", "running": True})

@app.route('/api/control/stop', methods=['POST'])
def stop_simulation():
    global SIMULATION_RUNNING
    SIMULATION_RUNNING = False
    return jsonify({"status": "stopped", "running": False})

if __name__ == '__main__':
    # Initialize some history
    print("Initializing Simulation...")
    for _ in range(20):
        simulate_traffic()
        
    app.run(debug=True, port=5000)
