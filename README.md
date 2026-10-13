# Phishing Guard

A small browser-based phishing checker backed by a scikit-learn text classifier and a FastAPI API. It can scan a URL or pasted email text. The app does not open links, contact their destinations, keep scan history, or store submitted text.

## Run locally

Requires Python 3.10 or newer.

```powershell
cd phishing-guard
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). Interactive API documentation is available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## API

`POST /api/scan`

```json
{
  "kind": "url",
  "text": "https://example.com/account"
}
```

`kind` can be `url`, `email`, or `auto`. `text` must contain 1–12,000 characters. The response includes a verdict (`likely_phishing`, `suspicious`, or `likely_safe`), a model risk score, and an uncertainty-aware confidence value.

## How it works

On application startup, FastAPI trains a logistic-regression classifier using character and word TF-IDF features from `data/training_samples.csv`. The model is trained locally from the bundled examples; no model downloads or third-party inference APIs are used. Extend or replace the sample CSV with a properly sourced, representative dataset before relying on the classifier for anything beyond a demo.

## Run tests

```powershell
python -m pytest
```

## Docker

```powershell
docker build -t phishing-guard .
docker run --rm -p 8000:8000 phishing-guard
```

## Important limitations

This is an educational prototype, **not a security product**. Its included training dataset is small and illustrative, and its scores are not calibrated probabilities or measured accuracy. It can miss attacks and flag legitimate content. Do not use it as the sole basis for security decisions; verify suspicious messages via a trusted contact method and never enter credentials or one-time codes through unexpected links.
