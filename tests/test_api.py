from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint() -> None:
    with TestClient(app) as client:
        response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_homepage_is_served() -> None:
    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert "Phishing Guard" in response.text


def test_url_scan_returns_classifier_result() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/scan",
            json={
                "kind": "url",
                "text": "http://paypa1-account-verify.example.invalid",
            },
        )

    assert response.status_code == 200
    result = response.json()
    assert result["verdict"] == "likely_phishing"
    assert result["risk_score"] >= 65
    assert 0 <= result["confidence"] <= 1


def test_email_scan_returns_classifier_result() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/api/scan",
            json={
                "kind": "email",
                "text": "Your account is suspended. Verify your password now at http://account-fix.example.invalid",
            },
        )

    assert response.status_code == 200
    assert response.json()["verdict"] == "likely_phishing"


def test_blank_input_is_rejected() -> None:
    with TestClient(app) as client:
        response = client.post("/api/scan", json={"text": "  "})

    assert response.status_code == 422


def test_oversized_input_is_rejected() -> None:
    with TestClient(app) as client:
        response = client.post("/api/scan", json={"text": "x" * 12001})

    assert response.status_code == 422
