"""
FloraGuard — CNN Modeli Testleri
CNNPredictor sınıfının ağırlıksız başlatılmasını ve tahmin çıktı formatını test eder.
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image

from src.models.cnn_model import CNNPredictor


def _make_test_image_bytes() -> bytes:
    """Test için 128x128 boyutunda yeşil bir PNG görüntüsü bayt dizisi üretir."""
    img = Image.new("RGB", (128, 128), color=(0, 128, 0))
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_cnn_predictor_initializes_without_weights(tmp_path: Path) -> None:
    """
    Var olmayan bir ağırlık dosyası verildiğinde CNNPredictor'ün rastgele
    ağırlıklarla sorunsuz başlatıldığını doğrular.
    """
    non_existent_weights = tmp_path / "non_existent_cnn.pt"
    predictor = CNNPredictor(
        num_classes=3,
        class_names=("saglikli", "hastalik_a", "hastalik_b"),
        weights_path=non_existent_weights,
    )
    assert predictor.model is not None


def test_cnn_predict_returns_correct_format(tmp_path: Path) -> None:
    """
    predict() metodunun 'class_probabilities' sözlüğü ve 0-1 arasında
    'diseased_probability' float değeri içerdiğini doğrular.
    """
    predictor = CNNPredictor(
        num_classes=3,
        class_names=("saglikli", "hastalik_a", "hastalik_b"),
        weights_path=tmp_path / "non_existent.pt",
    )
    image_bytes = _make_test_image_bytes()
    result = predictor.predict(image_bytes)

    assert "class_probabilities" in result
    assert "diseased_probability" in result

    class_probs = result["class_probabilities"]
    assert isinstance(class_probs, dict)
    assert set(class_probs.keys()) == {"saglikli", "hastalik_a", "hastalik_b"}

    diseased_prob = result["diseased_probability"]
    assert isinstance(diseased_prob, float)
    assert 0.0 <= diseased_prob <= 1.0


def test_cnn_predict_probabilities_sum_to_one(tmp_path: Path) -> None:
    """
    Model tarafından tahmin edilen sınıf olasılıklarının toplamının yaklaşık 1.0 olduğunu doğrular.
    """
    predictor = CNNPredictor(
        num_classes=3,
        class_names=("saglikli", "hastalik_a", "hastalik_b"),
        weights_path=tmp_path / "non_existent.pt",
    )
    image_bytes = _make_test_image_bytes()
    result = predictor.predict(image_bytes)

    total_prob = sum(result["class_probabilities"].values())
    assert total_prob == pytest.approx(1.0, abs=1e-3)


def test_cnn_predict_includes_confidence_and_uncertainty_fields(tmp_path: Path) -> None:
    """predict() çıktısı, uç durum yönetimi için confidence/is_uncertain alanlarını içermeli."""
    predictor = CNNPredictor(
        num_classes=3,
        class_names=("saglikli", "hastalik_a", "hastalik_b"),
        weights_path=tmp_path / "non_existent.pt",
    )
    result = predictor.predict(_make_test_image_bytes())

    assert 0.0 <= result["confidence"] <= 1.0
    assert isinstance(result["is_uncertain"], bool)


def test_cnn_predict_rejects_empty_bytes(tmp_path: Path) -> None:
    """Boş dosya baytları anlaşılır bir ValueError ile reddedilmeli (500 yerine)."""
    predictor = CNNPredictor(
        num_classes=3,
        class_names=("saglikli", "hastalik_a", "hastalik_b"),
        weights_path=tmp_path / "non_existent.pt",
    )
    with pytest.raises(ValueError):
        predictor.predict(b"")


def test_cnn_predict_rejects_corrupt_bytes(tmp_path: Path) -> None:
    """Görüntü olmayan/bozuk baytlar (ör. metin dosyası) ValueError ile reddedilmeli."""
    predictor = CNNPredictor(
        num_classes=3,
        class_names=("saglikli", "hastalik_a", "hastalik_b"),
        weights_path=tmp_path / "non_existent.pt",
    )
    with pytest.raises(ValueError):
        predictor.predict(b"bu bir goruntu dosyasi degil, duz metin")


def test_cnn_predict_rejects_too_small_image(tmp_path: Path) -> None:
    """Minimum boyutun (16x16px) altındaki görüntüler ValueError ile reddedilmeli."""
    tiny_image = Image.new("RGB", (4, 4), color=(0, 128, 0))
    buf = BytesIO()
    tiny_image.save(buf, format="PNG")

    predictor = CNNPredictor(
        num_classes=3,
        class_names=("saglikli", "hastalik_a", "hastalik_b"),
        weights_path=tmp_path / "non_existent.pt",
    )
    with pytest.raises(ValueError):
        predictor.predict(buf.getvalue())
