"""
FloraGuard — Geçmiş Kayıt Görüntüleme/Düzenleme/Silme RBAC Testleri

İzin matrisi:
  Görüntüleme: Çiftçi -> yalnızca kendi; Danışman -> kendi + çiftçiler;
               Admin -> herkes.
  Düzenleme/Silme: Çiftçi -> hiçbiri; Danışman -> yalnızca çiftçi kayıtları;
               Admin -> çiftçi + danışman kayıtları.
"""

from __future__ import annotations

from io import BytesIO
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from src.api.main import create_app


@pytest.fixture
def client():
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def _force_deterministic_pipeline():
    """
    Bu dosyadaki testler RBAC matrisini doğrular, ajan davranışını değil —
    gerçek LLM'i her testte çağırmak yavaş/maliyetli/kırılgan olur. Agent
    yolunu devre dışı bırakıp hızlı, deterministik fallback'i zorluyoruz
    (bkz. test_predict_integration.py'deki aynı desen).
    """
    with patch("src.agent.orchestrator.OrchestratorService._analyze_with_agent") as mock_agent:
        mock_agent.side_effect = RuntimeError("agent disabled for RBAC tests")
        yield


def _token(client: TestClient, username: str, password: str) -> str:
    response = client.post("/api/auth/token", data={"username": username, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def _headers(client: TestClient, username: str, password: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {_token(client, username, password)}"}


def _create_record(client: TestClient, headers: dict[str, str], farmer_id: str) -> int:
    image = Image.new("RGB", (128, 128), color=(34, 139, 34))
    buffer = BytesIO()
    image.save(buffer, format="JPEG")

    response = client.post(
        "/api/predict",
        headers=headers,
        data={"farmer_id": farmer_id, "location": "Antalya", "crop_type": "domates"},
        files={"image": ("leaf.jpg", buffer.getvalue(), "image/jpeg")},
    )
    assert response.status_code == 200

    history = client.get(f"/api/history/{farmer_id}", headers=headers).json()
    return history[0]["id"]


# --- Görüntüleme -------------------------------------------------------

def test_farmer_cannot_view_other_farmer_history(client: TestClient) -> None:
    headers = _headers(client, "ciftci1", "ciftci123")
    response = client.get("/api/history/someone-else", headers=headers)
    assert response.status_code == 403


def test_advisor_cannot_view_admin_history(client: TestClient) -> None:
    headers = _headers(client, "danisman1", "danisman123")
    response = client.get("/api/history/admin1", headers=headers)
    assert response.status_code == 403


def test_advisor_can_view_own_history(client: TestClient) -> None:
    headers = _headers(client, "danisman1", "danisman123")
    response = client.get("/api/history/danisman1", headers=headers)
    assert response.status_code == 200


def test_advisor_can_view_farmer_history(client: TestClient) -> None:
    headers = _headers(client, "danisman1", "danisman123")
    response = client.get("/api/history/ciftci1", headers=headers)
    assert response.status_code == 200


def test_admin_can_view_anyone(client: TestClient) -> None:
    headers = _headers(client, "admin1", "admin123")
    for target in ("ciftci1", "danisman1", "admin1"):
        assert client.get(f"/api/history/{target}", headers=headers).status_code == 200


# --- Düzenleme/Silme -----------------------------------------------------

def test_farmer_cannot_edit_own_record(client: TestClient) -> None:
    farmer_headers = _headers(client, "ciftci1", "ciftci123")
    record_id = _create_record(client, farmer_headers, "ciftci1")

    response = client.put(
        f"/api/history/record/{record_id}", headers=farmer_headers, json={"advice": "deneme"},
    )
    assert response.status_code == 403


def test_advisor_can_edit_farmer_record(client: TestClient) -> None:
    farmer_headers = _headers(client, "ciftci1", "ciftci123")
    record_id = _create_record(client, farmer_headers, "ciftci1")

    advisor_headers = _headers(client, "danisman1", "danisman123")
    response = client.put(
        f"/api/history/record/{record_id}", headers=advisor_headers, json={"advice": "danışman notu"},
    )
    assert response.status_code == 200
    assert response.json()["advice"] == "danışman notu"


def test_advisor_cannot_edit_own_record(client: TestClient) -> None:
    advisor_headers = _headers(client, "danisman1", "danisman123")
    record_id = _create_record(client, advisor_headers, "danisman1")

    response = client.put(
        f"/api/history/record/{record_id}", headers=advisor_headers, json={"advice": "kendi kaydı"},
    )
    assert response.status_code == 403


def test_advisor_cannot_delete_own_record(client: TestClient) -> None:
    advisor_headers = _headers(client, "danisman1", "danisman123")
    record_id = _create_record(client, advisor_headers, "danisman1")

    response = client.delete(f"/api/history/record/{record_id}", headers=advisor_headers)
    assert response.status_code == 403


def test_admin_can_edit_advisor_record(client: TestClient) -> None:
    advisor_headers = _headers(client, "danisman1", "danisman123")
    record_id = _create_record(client, advisor_headers, "danisman1")

    admin_headers = _headers(client, "admin1", "admin123")
    response = client.put(
        f"/api/history/record/{record_id}", headers=admin_headers, json={"advice": "admin notu"},
    )
    assert response.status_code == 200


def test_admin_can_delete_farmer_record(client: TestClient) -> None:
    farmer_headers = _headers(client, "ciftci1", "ciftci123")
    record_id = _create_record(client, farmer_headers, "ciftci1")

    admin_headers = _headers(client, "admin1", "admin123")
    response = client.delete(f"/api/history/record/{record_id}", headers=admin_headers)
    assert response.status_code == 204

    # Silindiğini doğrula: aynı kaydı tekrar silmeye çalışmak 404 dönmeli.
    response = client.delete(f"/api/history/record/{record_id}", headers=admin_headers)
    assert response.status_code == 404


def test_edit_nonexistent_record_returns_404(client: TestClient) -> None:
    admin_headers = _headers(client, "admin1", "admin123")
    response = client.put(
        "/api/history/record/999999", headers=admin_headers, json={"advice": "yok"},
    )
    assert response.status_code == 404


def test_edit_with_no_fields_returns_400(client: TestClient) -> None:
    farmer_headers = _headers(client, "ciftci1", "ciftci123")
    record_id = _create_record(client, farmer_headers, "ciftci1")

    admin_headers = _headers(client, "admin1", "admin123")
    response = client.put(f"/api/history/record/{record_id}", headers=admin_headers, json={})
    assert response.status_code == 400
