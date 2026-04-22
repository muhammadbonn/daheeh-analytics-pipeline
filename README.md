# 🎥📊 YouTube Data Pipeline & Analytics Dashboard

🔗 **Live Demo:**  
👉 https://daheeh-analytics-pipeline.streamlit.app/

---

## 🚀 Overview

End-to-end **Data Engineering + Analytics project** that:

- Extracts data from YouTube API  
- Processes & cleans the data using Airflow  
- Stores structured data locally  
- Visualizes insights through an interactive Streamlit dashboard  

---

## 🛠 Tech Stack

- 🐍 Python  
- ⚙️ Apache Airflow  
- 🐳 Docker  
- 📊 Pandas  
- 📈 Matplotlib  
- 🌐 Streamlit  

---

## 📦 Project Structure
```
daheeh-analytics-pipeline
│
├── dags/ # Airflow DAGs
├── src/ # ETL logic (extract, transform, load)
├── config/ # playlist IDs
├── data/ # output CSV
├── streamlit/ # dashboard app
├── docker-compose.yml
├── requirements.txt
└── README.md
```


---

## ⚙️ How to Run Locally (Full Pipeline)

### 1️⃣ Clone Repo

```bash
git clone https://github.com/muhammadbonn/daheeh-analytics-pipeline.git
cd daheeh-analytics-pipeline
```

### 2️⃣ Run Airflow (Docker)
```
docker-compose up
```

Airflow UI: http://localhost:2727

### 3️⃣ Create YouTube API Key

Go to: https://console.cloud.google.com/

Enable: YouTube Data API v3

Create API Key

### 4️⃣ Add API Key in Airflow

Open Airflow UI

Go to: Admin → Variables → Add
```
Key: YOUTUBE_API_KEY
Value: YOUR_API_KEY
```

### 5️⃣ Run the Pipeline

Go to DAGs

Enable:
```
daheeh_youtube_pipeline
```
Click ▶️ Trigger

📁 Output File: data/videos_metadata.csv
