import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib

np.random.seed(42)
features = [
    "rainfall", "soil_moisture", "slope",
    "elevation", "vegetation_loss", "terrain_instability"
]

def make_class_samples(n, low, high):
    rows = []
    while len(rows) < n:
        x = np.random.uniform(0, 100, size=(max(2000, n * 3), 6))
        score = (
            x[:, 0] * 0.30 + x[:, 1] * 0.20 + x[:, 2] * 0.20 +
            x[:, 3] * 0.10 + x[:, 4] * 0.10 + x[:, 5] * 0.10
        )
        mask = (score >= low) & (score < high)
        rows.extend(x[mask].tolist())
    return np.asarray(rows[:n])

parts = []
for label, low, high in [
    ("LOW", 0, 40),
    ("MODERATE", 40, 60),
    ("HIGH", 60, 80),
    ("CRITICAL", 80, 101),
]:
    x = make_class_samples(2000, low, high)
    df = pd.DataFrame(x, columns=features)
    df["risk_level"] = label
    parts.append(df)

data = pd.concat(parts, ignore_index=True).sample(
    frac=1, random_state=42
).reset_index(drop=True)

X = data[features]
y = data["risk_level"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

model = RandomForestClassifier(
    n_estimators=300,
    random_state=42,
    max_depth=14,
    min_samples_leaf=2,
    n_jobs=-1
)
model.fit(X_train, y_train)

predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)

print("DRISHTI BALANCED LANDSLIDE ML MODEL")
print(f"Accuracy: {accuracy:.2%}")
print("\nClassification Report:")
print(classification_report(y_test, predictions))

joblib.dump(model, "backend/ml/landslide_model.pkl")
print("\nModel saved: backend/ml/landslide_model.pkl")
