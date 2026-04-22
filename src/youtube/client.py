# src/youtube/client.py

from googleapiclient.discovery import build
import logging

# Create logger
logger = logging.getLogger(__name__)


def get_youtube_client(api_key: str):
    """
    Create YouTube API client
    """

    if not api_key:
        logger.error("YouTube API key is missing")
        raise ValueError("API key is missing")

    try:
        logger.info("Initializing YouTube client...")
        client = build("youtube", "v3", developerKey=api_key)
        logger.info("YouTube client initialized successfully")
        return client

    except Exception as e:
        logger.exception("Failed to initialize YouTube client")
        raise