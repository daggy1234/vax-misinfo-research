import httpx
import asyncpg
from typing import List
import json
import asyncio
import os
from datetime import datetime


YOUTUBE_API_KEY = os.getenv("YOUTUBE_KEY_A")
YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3"


async def fetch_youtube_video_info(video_id: str, pool: asyncpg.Pool, manual: bool = True):
    url = f"{YOUTUBE_API_URL}/videos?part=snippet&id={video_id}&key={YOUTUBE_API_KEY}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    js = response.json()
    itc = len(js.get("items", []))
    if itc < 1:
        return
    video = js["items"][0]
    tds = video["snippet"].get("topicDetails")
    if tds:
        tds_topics = ",".join(tds.get("topicCategories", [""]))
    else:
        tds_topics = ""
    # Convert timezone aware datetime to non-timezone aware datetime
    try:
        published_at = datetime.fromisoformat(video["snippet"]["publishedAt"])
        published_at = published_at.replace(tzinfo=None)
    except:
        try:
            published_at = datetime.strptime(
                video["snippet"]["publishedAt"], "%Y-%m-%dT%H:%M:%SZ")
            published_at = published_at.replace(tzinfo=None)
        except:
            published_at = datetime.fromtimestamp(0)
            published_at = published_at.replace(tzinfo=None)
    async with pool.acquire() as connection:
        query = "INSERT INTO videos(video_id, channel_id, title, description, thumbnail_url,channel_title, published_at, tags, topics, manual) VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9, $10) ON CONFLICT DO NOTHING;"
        data = (
            video["id"],
            video["snippet"]["channelId"],
            video["snippet"]["title"],
            video["snippet"]["description"],
            video["snippet"]["thumbnails"]["default"]["url"],
            video["snippet"]["channelTitle"],
            published_at,
            ",".join(video["snippet"].get("tags", [""])),
            tds_topics, manual)
        await connection.execute(query, *data)

    return True


async def main():
    pool = await asyncpg.create_pool(user='postgres', password=os.getenv("DATABASE_PASSWORD"),
                                     database='videodata', host='127.0.0.1')
    with open("video_ids.txt", "r") as file:
        lines = file.readlines()
    for line in lines:
        await fetch_youtube_video_info(line.strip(), pool)

if __name__ == "__main__":
    asyncio.run(main())
