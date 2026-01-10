import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score

print("Loading data...")
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

df_train = pd.read_csv('KDDTrain+.txt', names=columns)
df_test = pd.read_csv('KDDTest+.txt', names=columns)

print(f"Training set size: {df_train.shape}")
print(f"Test set size: {df_test.shape}")


print("\nPreprocessing data...")

# Function to handle categorical data (protocol, service, flag)
# Function to handle categorical data (protocol, service, flag)
def preprocess(df, encoders=None):
    # Create a copy to avoid SettingWithCopy warnings or modifying original data
    df = df.copy()
    
    df['target'] = df['label'].apply(lambda x: 0 if x == 'normal' else 1)
    df = df.drop(['label', 'difficulty'], axis=1)
    
    cat_cols = ['protocol_type', 'service', 'flag']
    
    if encoders is None:
        # TRAINING MODE: Fit encoders and return them
        encoders = {}
        for col in cat_cols:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col])
            encoders[col] = le
        return df, encoders
    else:
        # TESTING MODE: Use existing encoders
        for col in cat_cols:
            le = encoders[col]
            # Handle unseen labels (crucial for real-world/test data)
            # Map unseen labels to the first known class to prevent crashing
            known_classes = set(le.classes_)
            df[col] = df[col].apply(lambda x: x if x in known_classes else list(known_classes)[0])
            df[col] = le.transform(df[col])
        return df

# Fit on Training Data
train_data, encoders = preprocess(df_train)

# Transform Test Data using Training Encoders
test_data = preprocess(df_test, encoders=encoders)

# Separate Features (X) and Target (y)
X_train = train_data.drop('target', axis=1)
y_train = train_data['target']
X_test = test_data.drop('target', axis=1)
y_test = test_data['target']

print("\nTraining Random Forest Model")
rf = RandomForestClassifier(n_estimators=50, random_state=42)
rf.fit(X_train, y_train)
print("Training Complete!")

print("\nRunning Evaluation on Test Set")
y_pred = rf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
 
print(f"\nModel Accuracy: {accuracy * 100:.2f}%")
print("\n--- detailed Classification Report ---")
print(classification_report(y_test, y_pred))

importances = rf.feature_importances_
feature_names = X_train.columns
indices = np.argsort(importances)[::-1]

print("\nTOP 5 INDICATORS OF ATTACK:")
for i in range(5):
    print(f"{i+1}. {feature_names[indices[i]]} ({importances[indices[i]]:.4f})")