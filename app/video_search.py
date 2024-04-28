import httpx
import json
import asyncio
from datetime import datetime, timedelta
import asyncpg
from app.video_proc import fetch_youtube_video_info
import os
YOUTUBE_API_KEY = os.getenv("YOUTUBE_KEY_A")
YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3"


async def search_videos(keyword: str, file_name: str, pool, vids_ids: list[str]) -> list[str]:
    # Get the current date and time
    now = datetime.now()
    one_day_ago = now - timedelta(days=1)
    formatted_date = one_day_ago.strftime('%Y-%m-%dT%H:%M:%SZ')

    params = {
        "part": "snippet",
        "maxResults": 50,
        "q": keyword,
        "key": YOUTUBE_API_KEY,
        "order": "relevance",
        "regionCode": "US",
        "relevanceLanguage": "en",
        "safeSearch": "none",
        "type": "video",
        "publishedAfter": formatted_date

    }

    url = "https://www.googleapis.com/youtube/v3/search"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)

    data = response.json()
    video_ids = []
    if int(data["pageInfo"]["totalResults"]) > 0:
        for item in data["items"]:
            vid_id = item["id"]["videoId"]
            if vid_id not in vids_ids:
                video_ids.append(vid_id)
                await fetch_youtube_video_info(vid_id, pool, False)
    return video_ids


async def main_s(pool, vid_ids: list[str] = []) -> list[str]:
    search_terms = [
        "vaccine kills",
        "vaccine cause autism",
        "vaccine takes life",
        "vaccine harm",
        "vaccine choice",
        "severe illness after vaccination",
        "vaccine my body, my choice",
        "vaccine pro-choice",
        "covid vaccine"
    ]

    # Subset from article https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10506664/
    master_vid_ids = []
    for s in search_terms:
        print(f"STARTING: {s}")
        file_name = s.replace(" ", "_")
        master_vid_ids.extend(await search_videos(s, file_name, pool, vid_ids))
    return master_vid_ids


async def video_search():
    pool = await asyncpg.create_pool(user='postgres', password=os.getenv("DATABASE_PASSWORD"),
                                     database='videodata', host='127.0.0.1')
    await main_s(pool, [])


if __name__ == "__main__":

    asyncio.run(video_search())
