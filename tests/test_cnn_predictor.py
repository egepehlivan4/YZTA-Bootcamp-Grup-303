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
