import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "manipulation.db")
MODEL_PATH = os.path.join(os.path.dirname(__file__), "rf_classifier.pkl")

def train_model():
    print("Extracting feature snapshots linked to evaluated rule labels...")
    conn = sqlite3.connect(DB_PATH)
    # Join features with their evaluated deterministic labels to bootstrap the model
    query = """
    SELECT 
        f.interaction_count, f.success_rate, f.mean_size, f.size_std, 
        f.unique_destinations, f.destination_concentration, 
        f.frequency_spike_score, f.size_spike_score, 
        s.risk_label
    FROM source_feature_snapshots f
    JOIN source_risk_scores s 
      ON f.source_id = s.source_id 
      AND f.window_name = s.window_name
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    if len(df) < 10:
        print("Not enough data to train. Please run the simulator and deterministic scoring first.")
        return

    # Impute missing values with 0
    df = df.fillna(0)

    X = df.drop(columns=['risk_label'])
    y = df['risk_label']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print(f"Training RandomForestClassifier on {len(X_train)} samples...")
    clf = RandomForestClassifier(n_estimators=50, max_depth=5, random_state=42)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    print("\n[Evaluation Summary]")
    print(classification_report(y_test, y_pred))

    joblib.dump(clf, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")

if __name__ == "__main__":
    train_model()
