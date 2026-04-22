import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ========================
# Config
# ========================
st.set_page_config(page_title="YouTube Analytics", layout="wide")

DATA_PATH = "../data/videos_metadata.csv"


# ========================
# Load Data
# ========================
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)

    # convert numeric
    for col in ["Views", "Likes", "Comments"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Duration
    if "Duration_minutes" not in df.columns:
        if "Duration_seconds" in df.columns:
            df["Duration_minutes"] = df["Duration_seconds"] / 60
        else:
            st.error("Duration column missing")
            st.stop()

    # base cleaning
    df = df.dropna(subset=["Views", "Likes", "Comments", "Duration_minutes", "ChannelName"])

    # ❌ remove shorts
    df = df[df["Duration_minutes"] >= 1]

    # ❌ remove AUC
    df = df[~df["ChannelName"].str.contains("AUC", case=False, na=False)]

    # ✅ keep English only
    def keep_english(text):
        return "".join([c for c in str(text) if ord(c) < 128])

    df["ChannelName"] = df["ChannelName"].apply(keep_english)
    df = df[df["ChannelName"].str.strip() != ""]

    return df


df = load_data()

st.title("📊 YouTube Video Analytics")

# ========================
# Sidebar Controls
# ========================

st.sidebar.header("Filters")

# Channels
channels = st.sidebar.multiselect(
    "Select Channels",
    options=sorted(df["ChannelName"].unique()),
    default=list(df["ChannelName"].unique())
)

# Mode
mode = st.sidebar.radio(
    "Select Analysis Mode",
    [
        "All Data",
        "Remove Outliers (IQR)",
        "Limit by Views"
    ]
)

# View threshold (يظهر بس لو اختار mode 3)
view_limit = None
if mode == "Limit by Views":
    view_limit = st.sidebar.selectbox(
        "Max Views",
        [1_000_000, 8_000_000, 10_000_000, 12_000_000],
        format_func=lambda x: f"{x:,}"
    )

# ========================
# Apply Filters
# ========================
filtered_df = df[df["ChannelName"].isin(channels)].copy()

# Mode logic
if mode == "Remove Outliers (IQR)":
    Q1 = filtered_df["Views"].quantile(0.25)
    Q3 = filtered_df["Views"].quantile(0.75)
    IQR = Q3 - Q1

    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR

    filtered_df = filtered_df[
        (filtered_df["Views"] >= lower) &
        (filtered_df["Views"] <= upper)
    ]

elif mode == "Limit by Views":
    filtered_df = filtered_df[filtered_df["Views"] <= view_limit]


# ========================
# Plot Function
# ========================
def plot_scatter(x, y, title, ylabel):
    fig, ax = plt.subplots()

    for channel in filtered_df["ChannelName"].unique():
        data = filtered_df[filtered_df["ChannelName"] == channel]
        ax.scatter(data[x], data[y], label=channel, alpha=0.6)

    # Trend line
    if len(filtered_df) > 1:
        z = np.polyfit(filtered_df[x], filtered_df[y], 1)
        p = np.poly1d(z)
        ax.plot(filtered_df[x], p(filtered_df[x]), linestyle="--")

    ax.set_xlabel("Duration (minutes)")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(fontsize=8)

    return fig


# ========================
# Plots
# ========================
st.subheader("Duration vs Views")
st.pyplot(plot_scatter("Duration_minutes", "Views", "Duration vs Views", "Views"))

st.subheader("Duration vs Likes")
st.pyplot(plot_scatter("Duration_minutes", "Likes", "Duration vs Likes", "Likes"))

st.subheader("Duration vs Comments")
st.pyplot(plot_scatter("Duration_minutes", "Comments", "Duration vs Comments", "Comments"))


# ========================
# Insight
# ========================
st.markdown("## 🎯 Best Video Duration Insight")

filtered_df["Duration_bucket"] = pd.cut(
    filtered_df["Duration_minutes"],
    bins=[0, 5, 10, 15, 20, 30, 60]
)

grouped = filtered_df.groupby("Duration_bucket")["Views"].mean().reset_index()

if len(grouped) > 0:
    best_row = grouped.sort_values("Views", ascending=False).iloc[0]
    interval = best_row["Duration_bucket"]

    best_range = f"{int(interval.left)} - {int(interval.right)} minutes"

    st.success(f"🔥 Best duration: {best_range}")
    st.info(f"📈 Avg views: {int(best_row['Views']):,}")
else:
    st.warning("Not enough data for insight")


# ========================
# KPIs
# ========================
st.markdown("---")

col1, col2, col3 = st.columns(3)

col1.metric("Total Videos", len(filtered_df))
col2.metric("Total Views", f"{int(filtered_df['Views'].sum()):,}")
col3.metric("Avg Duration (min)", round(filtered_df["Duration_minutes"].mean(), 2))