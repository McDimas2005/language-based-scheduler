from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Any
import shutil

from app.core.config import Settings
from app.core.logging import get_logger
from app.models.schemas import ClassificationResult


logger = get_logger(__name__)


@dataclass
class ClassifierLoadState:
    loaded: bool = False
    error: str | None = None


class BertActivityClassifier:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.labels = settings.bert_labels
        self.model: Any | None = None
        self.tokenizer: Any | None = None
        self.device: Any | None = None
        self.state = ClassifierLoadState()

    def is_loaded(self) -> bool:
        return self.state.loaded

    def is_available(self) -> bool:
        return self.is_loaded()

    def status_warning(self) -> str | None:
        return self.state.error

    def status(self) -> dict[str, Any]:
        return {
            "available": self.is_loaded(),
            "checkpoint_path": str(self.settings.bert_checkpoint_path),
            "labels": self.labels,
            "error": self.state.error,
        }

    def load_model(self) -> bool:
        if self.state.loaded:
            return True

        checkpoint_path = self._ensure_checkpoint()
        if not checkpoint_path.exists():
            self.state.error = self.state.error or f"BERT checkpoint not found at {checkpoint_path}."
            logger.warning(self.state.error)
            return False

        try:
            import torch
            from transformers import BertForSequenceClassification, BertTokenizer
        except Exception as exc:  # pragma: no cover - depends on optional ML deps
            self.state.error = f"BERT dependencies are not installed: {exc}"
            logger.warning(self.state.error)
            return False

        try:  # pragma: no cover - exercised when ML deps are installed
            self.device = torch.device("cpu")
            self.tokenizer = BertTokenizer.from_pretrained(self.settings.bert_base_model)
            self.model = BertForSequenceClassification.from_pretrained(
                self.settings.bert_base_model,
                num_labels=len(self.labels),
            )
            checkpoint = torch.load(checkpoint_path, map_location=self.device)
            state_dict = self._extract_state_dict(checkpoint)
            state_dict = self._strip_module_prefix(state_dict)
            self.model.load_state_dict(state_dict, strict=False)
            self.model.to(self.device)
            self.model.eval()
            self.state = ClassifierLoadState(loaded=True)
            logger.info("Loaded BERT activity classifier from %s with labels %s", checkpoint_path, self.labels)
            return True
        except Exception as exc:
            self.state.error = f"Could not load BERT checkpoint: {exc}"
            logger.exception(self.state.error)
            self.model = None
            self.tokenizer = None
            return False

    def _ensure_checkpoint(self) -> Path:
        checkpoint_path = Path(self.settings.bert_checkpoint_path)
        if checkpoint_path.exists():
            logger.info("BERT checkpoint exists at %s", checkpoint_path)
            return checkpoint_path

        if not self.settings.bert_download_from_hf:
            return checkpoint_path

        if not self.settings.bert_hf_repo_id:
            self.state.error = "BERT_HF_REPO_ID is required when BERT_DOWNLOAD_FROM_HF=true."
            logger.warning(self.state.error)
            return checkpoint_path

        try:
            from huggingface_hub import hf_hub_download
        except Exception as exc:  # pragma: no cover - depends on optional dep
            self.state.error = f"huggingface_hub is not installed: {exc}"
            logger.warning(self.state.error)
            return checkpoint_path

        try:  # pragma: no cover - depends on network/cache
            logger.info(
                "Downloading BERT checkpoint %s from Hugging Face repo %s",
                self.settings.bert_hf_filename,
                self.settings.bert_hf_repo_id,
            )
            downloaded = Path(
                hf_hub_download(
                    repo_id=self.settings.bert_hf_repo_id,
                    filename=self.settings.bert_hf_filename,
                    token=os.environ.get("HF_TOKEN"),
                )
            )
            checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
            if downloaded.resolve() != checkpoint_path.resolve():
                shutil.copyfile(downloaded, checkpoint_path)
            logger.info("BERT checkpoint is ready at %s", checkpoint_path)
        except Exception as exc:
            self.state.error = f"Could not download BERT checkpoint from Hugging Face: {exc}"
            logger.warning(self.state.error)

        return checkpoint_path

    def predict(self, text: str) -> ClassificationResult:
        if not self.load_model():
            return ClassificationResult(
                label="unavailable",
                confidence=0.0,
                class_probabilities={label: 0.0 for label in self.labels},
                loaded=False,
                warning=self.state.error or "BERT classifier is unavailable.",
            )

        import torch  # pragma: no cover

        inputs = self.tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=self.settings.bert_max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )
        input_ids = inputs["input_ids"].to(self.device)
        attention_mask = inputs["attention_mask"].to(self.device)

        with torch.no_grad():
            outputs = self.model(input_ids, attention_mask=attention_mask)
            probabilities = torch.softmax(outputs.logits, dim=1).squeeze(0).cpu().tolist()

        best_idx = max(range(len(probabilities)), key=probabilities.__getitem__)
        return ClassificationResult(
            label=self.labels[best_idx],
            confidence=float(probabilities[best_idx]),
            class_probabilities={
                label: float(probabilities[idx]) for idx, label in enumerate(self.labels)
            },
        )

    @staticmethod
    def _extract_state_dict(checkpoint: Any) -> dict[str, Any]:
        if isinstance(checkpoint, dict):
            if "label_mapping" in checkpoint:
                logger.info("Checkpoint includes label_mapping; configured labels remain authoritative.")
            for key in ("model_state_dict", "state_dict"):
                if key in checkpoint:
                    return checkpoint[key]
        return checkpoint

    @staticmethod
    def _strip_module_prefix(state_dict: dict[str, Any]) -> dict[str, Any]:
        if not any(key.startswith("module.") for key in state_dict):
            return state_dict
        return {key.removeprefix("module."): value for key, value in state_dict.items()}
