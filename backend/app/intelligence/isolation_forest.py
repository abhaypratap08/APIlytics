
from dataclasses import dataclass

from sklearn.ensemble import IsolationForest


# Keep feature order consistent during training and prediction.
FEATURE_NAMES = [
    "request_count",
    "error_rate_pct",
    "avg_latency_ms",
    "p95_latency_ms",
]


@dataclass
class AnomalyResult:
    is_anomaly: bool
    anomaly_score: float
    prediction: int


def create_model(
    contamination: float = 0.05,
    random_state: int = 42,
) -> IsolationForest:
    """
    Create an Isolation Forest model.

    contamination represents the expected proportion
    of unusual observations in the training data.
    """
    if not 0 < contamination <= 0.5:
        raise ValueError("contamination must be between 0 and 0.5")

    return IsolationForest(
        n_estimators=100,
        contamination=contamination,
        random_state=random_state,
    )


def train_model(training_data: list[list[float]]) -> IsolationForest:
    """
    Train using numerical telemetry features.
    """
    if len(training_data) < 2:
        raise ValueError("At least two training samples are required")

    for row in training_data:
        if len(row) != len(FEATURE_NAMES):
            raise ValueError("Invalid feature count")

        if any(value < 0 for value in row):
            raise ValueError("Features cannot be negative")

    model = create_model()
    model.fit(training_data)

    return model


def detect_anomalies(
    model: IsolationForest,
    observations: list[list[float]],
) -> list[AnomalyResult]:
    """
    Predict whether each observation is normal or anomalous.

    Prediction:
        1  = normal
       -1  = anomaly
    """
    if not observations:
        return []

    for row in observations:
        if len(row) != len(FEATURE_NAMES):
            raise ValueError("Invalid feature count")

        if any(value < 0 for value in row):
            raise ValueError("Features cannot be negative")

    predictions = model.predict(observations)
    scores = model.decision_function(observations)

    return [
        AnomalyResult(
            is_anomaly=prediction == -1,
            anomaly_score=float(score),
            prediction=int(prediction),
        )
        for prediction, score in zip(predictions, scores)
    ]

