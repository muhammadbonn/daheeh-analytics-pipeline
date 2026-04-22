# src/youtube/extract.py

import logging
import pandas as pd
import re

logger = logging.getLogger(__name__)


# ========================
# Duration Parser
# ========================
def parse_duration(duration: str) -> int:
    """
    Convert ISO 8601 duration to seconds
    Example: PT1H2M10S -> 3730 seconds
    """
    if not duration:
        return 0

    pattern = re.compile(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?')
    match = pattern.match(duration)

    if not match:
        return 0

    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)

    return hours * 3600 + minutes * 60 + seconds


# ========================
# Fetch Playlist Videos
# ========================
def fetch_playlist_videos(youtube, playlist_id: str):
    logger.info(f"Start fetching playlist: {playlist_id}")

    videos = []
    next_page_token = None

    try:
        while True:
            request = youtube.playlistItems().list(
                part="contentDetails",
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token
            )

            response = request.execute()

            items = response.get("items", [])
            logger.info(f"Fetched {len(items)} videos from current page")

            for item in items:
                try:
                    videos.append({
                        "VideoID": item["contentDetails"]["videoId"]
                    })
                except KeyError:
                    logger.warning("Missing videoId in one item, skipping")

            next_page_token = response.get("nextPageToken")

            if not next_page_token:
                break

        logger.info(f"Finished playlist {playlist_id} → total videos: {len(videos)}")

    except Exception:
        logger.exception(f"Error while fetching playlist {playlist_id}")
        raise

    return videos


# ========================
# Fetch Metadata
# ========================
def fetch_metadata(youtube, video_ids: list):
    logger.info(f"Start fetching metadata for {len(video_ids)} videos")

    all_data = []

    try:
        for i in range(0, len(video_ids), 50):
            chunk = video_ids[i:i + 50]
            logger.info(f"Processing chunk {i} → {i + len(chunk)}")

            request = youtube.videos().list(
                part="snippet,statistics,contentDetails",  # 🔥 added contentDetails
                id=",".join(chunk)
            )

            response = request.execute()

            items = response.get("items", [])
            logger.info(f"Fetched metadata for {len(items)} videos")

            for item in items:
                snippet = item.get("snippet", {})
                stats = item.get("statistics", {})
                content = item.get("contentDetails", {})

                duration_iso = content.get("duration")

                all_data.append({
                    "VideoID": item.get("id"),
                    "Title": snippet.get("title"),
                    "PublishedAt": snippet.get("publishedAt"),
                    "ChannelName": snippet.get("channelTitle"),
                    "Views": stats.get("viewCount"),
                    "Likes": stats.get("likeCount"),
                    "Comments": stats.get("commentCount"),

                    # 🔥 NEW FIELDS
                    "Duration_seconds": parse_duration(duration_iso),
                })

        if not all_data:
            logger.warning("No metadata fetched")

        logger.info("Metadata fetching completed successfully")

    except Exception:
        logger.exception("Error while fetching metadata")
        raise

    return pd.DataFrame(all_data)