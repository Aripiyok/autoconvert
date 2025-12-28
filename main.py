import os
import re
import yt_dlp
from telethon import TelegramClient, events
from dotenv import load_dotenv

# ================= LOAD ENV =================
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

SOURCE_CHANNEL = int(os.getenv("SOURCE_CHANNEL_ID"))
TARGET_CHANNEL = int(os.getenv("TARGET_CHANNEL_ID"))

TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

# ================= CLIENT =================
client = TelegramClient("session", API_ID, API_HASH)

# ================= UTIL =================
def extract_url(text):
    urls = re.findall(r"https?://\S+", text)
    return urls[0] if urls else None

def load_hashtags():
    if not os.path.exists("hashtag.txt"):
        return ""
    with open("hashtag.txt", "r", encoding="utf-8") as f:
        tags = [x.strip() for x in f if x.strip()]
    return "\n\n" + " ".join(tags)

def download_video(url):
    ydl_opts = {
        "outtmpl": f"{TEMP_DIR}/%(id)s.%(ext)s",
        "format": "mp4",
        "quiet": True,
        "no_warnings": True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        caption = info.get("description", "") or ""
        return filename, caption

# ================= HANDLER =================
@client.on(events.NewMessage(chats=SOURCE_CHANNEL))
async def repost_handler(event):
    if not event.text:
        return

    url = extract_url(event.text)
    if not url:
        return

    try:
        video_path, original_caption = download_video(url)
        final_caption = original_caption.strip() + load_hashtags()

        await client.send_file(
            TARGET_CHANNEL,
            video_path,
            caption=final_caption,
            supports_streaming=True
        )

        os.remove(video_path)

    except Exception as e:
        print("ERROR:", e)

# ================= RUN =================
print("🚀 BOT AUTO REPOST REAL-TIME (PRIVATE CHANNEL MODE)")
client.start()
client.run_until_disconnected()
