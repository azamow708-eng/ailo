import requests
from config import YOUTUBE_API_KEY, AI_API_KEY
from telethon import TelegramClient
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH

tg_client = TelegramClient('anon', TELEGRAM_API_ID, TELEGRAM_API_HASH)

async def get_telegram_stats(channel_username):
    await tg_client.start()
    entity = await tg_client.get_entity(channel_username)
    return {
        "members": entity.participants_count if hasattr(entity, 'participants_count') else None
    }

def get_youtube_stats(channel_id):
    url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={channel_id}&key={YOUTUBE_API_KEY}"
    r = requests.get(url).json()
    stats = r['items'][0]['statistics']
    return {
        "subscribers": stats['subscriberCount'],
        "views": stats['viewCount'],
        "videos": stats['videoCount']
    }

def ai_analysis(prompt):
    headers = {"Authorization": f"Bearer {AI_API_KEY}"}
    data = {"prompt": prompt, "max_tokens":500}
    r = requests.post("https://api.openai.com/v1/completions", json=data, headers=headers)
    return r.json()["choices"][0]["text"]
