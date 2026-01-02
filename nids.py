import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score

# --- STEP 1: LOAD DATA ---
print("Loading data...")
# NSL-KDD column names (the file doesn't have headers)
columns = ["duration","protocol_type","service","flag","src_bytes","dst_bytes",
           "land","wrong_fragment","urgent","hot","num_failed_logins",
           "logged_in","num_compromised","root_shell","su_attempted",
           "num_root","num_file_creations","num_shells","num_access_files",
           "num_outbound_cmds","is_host_login","is_guest_login","count",
           "srv_count","serror_rate","srv_serror_rate","rerror_rate",
           "srv_rerror_rate","same_srv_rate","diff_srv_rate","srv_diff_host_rate",
           "dst_host_count","dst_host_srv_count","dst_host_same_srv_rate",
           "dst_host_diff_srv_rate","dst_host_same_src_port_rate",
           "dst_host_srv_diff_host_rate","dst_host_serror_rate",
           "dst_host_srv_serror_rate","dst_host_rerror_rate",
           "dst_host_srv_rerror_rate","label", "difficulty"]

# Load Training and Test data
df_train = pd.read_csv('KDDTrain+.txt', names=columns)
df_test = pd.read_csv('KDDTest+.txt', names=columns)

print(f"Training set size: {df_train.shape}")
print(f"Test set size: {df_test.shape}")

# --- STEP 2: PREPROCESSING ---
print("\nPreprocessing data...")

# Function to handle categorical data (protocol, service, flag)
def preprocess(df):
    # Create target: 0 for normal, 1 for attack
    df['target'] = df['label'].apply(lambda x: 0 if x == 'normal' else 1)
    
    # Drop columns we don't need
    df = df.drop(['label', 'difficulty'], axis=1)
    
    # Encode text columns to numbers
    for col in ['protocol_type', 'service', 'flag']:
        le = LabelEncoder()
        # Fit on the column and transform
        df[col] = le.fit_transform(df[col])
    return df

train_data = preprocess(df_train)
test_data = preprocess(df_test)

# Separate Features (X) and Target (y)
X_train = train_data.drop('target', axis=1)
y_train = train_data['target']
X_test = test_data.drop('target', axis=1)
y_test = test_data['target']

# --- STEP 3: TRAINING THE MODEL ---
print("\nTraining Random Forest Model (this might take a minute)...")
# n_estimators=50 is enough for a demo; increase to 100 for better results
rf = RandomForestClassifier(n_estimators=50, random_state=42)
rf.fit(X_train, y_train)
print("Training Complete!")

# --- STEP 4: EVALUATION ---
print("\nRunning Evaluation on Test Set...")
y_pred = rf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"\nModel Accuracy: {accuracy * 100:.2f}%")
print("\n--- detailed Classification Report ---")
print(classification_report(y_test, y_pred))

# --- STEP 5: RESEARCH INSIGHTS (Feature Importance) ---
# This is the "Why" that researchers care about
importances = rf.feature_importances_
feature_names = X_train.columns
indices = np.argsort(importances)[::-1]

print("\nTOP 5 INDICATORS OF ATTACK:")
for i in range(5):
    print(f"{i+1}. {feature_names[indices[i]]} ({importances[indices[i]]:.4f})")