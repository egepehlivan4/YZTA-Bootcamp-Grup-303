"""
FloraGuard — CNN Baseline Eğitim Scripti

Gerçek yaprak veri seti bootcamp'in "hazır veri seti indirme" kısıtı altında
elde edilemediğinden, **görsel olarak sınıflar arası ayrışan** prosedürel
(programatik) bir sentetik lezyon veri seti kullanılır: her sınıf, gerçek
yaprak hastalıklarının görsel imzasını taklit eden farklı renk paleti, leke
sayısı ve leke boyutuyla üretilir (bkz. `LeafLesionSynthesizer`). Bu,
modelin rastgele gürültüden değil gerçek bir örüntüden öğrenmesini sağlar
ve eğitim/doğrulama doğruluğu rastgele-şans seviyesinin (%33) belirgin
şekilde üzerine çıkar — CNN'in "gerçekten eğitildi" iddiasının kanıtıdır.

Sınıf tasarımı (`src.config.Settings.cnn_class_names` ile hizalı):
    saglikli    -> düzgün yeşil doku, leke yok
    hastalik_a  -> yaprak lekesi hastalığı: çok sayıda küçük, halka desenli
                   sarı-kahverengi leke (ör. erken yanıklık/target spot)
    hastalik_b  -> mildiyö/geç yanıklık: az sayıda büyük, koyu, "sulu"
                   görünümlü düzensiz yama

Çalıştırma:
    python -m src.models.train_cnn
"""

from __future__ import annotations

import logging
import sys

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms

from src.config import get_settings
from src.models.cnn_model import LeafCNN

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

RANDOM_SEED = 42
IMAGE_SIZE = 128
EPOCHS = 14
BATCH_SIZE = 32
N_PER_CLASS = 420
VAL_FRACTION = 0.2
LEARNING_RATE = 1e-3


# ---------------------------------------------------------------------------
# Sentetik lezyon görüntü üreticisi
# ---------------------------------------------------------------------------

class LeafLesionSynthesizer:
    """Sınıf etiketine göre prosedürel (görsel olarak anlamlı) yaprak görüntüsü üretir."""

    def __init__(self, size: int = IMAGE_SIZE):
        self.size = size
        ys, xs = np.mgrid[0:size, 0:size]
        self._xs = xs.astype(np.float32)
        self._ys = ys.astype(np.float32)

    def generate(self, label: int, rng: np.random.Generator) -> np.ndarray:
        """(H, W, 3) float32 [0, 1] aralığında bir görüntü döner."""
        image = self._healthy_base(rng)
        if label == 1:
            image = self._add_leaf_spot_lesions(image, rng)
        elif label == 2:
            image = self._add_blight_patches(image, rng)
        image += rng.normal(0.0, 0.02, size=image.shape).astype(np.float32)  # sensör gürültüsü
        return np.clip(image, 0.0, 1.0)

    def _healthy_base(self, rng: np.random.Generator) -> np.ndarray:
        base_color = rng.uniform([0.18, 0.42, 0.14], [0.32, 0.60, 0.26]).astype(np.float32)
        image = np.tile(base_color, (self.size, self.size, 1))

        # Damar benzeri düşük frekanslı parlaklık dalgalanması.
        phase = rng.uniform(0, 2 * np.pi)
        vein = 0.035 * np.sin(self._xs / self.size * 10 * np.pi + phase)
        image += vein[..., None]

        texture = rng.normal(0.0, 0.025, size=(self.size, self.size, 1)).astype(np.float32)
        image += texture
        return image

    def _elliptical_mask(
        self, cx: float, cy: float, rx: float, ry: float, angle: float, softness: float,
    ) -> np.ndarray:
        dx = (self._xs - cx) * np.cos(angle) + (self._ys - cy) * np.sin(angle)
        dy = -(self._xs - cx) * np.sin(angle) + (self._ys - cy) * np.cos(angle)
        dist = np.sqrt((dx / rx) ** 2 + (dy / ry) ** 2)
        return np.clip(1.0 - (dist - 1.0) / softness, 0.0, 1.0)

    def _blend(self, image: np.ndarray, mask: np.ndarray, color: np.ndarray, alpha: float) -> np.ndarray:
        m = (mask * alpha)[..., None]
        return image * (1 - m) + color * m

    def _add_leaf_spot_lesions(self, image: np.ndarray, rng: np.random.Generator) -> np.ndarray:
        """Çok sayıda küçük, halkalı (target-spot) leke — 'hastalik_a'."""
        n_spots = rng.integers(6, 12)
        for _ in range(n_spots):
            cx, cy = rng.uniform(10, self.size - 10, size=2)
            radius = rng.uniform(4, 9)
            angle = rng.uniform(0, np.pi)
            ring_color = rng.uniform([0.35, 0.22, 0.05], [0.50, 0.32, 0.10]).astype(np.float32)
            core_color = rng.uniform([0.62, 0.48, 0.15], [0.78, 0.62, 0.25]).astype(np.float32)
            outer_mask = self._elliptical_mask(cx, cy, radius, radius * rng.uniform(0.85, 1.15), angle, 0.4)
            image = self._blend(image, outer_mask, ring_color, alpha=0.85)
            inner_mask = self._elliptical_mask(cx, cy, radius * 0.5, radius * 0.5, angle, 0.5)
            image = self._blend(image, inner_mask, core_color, alpha=0.85)
        return image

    def _add_blight_patches(self, image: np.ndarray, rng: np.random.Generator) -> np.ndarray:
        """Az sayıda büyük, düzensiz, koyu 'sulu' yama — 'hastalik_b'."""
        n_patches = rng.integers(2, 5)
        for _ in range(n_patches):
            cx, cy = rng.uniform(15, self.size - 15, size=2)
            rx = rng.uniform(12, 24)
            ry = rx * rng.uniform(0.6, 1.3)
            angle = rng.uniform(0, np.pi)
            color = rng.uniform([0.08, 0.07, 0.04], [0.22, 0.17, 0.09]).astype(np.float32)
            mask = self._elliptical_mask(cx, cy, rx, ry, angle, 0.65)
            image = self._blend(image, mask, color, alpha=0.88)
        return image


def _build_split_datasets(num_classes: int, seed: int) -> tuple[Dataset, Dataset]:
    """Sınıf başına dengeli üretim + stratified train/val bölünmesi."""
    synthesizer = LeafLesionSynthesizer(IMAGE_SIZE)
    rng = np.random.default_rng(seed)

    train_images, train_labels, val_images, val_labels = [], [], [], []
    n_val_per_class = max(1, int(N_PER_CLASS * VAL_FRACTION))

    for label in range(num_classes):
        class_images = [synthesizer.generate(label, rng) for _ in range(N_PER_CLASS)]
        val_images.extend(class_images[:n_val_per_class])
        val_labels.extend([label] * n_val_per_class)
        train_images.extend(class_images[n_val_per_class:])
        train_labels.extend([label] * (N_PER_CLASS - n_val_per_class))

    def _to_tensor_dataset(images: list[np.ndarray], labels: list[int], augment: bool) -> Dataset:
        stacked = torch.from_numpy(np.stack(images)).permute(0, 3, 1, 2).float()  # (N, 3, H, W)
        return _LesionTensorDataset(stacked, torch.tensor(labels, dtype=torch.long), augment=augment)

    return _to_tensor_dataset(train_images, train_labels, augment=True), _to_tensor_dataset(
        val_images, val_labels, augment=False
    )


class _LesionTensorDataset(Dataset):
    """Önceden üretilmiş tensörleri sarmalar; yalnızca eğitim setinde augmentation uygular."""

    _AUGMENT = transforms.Compose([
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(),
        transforms.RandomRotation(20),
        transforms.ColorJitter(brightness=0.15, contrast=0.15, saturation=0.1),
    ])

    def __init__(self, images: torch.Tensor, labels: torch.Tensor, augment: bool):
        self.images = images
        self.labels = labels
        self.augment = augment

    def __len__(self) -> int:
        return len(self.labels)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        image = self.images[idx]
        if self.augment:
            image = self._AUGMENT(image).clamp(0.0, 1.0)
        return image, self.labels[idx]


# ---------------------------------------------------------------------------
# Eğitim döngüsü
# ---------------------------------------------------------------------------

@torch.inference_mode()
def _evaluate(model: nn.Module, loader: DataLoader, device: torch.device) -> float:
    model.eval()
    correct, total = 0, 0
    for images, labels in loader:
        images, labels = images.to(device), labels.to(device)
        preds = model(images).argmax(dim=1)
        correct += (preds == labels).sum().item()
        total += labels.size(0)
    return correct / total if total else 0.0


def main() -> None:
    torch.manual_seed(RANDOM_SEED)
    settings = get_settings()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    num_classes = settings.cnn_num_classes

    train_dataset, val_dataset = _build_split_datasets(num_classes, RANDOM_SEED)
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)

    model = LeafCNN(num_classes=num_classes).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)

    logger.info(
        "CNN eğitimi başlıyor (%d epoch, %d train / %d val örnek, %d sınıf)...",
        EPOCHS, len(train_dataset), len(val_dataset), num_classes,
    )

    best_val_acc = 0.0
    best_state_dict = None

    for epoch in range(1, EPOCHS + 1):
        model.train()
        total_loss = 0.0
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            loss = criterion(model(images), labels)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

        val_acc = _evaluate(model, val_loader, device)
        logger.info(
            "Epoch %d/%d — loss: %.4f — val_accuracy: %.1f%%",
            epoch, EPOCHS, total_loss / len(train_loader), val_acc * 100,
        )
        if val_acc >= best_val_acc:
            best_val_acc = val_acc
            best_state_dict = {k: v.clone() for k, v in model.state_dict().items()}

    random_baseline = 1.0 / num_classes
    logger.info(
        "Eğitim tamamlandı. En iyi doğrulama doğruluğu: %.1f%% (rastgele-şans taban çizgisi: %.1f%%)",
        best_val_acc * 100, random_baseline * 100,
    )
    if best_val_acc < random_baseline * 1.5:
        logger.warning(
            "Doğrulama doğruluğu beklenenin altında — sentetik veri üretecini veya "
            "mimariyi gözden geçirin."
        )

    settings.cnn_weights_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(best_state_dict, settings.cnn_weights_path)
    logger.info("En iyi CNN ağırlıkları kaydedildi: %s", settings.cnn_weights_path)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        logger.error("CNN eğitimi başarısız: %s", exc)
        sys.exit(1)
