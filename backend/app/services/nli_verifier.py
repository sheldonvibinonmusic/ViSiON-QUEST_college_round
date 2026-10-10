"""
Local NLI Verification Service using DeBERTa.
Optional assessment signal comparing evidence premise to claim hypothesis.
Gracefully falls back to rules-only mode if dependencies or weights are unavailable.
"""
from typing import Optional, Dict, Any, Tuple
import logging

from backend.app.config import settings

logger = logging.getLogger("second_opinion.nli")

class NLIVerifier:
    """
    Singleton lazy loader for local DeBERTa NLI.
    """
    _instance: Optional["NLIVerifier"] = None

    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.label_map = None  # maps label string ('entailment', 'contradiction', 'neutral') to index
        self.is_loaded = False
        self.load_attempted = False
        self.load_error: Optional[str] = None

    @classmethod
    def get_instance(cls) -> "NLIVerifier":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load_model(self) -> bool:
        """
        Attempt to load model and tokenizer lazily.
        Returns True if loaded, False otherwise.
        """
        if self.load_attempted:
            return self.is_loaded

        self.load_attempted = True

        if not settings.MODEL_ENABLED:
            logger.info("Local NLI model is disabled by configuration (MODEL_ENABLED=false).")
            return False

        try:
            import torch
            from transformers import AutoTokenizer, AutoModelForSequenceClassification

            logger.info(f"Loading NLI model '{settings.MODEL_ID}' on device '{settings.DEVICE}'...")
            self.tokenizer = AutoTokenizer.from_pretrained(settings.MODEL_ID)
            self.model = AutoModelForSequenceClassification.from_pretrained(settings.MODEL_ID)
            self.model.to(settings.DEVICE)
            self.model.eval()

            # Dynamic runtime inspection of model's id2label mapping (§9.6, line 516)
            raw_id2label = getattr(self.model.config, "id2label", None)
            if raw_id2label:
                self.label_map = {str(v).lower(): int(k) for k, v in raw_id2label.items()}
            else:
                # Default MNLI mapping if not present
                self.label_map = {"contradiction": 0, "neutral": 1, "entailment": 2}

            self.is_loaded = True
            logger.info(f"Successfully loaded NLI model. Label mapping: {self.label_map}")
            return True

        except Exception as exc:
            self.load_error = str(exc)
            logger.warning(
                f"Could not load local NLI model '{settings.MODEL_ID}': {exc}. "
                "Operating in rules-only verification mode."
            )
            self.is_loaded = False
            return False

    def predict_pair(
        self,
        premise: str,
        hypothesis: str
    ) -> Optional[Dict[str, float]]:
        """
        Run inference: premise (source passage), hypothesis (claim).
        Returns normalized class scores dict or None if model is unavailable.
        """
        if not self.is_loaded and not self.load_model():
            return None

        try:
            import torch

            inputs = self.tokenizer(
                premise,
                hypothesis,
                truncation=True,
                max_length=512,
                return_tensors="pt"
            )
            inputs = {k: v.to(settings.DEVICE) for k, v in inputs.items()}

            with torch.no_grad():
                logits = self.model(**inputs).logits
                probs = torch.softmax(logits, dim=-1).squeeze().tolist()

            scores = {}
            for label, idx in self.label_map.items():
                scores[label] = round(float(probs[idx]), 4)

            return scores

        except Exception as exc:
            logger.error(f"Inference error during NLI prediction: {exc}")
            return None
