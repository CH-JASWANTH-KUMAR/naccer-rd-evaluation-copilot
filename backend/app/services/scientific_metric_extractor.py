import re

KNOWN_METRICS = [
    "Precision",
    "Recall",
    "F1-score",
    "F1",
    "Accuracy",
    "Specificity",
    "Sensitivity",
    "False Alarm Rate",
    "False Positive Rate",
    "False Negative Rate",
    "AUC",
    "ROC-AUC",
    "MAE",
    "MSE",
    "RMSE",
    "R2",
    "R²",
    "MAPE",
]

KNOWN_MODELS = [
    "LSTM",
    "Random Forest",
    "Gradient Boosting",
    "SVM",
    "Support Vector Machine",
    "CNN",
    "XGBoost",
    "FFT Spectral Analysis",
    "Baseline",
]


class ExtractedMetricResult:
    def __init__(
        self,
        metric_name: str,
        raw_value: str,
        normalized_value: float | None,
        unit: str | None,
        comparison_target: str | None,
        source_text: str,
    ):
        self.metric_name = metric_name
        self.raw_value = raw_value
        self.normalized_value = normalized_value
        self.unit = unit
        self.comparison_target = comparison_target
        self.source_text = source_text


class ScientificMetricExtractor:
    """Extracts reported scientific metrics with strict raw value preservation and safe normalization."""

    @classmethod
    def extract_metrics_from_text(cls, text: str) -> list[ExtractedMetricResult]:
        results: list[ExtractedMetricResult] = []
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        for line in lines:
            # Check for model/comparison target in line
            model_target = cls._detect_model_target(line)

            for metric in KNOWN_METRICS:
                pattern = rf"\b{re.escape(metric)}\b\s*(?:of|=|is|averaged|achieved)?\s*([\d\.]+%?|\b0\.\d+\b|\b\d+\.\d+\b)"
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    raw_val = match.group(1).rstrip(".").strip()
                    norm_val, unit = cls.normalize_metric_value(raw_val, metric)

                    # Create extracted result
                    results.append(
                        ExtractedMetricResult(
                            metric_name=metric if metric != "F1" else "F1-score",
                            raw_value=raw_val,
                            normalized_value=norm_val,
                            unit=unit,
                            comparison_target=model_target,
                            source_text=line[:300],
                        )
                    )

        return results

    @classmethod
    def normalize_metric_value(cls, raw_val: str, metric_name: str) -> tuple[float | None, str | None]:
        clean = raw_val.strip()
        if not clean:
            return None, None

        if clean.endswith("%") or "percent" in clean.lower():
            num_str = clean.replace("%", "").replace("percent", "").strip()
            try:
                val = float(num_str)
                return round(val / 100.0, 4), "ratio"
            except ValueError:
                return None, "%"

        try:
            val = float(clean)
            if 0.0 <= val <= 1.0:
                return val, "ratio"
            return val, "numeric"
        except ValueError:
            return None, None

    @classmethod
    def _detect_model_target(cls, text: str) -> str | None:
        for model in KNOWN_MODELS:
            if re.search(rf"\b{re.escape(model)}\b", text, re.IGNORECASE):
                return model
        return None
