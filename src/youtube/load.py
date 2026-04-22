# src/youtube/load.py

import os
import logging

logger = logging.getLogger(__name__)


def save_to_csv(df, path: str):
    """
    Save DataFrame to CSV
    """

    if df.empty:
        logger.error("Attempted to save empty DataFrame")
        raise ValueError("No data to save")

    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)

        logger.info(f"Saving data to {path} ...")
        logger.info(f"Number of rows: {len(df)}")

        df.to_csv(path, index=False, encoding="utf-8-sig")

        logger.info(f"Data saved successfully to {path}")

    except Exception:
        logger.exception("Failed to save data to CSV")
        raise