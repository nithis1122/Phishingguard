from contextlib import asynccontextmanager
from enum import Enum
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator
from sklearn.pipeline import Pipeline

from app.classifier import train_classifier

WEB_DIR = Path(__file__).resolve().parent.parent / "web"


class ScanKind(str, Enum):
    url = "url"
    email = "email"
    auto = "auto"


class ScanRequest(BaseModel):
    text: Annotated[str, Field(min_length=1, max_length=12000)]
    kind: ScanKind = ScanKind.auto

    @field_validator("text")
    @classmethod
    def text_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Paste a URL or email message to scan.")
        return value.strip()


@asynccontextmanager
async def lifespan(application: FastAPI):
    application.state.classifier = train_classifier()
    yield


app = FastAPI(
    title="Phishing Guard",
    description="A small text-classification API and web app for phishing awareness.",
    version="1.0.0",
    lifespan=lifespan,
)
app.mount("/static", StaticFiles(directory=WEB_DIR / "static"), name="static")


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/scan")
def scan(request: ScanRequest) -> dict[str, object]:
    classifier: Pipeline | None = getattr(app.state, "classifier", None)
    if classifier is None:
        raise HTTPException(status_code=503, detail="The classifier is not ready.")

    prefix = request.kind.value.upper()
    probabilities = classifier.predict_proba([f"{prefix}: {request.text}"])[0]
    phishing_index = list(classifier.classes_).index("phishing")
    probability = float(probabilities[phishing_index])

    if probability >= 0.65:
        verdict = "likely_phishing"
    elif probability <= 0.35:
        verdict = "likely_safe"
    else:
        verdict = "suspicious"

    return {
        "verdict": verdict,
        "risk_score": round(probability * 100),
        "confidence": round(max(probability, 1 - probability), 3),
        "message": {
            "likely_phishing": "This looks suspicious. Do not click links or share sensitive information.",
            "suspicious": "The result is uncertain. Verify the sender and destination independently.",
            "likely_safe": "The model found fewer phishing patterns, but this is not a guarantee of safety.",
        }[verdict],
        "disclaimer": "This is an experimental model trained on a small sample dataset. It can be wrong; verify important messages through a trusted channel.",
    }
