# src/youtube/transform.py

import pandas as pd
import logging

logger = logging.getLogger(__name__)


def clean_videos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and prepare data
    """

    if df.empty:
        logger.error("Received empty DataFrame")
        raise ValueError("Empty DataFrame")

    logger.info(f"Starting data cleaning → rows before: {len(df)}")

    # Remove duplicates
    before = len(df)
    df = df.drop_duplicates(subset=["VideoID"])
    after = len(df)

    logger.info(f"Removed duplicates → {before - after} rows dropped")

    # Convert numeric columns
    numeric_cols = ["Views", "Likes", "Comments"]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

            null_count = df[col].isna().sum()
            logger.info(f"{col}: {null_count} null values after conversion")

    # Convert date
    if "PublishedAt" in df.columns:
        df["PublishedAt"] = pd.to_datetime(df["PublishedAt"], errors="coerce")

        null_dates = df["PublishedAt"].isna().sum()
        logger.info(f"PublishedAt: {null_dates} invalid dates")

    logger.info(f"Data cleaning finished → rows after: {len(df)}")

    return df