import logging
from typing import Tuple, List

import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    classification_report,
)

from zenml import step
from zenml.client import Client


# ------------------ MODEL DEFINITION ------------------
class BrainTumorCNN(nn.Module):
    def __init__(self):
        super(BrainTumorCNN, self).__init__()

        self.layer1 = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )

        self.layer2 = nn.Sequential(
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )

        self.layer3 = nn.Sequential(
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )

        self.fc = nn.Sequential(
            nn.Linear(128 * 18 * 18, 256),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(256, 4),  # number of classes
        )

    def forward(self, x):
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = x.view(x.size(0), -1)
        return self.fc(x)


# ------------------ EVALUATION STEP ------------------
@step
def evaluate_model_step(
    model_path: str,
    test_loader: DataLoader,
    device: str,
    class_names: List[str],
) -> Tuple[float, float, float]:

    # Load model inside the step (ZenML-safe)
    model = BrainTumorCNN()
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()

    y_true, y_pred = [], []

    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(device)
            labels = labels.to(device)

            outputs = model(images)
            _, predicted = torch.max(outputs, 1)

            y_true.extend(labels.cpu().numpy())
            y_pred.extend(predicted.cpu().numpy())

    accuracy = accuracy_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred, average="macro")
    recall = recall_score(y_true, y_pred, average="macro")

    print(classification_report(y_true, y_pred, target_names=class_names))

    # Log metrics to ZenML
    try:
        client = Client()
        client.log_artifact_metadata(
            artifact_name="evaluation_metrics",
            metadata={
                "accuracy": accuracy,
                "precision": precision,
                "recall": recall,
            },
        )
    except Exception as e:
        logging.warning(f"Metadata logging failed: {e}")

    logging.info(f"Evaluation completed | Accuracy: {accuracy:.4f}")

    return accuracy, precision, recall
