"""Validate regression fixtures before generating evaluation metrics."""

from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = ("message", "intent", "urgency")


def load_evaluation_frame(path: Path) -> pd.DataFrame:
    """Fail on missing, empty, or duplicated labels instead of emitting misleading metrics."""
    frame = pd.read_csv(path)
    missing = set(REQUIRED_COLUMNS) - set(frame.columns)
    if missing:
        raise ValueError(f"Missing evaluation columns: {', '.join(sorted(missing))}")
    if frame.empty:
        raise ValueError("Evaluation dataset has no tickets")

    for name in REQUIRED_COLUMNS:
        values = frame[name]
        if values.isna().any() or values.astype(str).str.strip().eq("").any():
            raise ValueError(f"Evaluation column {name} contains empty values")

    normalized_messages = frame["message"].str.strip().str.casefold()
    if normalized_messages.duplicated().any():
        raise ValueError("Evaluation dataset contains duplicate ticket messages")

    return frame
