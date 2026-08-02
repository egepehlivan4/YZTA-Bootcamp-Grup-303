"""
FloraGuard — Streamlit API İstemcisi Testleri
`src/ui/api_client.py` ağ katmanının başarı/hata yollarını `requests`
kütüphanesini mock'layarak (gerçek backend gerekmeden) doğrular.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import requests

from src.ui import api_client


def _mock_response(status_code: int, json_data: dict | list | None = None, text: str = "") -> MagicMock:
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = json_data if json_data is not None else {}
    response.text = text
    response.content = b"{}" if json_data is not None else b""
    return response


@patch("src.ui.api_client.requests.request")
def test_login_success(mock_request: MagicMock) -> None:
    mock_request.return_value = _mock_response(200, {"access_token": "abc", "role": "farmer"})

    result = api_client.login("ciftci1", "ciftci123")

    assert result.ok
    assert result.data["access_token"] == "abc"


@patch("src.ui.api_client.requests.request")
def test_login_invalid_credentials_returns_error_message(mock_request: MagicMock) -> None:
    mock_request.return_value = _mock_response(401, {"detail": "Kullanıcı adı veya şifre hatalı."})

    result = api_client.login("ciftci1", "wrong")

    assert not result.ok
    assert result.status_code == 401
    assert "hatalı" in result.message


@patch("src.ui.api_client.requests.request")
def test_connection_error_is_handled_gracefully(mock_request: MagicMock) -> None:
    mock_request.side_effect = requests.ConnectionError()

    result = api_client.login("ciftci1", "ciftci123")

    assert not result.ok
    assert result.status_code is None
    assert "ulaşılamadı" in result.message


@patch("src.ui.api_client.requests.request")
def test_timeout_is_handled_gracefully(mock_request: MagicMock) -> None:
    mock_request.side_effect = requests.Timeout()

    result = api_client.predict(
        "fake-token", farmer_id="ciftci1", location="Antalya", crop_type="domates",
        image_name="leaf.jpg", image_bytes=b"fake", image_type="image/jpeg",
    )

    assert not result.ok
    assert "zaman aşımı" in result.message


@patch("src.ui.api_client.requests.request")
def test_predict_success_passes_multipart_payload(mock_request: MagicMock) -> None:
    mock_request.return_value = _mock_response(200, {"farmer_id": "ciftci1", "disease_probability": 0.5})

    result = api_client.predict(
        "fake-token", farmer_id="ciftci1", location="Antalya", crop_type="domates",
        image_name="leaf.jpg", image_bytes=b"fake-bytes", image_type="image/jpeg",
    )

    assert result.ok
    _, kwargs = mock_request.call_args
    assert kwargs["files"]["image"] == ("leaf.jpg", b"fake-bytes", "image/jpeg")
    assert kwargs["data"]["farmer_id"] == "ciftci1"
    assert kwargs["headers"]["Authorization"] == "Bearer fake-token"


@patch("src.ui.api_client.requests.request")
def test_get_history_success(mock_request: MagicMock) -> None:
    mock_request.return_value = _mock_response(200, [{"id": 1, "farmer_id": "ciftci1"}])

    result = api_client.get_history("fake-token", "ciftci1", limit=10)

    assert result.ok
    assert result.data == [{"id": 1, "farmer_id": "ciftci1"}]


@patch("src.ui.api_client.requests.request")
def test_get_history_server_error_uses_raw_text_when_not_json(mock_request: MagicMock) -> None:
    response = MagicMock()
    response.status_code = 500
    response.json.side_effect = ValueError("not json")
    response.text = "Internal Server Error"
    mock_request.return_value = response

    result = api_client.get_history("fake-token", "ciftci1")

    assert not result.ok
    assert result.message == "Internal Server Error"


@patch("src.ui.api_client.requests.request")
def test_update_history_record_success(mock_request: MagicMock) -> None:
    mock_request.return_value = _mock_response(200, {"id": 1, "advice": "yeni tavsiye"})

    result = api_client.update_history_record("fake-token", 1, advice="yeni tavsiye", location=None)

    assert result.ok
    _, kwargs = mock_request.call_args
    assert kwargs["json"] == {"advice": "yeni tavsiye"}  # None alanlar filtrelenmeli


@patch("src.ui.api_client.requests.request")
def test_update_history_record_forbidden(mock_request: MagicMock) -> None:
    mock_request.return_value = _mock_response(403, {"detail": "Bu kaydı düzenleme yetkiniz yok."})

    result = api_client.update_history_record("fake-token", 1, advice="x")

    assert not result.ok
    assert result.status_code == 403


@patch("src.ui.api_client.requests.request")
def test_delete_history_record_success_handles_empty_body(mock_request: MagicMock) -> None:
    """DELETE 204 No Content döner — response.json() çağrılırsa patlar, bu yüzden
    boş gövde özel olarak ele alınmalı."""
    response = MagicMock()
    response.status_code = 204
    response.content = b""
    response.json.side_effect = ValueError("no body")
    mock_request.return_value = response

    result = api_client.delete_history_record("fake-token", 1)

    assert result.ok
    assert result.data is None
