"""
FloraGuard — CNN Modülü (Yaprak Görüntüsü Sınıflandırma)
Sprint 1'deki `model_prototypes.py::LeafCNN` mimarisi buraya taşındı ve
`CNNPredictor` inference sarmalayıcısı ile üretim kullanımı için hazırlandı.

Sorumluluk sınırı: Bu modül YALNIZCA görüntüden sınıf olasılığı üretir.
Ensemble/regresyon/agent mantığı bilerek burada YOKTUR (katman ayrımı).
"""

from __future__ import annotations

import logging
from io import BytesIO
from pathlib import Path

import torch
import torch.nn as nn
from PIL import Image, UnidentifiedImageError
from torchvision import transforms

logger = logging.getLogger(__name__)

MIN_IMAGE_DIMENSION_PX = 16
# Top-1 ve top-2 sınıf olasılıkları bu değerden daha az ayrışırsa tahmin
# "belirsiz" (uncertain) olarak işaretlenir — ör. yaprak dışı bir nesne
# yüklendiğinde model çıktısı neredeyse uniform dağılıma yaklaşır.
UNCERTAINTY_MARGIN = 0.15


class LeafCNN(nn.Module):
    """
    CNN. Girdi: (batch, 3, 128, 128) RGB yaprak görüntüsü.
    Çıktı: (batch, num_classes) sınıf logit'leri.

    BatchNorm + Dropout, sentetik lezyon veri setindeki (bkz. train_cnn.py)
    doku/renk örüntülerine aşırı uyumu (overfitting) azaltmak için eklendi.
    """

    def __init__(self, num_classes: int = 3):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=3, padding=1),
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.MaxPool2d(2),  # 128 -> 64
            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2),  # 64 -> 32
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2),  # 32 -> 16
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d(1),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Dropout(0.3),
            nn.Linear(128, num_classes),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.classifier(self.features(x))


_PREPROCESS = transforms.Compose([
    transforms.Resize((128, 128)),
    transforms.ToTensor(),
])


class CNNPredictor:
    """
    Görüntü ön-işleme + model çıkarımını tek arayüzde toplar.
    Ağırlık dosyası bulunamazsa (henüz eğitilmemiş model), rastgele başlatılmış
    ağırlıklarla çalışır ve uyarı loglar — böylece sistem uçtan uca test edilebilir
    kalır, ama gerçek tahmin kalitesi eğitim sonrasına kadar garanti edilmez.
    """

    def __init__(self, num_classes: int, class_names: tuple[str, ...], weights_path: Path | None = None):
        self.class_names = class_names
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = LeafCNN(num_classes=num_classes).to(self.device)

        if weights_path and weights_path.exists():
            state_dict = torch.load(weights_path, map_location=self.device)
            self.model.load_state_dict(state_dict)
            logger.info("CNN ağırlıkları yüklendi: %s", weights_path)
        else:
            logger.warning(
                "CNN ağırlık dosyası bulunamadı (%s) — model EĞİTİLMEMİŞ rastgele "
                "ağırlıklarla çalışıyor. Sprint 2 sonunda gerçek eğitim yapılmalı.",
                weights_path,
            )
        self.model.eval()

    @staticmethod
    def _decode_image(image_bytes: bytes) -> Image.Image:
        """Ham baytları RGB PIL görüntüsüne çevirir; bozuk/desteklenmeyen
        dosyalarda anlaşılır bir hata fırlatır (API katmanı bunu 422'ye çevirir)."""
        if not image_bytes:
            raise ValueError("Yüklenen görüntü dosyası boş.")
        try:
            image = Image.open(BytesIO(image_bytes))
            image.load()  # Kesik/bozuk dosyaları burada, erken yakalar.
        except (UnidentifiedImageError, OSError) as exc:
            raise ValueError("Yüklenen dosya geçerli bir JPEG/PNG görüntüsü değil.") from exc

        if image.width < MIN_IMAGE_DIMENSION_PX or image.height < MIN_IMAGE_DIMENSION_PX:
            raise ValueError(
                f"Görüntü çok küçük ({image.width}x{image.height}px). "
                f"En az {MIN_IMAGE_DIMENSION_PX}x{MIN_IMAGE_DIMENSION_PX}px olmalı."
            )
        return image.convert("RGB")

    @torch.inference_mode()
    def predict(self, image_bytes: bytes) -> dict:
        """Ham görüntü baytlarından sınıf olasılıklarını döner."""
        image = self._decode_image(image_bytes)
        tensor = _PREPROCESS(image).unsqueeze(0).to(self.device)  # (1, 3, 128, 128)

        logits = self.model(tensor)
        probs = torch.softmax(logits, dim=1).squeeze(0).cpu().tolist()

        class_probabilities = dict(zip(self.class_names, probs))
        healthy_key = self.class_names[0]
        diseased_probability = 1.0 - class_probabilities.get(healthy_key, 0.0)

        sorted_probs = sorted(probs, reverse=True)
        top1_top2_margin = sorted_probs[0] - sorted_probs[1] if len(sorted_probs) > 1 else 1.0

        return {
            "class_probabilities": class_probabilities,
            "diseased_probability": round(diseased_probability, 4),
            "confidence": round(sorted_probs[0], 4),
            "is_uncertain": top1_top2_margin < UNCERTAINTY_MARGIN,
        }
