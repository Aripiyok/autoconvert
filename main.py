
import os, re, yt_dlp
from telethon import TelegramClient, events
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

SOURCE_CHANNEL = "https://t.me/CHANNEL_SUMBER"
TARGET_CHANNEL = "https://t.me/CHANNEL_TUJUAN"

TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

client = TelegramClient("session", API_ID, API_HASH)

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
        caption = info.get("description", "")
        return filename, caption

@client.on(events.NewMessage(chats=SOURCE_CHANNEL))
async def handler(event):
    if not event.text:
        return
    url = extract_url(event.text)
    if not url:
        return
    try:
        video, caption = download_video(url)
        final_caption = caption.strip() + load_hashtags()
        await client.send_file(
            TARGET_CHANNEL,
            video,
            caption=final_caption,
            supports_streaming=True
        )
        os.remove(video)
    except Exception as e:
        print("ERROR:", e)

print("BOT AUTO REPOST AKTIF")
client.start()
client.run_until_disconnected()
