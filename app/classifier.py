import csv
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion, Pipeline

DATASET_PATH = Path(__file__).resolve().parent.parent / "data" / "training_samples.csv"


def create_classifier() -> Pipeline:
    return Pipeline(
        [
            (
                "features",
                FeatureUnion(
                    [
                        (
                            "characters",
                            TfidfVectorizer(
                                analyzer="char_wb",
                                ngram_range=(2, 5),
                                min_df=1,
                                sublinear_tf=True,
                                max_features=20000,
                            ),
                        ),
                        (
                            "words",
                            TfidfVectorizer(
                                analyzer="word",
                                ngram_range=(1, 2),
                                min_df=1,
                                sublinear_tf=True,
                                max_features=20000,
                            ),
                        ),
                    ]
                ),
            ),
            (
                "classifier",
                LogisticRegression(
                    class_weight="balanced",
                    max_iter=1000,
                    random_state=42,
                ),
            ),
        ]
    )


def train_classifier(dataset_path: Path = DATASET_PATH) -> Pipeline:
    texts: list[str] = []
    labels: list[str] = []

    with dataset_path.open(encoding="utf-8", newline="") as dataset_file:
        for row in csv.DictReader(dataset_file):
            text = row["text"].strip()
            label = row["label"].strip()
            if text and label in {"safe", "phishing"}:
                texts.append(text)
                labels.append(label)

    if not texts or set(labels) != {"safe", "phishing"}:
        raise ValueError(
            f"Training data at {dataset_path} must contain examples for both labels."
        )

    return create_classifier().fit(texts, labels)
