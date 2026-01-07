import pandas as pd
import numpy as np
from flask import Flask, render_template, jsonify
import nids
import random

app = Flask(__name__)

# Using the trained model and test data from nids.py which runs training on import
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
    
    idx = random.randint(0, len(nids.X_test) - 1)
    row = nids.X_test.iloc[[idx]]
    
    # Predict
    prediction = nids.rf.predict(row)[0] # 0 or 1
    # prediction proba for "confidence" or "severity" approximation
    proba = nids.rf.predict_proba(row)[0][1] # probability of class 1 (attack)
    
    TOTAL_PACKETS_SIMULATED += 1
    
    is_attack = (prediction == 1)
    if is_attack:
        THREAT_COUNT += 1
        alert = {
            "id": TOTAL_PACKETS_SIMULATED,
            "severity": "High" if proba > 0.8 else "Medium",
            "score": float(f"{proba:.2f}"),
            "type": "Malicious Activity", # We don't have multi-class labels in nids.py, just 0/1
            "timestamp": pd.Timestamp.now().strftime("%H:%M:%S")
        }
        recent_alerts.insert(0, alert)
        recent_alerts = recent_alerts[:50]
        
    return is_attack

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats')
def get_stats():
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
    print("Initializing Simulation...")
    for _ in range(20):
        simulate_traffic()
        
    app.run(debug=True, port=5000)
