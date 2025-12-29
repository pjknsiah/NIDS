# AI-Driven Network Intrusion Detection System (NIDS)

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Library](https://img.shields.io/badge/Scikit--Learn-Random%20Forest-orange)
![Status](https://img.shields.io/badge/Status-Prototype-green)

A machine learning-based intrusion detection pipeline designed to classify network traffic anomalies. This project leverages the **NSL-KDD** dataset to train a **Random Forest** classifier capable of distinguishing between normal traffic and malicious attack vectors (DoS, Probe, U2R, R2L) with **78.26% accuracy** on unseen test data.

## Project Overview

Traditional firewall systems often rely on static rules signatures, making them vulnerable to zero-day attacks and novel intrusion patterns. This project explores a **statistical learning approach** to security, using supervised machine learning to identify malicious packet flows based on traffic characteristics rather than explicit signatures.

**Key Objectives:**
* **Data Ingestion:** Process raw network traffic records from the NSL-KDD dataset.
* **Feature Engineering:** Transform categorical packet headers (Protocol, Service, Flags) into numerical vectors.
* **Classification:** Train a Random Forest model to predict traffic labels (`normal` vs. `anomaly`).
* **Analysis:** Evaluate model performance on a distinct test set to simulate real-world generalization.

## 📊 Key Results

* **Model Architecture:** Random Forest Classifier (n_estimators=100)
* **Training Set:** KDDTrain+ (125,973 records)
* **Test Set:** KDDTest+ (22,544 records - contains attack types not present in training)
* **Accuracy:** **78.26%**
* **Why this matters:** The gap between training accuracy (>99%) and test accuracy (~78%) highlights the challenge of **Zero-Day Attack Detection**. The model successfully generalized to most attack categories but identified specific novel attack signatures that require further retraining, mimicking real-world security constraints.

### Top Predictive Features
Analysis of Gini Importance identified the following as the strongest indicators of malicious activity:
1.  **src_bytes:** Volume of data sent from source (high volume often indicates exfiltration or DoS).
2.  **dst_bytes:** Volume of data received at destination.
3.  **flag:** Connection status (e.g., `SF`, `S0` - indicating incomplete handshakes).

## Installation & Setup

### Prerequisites
* Python 3.8+
* pip

### 1. Clone the Repository
```bash
git clone [https://github.com/YOUR_USERNAME/nids-project.git](https://github.com/YOUR_USERNAME/nids-project.git)
cd nids-project

### 2. Install Dependencies
```bash
pip install pandas numpy scikit-learn matplotlib seaborn
```

### 3. Download the Dataset
```bash
Download KDDTrain+.txt and KDDTest+.txt from the NSL-KDD Dataset and place them in the root directory.
```

## Usage
```bash
python nids.py
```
