
from app.intelligence.isolation_forest import (
    FEATURE_NAMES,
    train_model,
    detect_anomalies,
)


# Synthetic normal telemetry for demonstration.
training_data = [
    [100, 2, 100, 150],
    [110, 3, 105, 160],
    [95, 2, 98, 145],
    [120, 4, 110, 170],
    [105, 2, 102, 155],
    [90, 3, 95, 140],
    [115, 3, 108, 165],
    [100, 2, 101, 150],
    [108, 4, 104, 158],
    [98, 3, 99, 148],
    [112, 2, 106, 162],
    [102, 3, 103, 152],
    [92, 2, 97, 143],
    [118, 3, 109, 168],
    [107, 2, 104, 157],
    [96, 4, 100, 149],
    [113, 3, 107, 163],
    [103, 2, 102, 153],
    [99, 3, 101, 151],
    [109, 2, 105, 159],
]


# Train the model.
model = train_model(training_data)


# Normal and intentionally unusual observations.
test_data = [
    [105, 3, 103, 155],
    [98, 2, 99, 148],
    [10000, 80, 5000, 9000],
]

results = detect_anomalies(model, test_data)

for features, result in zip(test_data, results):
    print("\nObservation:", features)
    print("Features:", FEATURE_NAMES)
    print("Prediction:", "ANOMALY" if result.is_anomaly else "NORMAL")
    print("Anomaly score:", round(result.anomaly_score, 4))

