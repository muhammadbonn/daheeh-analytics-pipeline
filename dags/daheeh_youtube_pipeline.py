# dags/daheeh_youtube_pipeline.py

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from airflow.utils.log.logging_mixin import LoggingMixin
from datetime import datetime, timedelta

import pandas as pd

from src.youtube.client import get_youtube_client
from src.youtube.extract import fetch_playlist_videos, fetch_metadata
from src.youtube.transform import clean_videos
from src.youtube.load import save_to_csv


# ========================
# Logging
# ========================
log = LoggingMixin().log


# ========================
# CONFIG
# ========================
DATA_PATH = "/opt/airflow/data/videos_metadata.csv"
PLAYLIST_FILE = "/opt/airflow/config/playlist_ids.txt"


# ========================
# Default Args (Retries)
# ========================
default_args = {
    "owner": "airflow",
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}


# ========================
# Failure Callback
# ========================
def on_failure_callback(context):
    task_id = context["task_instance"].task_id
    dag_id = context["dag"].dag_id

    log.error(f"Task Failed → DAG: {dag_id}, Task: {task_id}")


# ========================
# Helper
# ========================
def load_playlist_ids():
    with open(PLAYLIST_FILE) as f:
        return [line.strip().replace(",", "") for line in f if line.strip()]


# ========================
# TASK 1
# ========================
def extract_videos():
    log.info("Starting video extraction...")

    youtube = get_youtube_client(Variable.get("YOUTUBE_API_KEY"))
    playlist_ids = load_playlist_ids()

    videos = []
    for pid in playlist_ids:
        log.info(f"Processing playlist: {pid}")
        videos.extend(fetch_playlist_videos(youtube, pid))

    df = clean_videos(pd.DataFrame(videos))

    if df.empty:
        raise ValueError("No videos extracted")

    path = "/opt/airflow/data/raw_videos.csv"
    df.to_csv(path, index=False)

    log.info(f"Raw videos saved → {path}")
    return path


# ========================
# TASK 2
# ========================
def extract_metadata(ti):
    log.info("Starting metadata extraction...")

    youtube = get_youtube_client(Variable.get("YOUTUBE_API_KEY"))

    file_path = ti.xcom_pull(task_ids="extract_videos")
    df = pd.read_csv(file_path)

    meta_df = fetch_metadata(youtube, df["VideoID"].tolist())

    if meta_df.empty:
        raise ValueError("Metadata extraction failed")

    final_df = df.merge(meta_df, on="VideoID", how="left")

    path = "/opt/airflow/data/final_videos.csv"
    final_df.to_csv(path, index=False)

    log.info(f"Metadata merged and saved → {path}")
    return path


# ========================
# TASK 3
# ========================
def save_final(ti):
    log.info("Starting final save step...")

    file_path = ti.xcom_pull(task_ids="extract_metadata")
    df = clean_videos(pd.read_csv(file_path))

    save_to_csv(df, DATA_PATH)

    log.info("Pipeline completed successfully")


# ========================
# DAG
# ========================
with DAG(
    dag_id="daheeh_youtube_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule="@once",
    catchup=False,
    default_args=default_args,
    tags=["youtube", "daheeh"],
) as dag:

    t1 = PythonOperator(
        task_id="extract_videos",
        python_callable=extract_videos,
        on_failure_callback=on_failure_callback,
    )

    t2 = PythonOperator(
        task_id="extract_metadata",
        python_callable=extract_metadata,
        on_failure_callback=on_failure_callback,
    )

    t3 = PythonOperator(
        task_id="save_final",
        python_callable=save_final,
        on_failure_callback=on_failure_callback,
    )

    t1 >> t2 >> t3