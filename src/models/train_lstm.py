"""
FloraGuard — LSTM Baseline Eğitim Scripti

Sentetik hava durumu zaman serileriyle baseline LSTM ağırlıkları üretir.
Üretilen `artifacts/weather_lstm.pt` dosyası inference sırasında
LSTMPredictor tarafından yüklenir.

Çalıştırma:
    python -m src.models.train_lstm
"""

from __future__ import annotations

import logging
import sys

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset

from src.config import get_settings
from src.models.lstm_model import NUM_FEATURES, WeatherLSTM

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

RANDOM_SEED = 42
EPOCHS = 8
BATCH_SIZE = 32
N_SAMPLES = 800
SEQ_LEN = 14


class SyntheticWeatherDataset(Dataset):
    """Sentetik hava serisi ve risk etiketi."""

    def __init__(self, n_samples: int, seq_len: int, seed: int = RANDOM_SEED):
        generator = torch.Generator().manual_seed(seed)
        self.series = torch.rand(n_samples, seq_len, NUM_FEATURES, generator=generator) * 100
        humidity = self.series[:, :, 1] / 100.0
        temp_norm = self.series[:, :, 0] / 100.0
        rain_norm = self.series[:, :, 2] / 100.0
        risk = torch.clamp(0.35 * humidity + 0.35 * temp_norm + 0.30 * rain_norm, 0.0, 1.0)
        self.labels = risk.mean(dim=1, keepdim=True)

    def __len__(self) -> int:
        return len(self.labels)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        return self.series[idx], self.labels[idx]


def main() -> None:
    settings = get_settings()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    dataset = SyntheticWeatherDataset(N_SAMPLES, SEQ_LEN)
    loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

    model = WeatherLSTM(num_features=NUM_FEATURES).to(device)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

    logger.info("LSTM baseline eğitimi başlıyor (%d epoch, %d örnek)...", EPOCHS, N_SAMPLES)
    model.train()
    for epoch in range(1, EPOCHS + 1):
        total_loss = 0.0
        for series, labels in loader:
            series, labels = series.to(device), labels.to(device)
            optimizer.zero_grad()
            loss = criterion(model(series), labels)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        logger.info("Epoch %d/%d — loss: %.4f", epoch, EPOCHS, total_loss / len(loader))

    settings.lstm_weights_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), settings.lstm_weights_path)
    logger.info("LSTM ağırlıkları kaydedildi: %s", settings.lstm_weights_path)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        logger.error("LSTM eğitimi başarısız: %s", exc)
        sys.exit(1)
