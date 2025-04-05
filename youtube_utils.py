import os
import streamlit as st
import requests
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable

# Load environment variables
load_dotenv()

# Prefer Streamlit secrets; fallback to .env (for local dev)
YOUTUBE_API_KEY = st.secrets.get("YOUR_YOUTUBE_API_KEY", os.getenv("YOUR_YOUTUBE_API_KEY"))
SCRAPERAPI_KEY = st.secrets.get("SCRAPERAPI_KEY", os.getenv("SCRAPERAPI_KEY"))

def extract_video_id(url):
    """Extract YouTube Video ID from URL"""
    try:
        if "youtube.com/watch?v=" in url:
            return url.split("v=")[1].split("&")[0]
        elif "youtu.be/" in url:
            return url.split("youtu.be/")[1].split("?")[0]
        else:
            return None
    except:
        return None

def get_video_title(video_id):
    """Fetch Video Title using YouTube API"""
    try:
        if not YOUTUBE_API_KEY:
            return "⚠️ YouTube API Key Missing"

        url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={YOUTUBE_API_KEY}"
        response = requests.get(url)

        if response.status_code == 403:
            return "❌ API Key Quota Exceeded - Try another key."
        elif response.status_code == 401:
            return "❌ Invalid YouTube API Key."

        response.raise_for_status()
        data = response.json()
        return data.get("items", [{}])[0].get("snippet", {}).get("title", "⚠️ Title Not Found")

    except requests.exceptions.RequestException as e:
        return f"⚠️ YouTube API Error: {e}"

def fetch_youtube_transcript(video_id):
    """Fetch YouTube Video Transcript using proxy (ScraperAPI)"""
    try:
        if not SCRAPERAPI_KEY:
            return "⚠️ ScraperAPI key missing. Add it to Render secrets."

        # Add ScraperAPI proxy
        proxy = {
            "http": f"http://scraperapi:{SCRAPERAPI_KEY}@proxy-server.scraperapi.com:8001",
            "https": f"http://scraperapi:{SCRAPERAPI_KEY}@proxy-server.scraperapi.com:8001",
        }

        # Pass proxies to YouTubeTranscriptApi
        transcript = YouTubeTranscriptApi.get_transcript(video_id, proxies=proxy)
        return "\n".join([f"[{item['start']:.2f}s] {item['text']}" for item in transcript])

    except TranscriptsDisabled:
        return "⚠️ Transcripts are disabled for this video."
    except NoTranscriptFound:
        return "⚠️ No transcript available for this video."
    except VideoUnavailable:
        return "⚠️ This video is unavailable."
    except Exception as e:
        return f"⚠️ Error fetching transcript: {e}"

