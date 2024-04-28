import httpx
import asyncio
import asyncpg
from datetime import datetime
import os

YOUTUBE_API_KEY = os.getenv("YOUTUBE_KEY_B")
YOUTUBE_API_URL = "https://www.googleapis.com/youtube/v3"


def com_to_tup(data, is_reply: bool, video_id: str, parent_id: str = "") -> tuple:
    try:
        published_at = datetime.fromisoformat(data["snippet"]["publishedAt"])
        published_at = published_at.replace(tzinfo=None)
        updated_at = datetime.fromisoformat(data["snippet"]["updatedAt"])
        updated_at = updated_at.replace(tzinfo=None)
    except:
        try:
            published_at = datetime.strptime(
                data["snippet"]["publishedAt"], "%Y-%m-%dT%H:%M:%SZ")
            published_at = published_at.replace(tzinfo=None)
            updated_at = datetime.strptime(
                data["snippet"]["updatedAt"], "%Y-%m-%dT%H:%M:%SZ")
            updated_at = updated_at.replace(tzinfo=None)
        except:
            published_at = datetime.fromtimestamp(0)
            published_at = published_at.replace(tzinfo=None)
            updated_at = datetime.now()
            updated_at = updated_at.replace(tzinfo=None)

    parsed_data = (
        data["id"],
        video_id,
        data["snippet"]["authorDisplayName"],
        data["snippet"]["authorProfileImageUrl"],
        data["snippet"]["authorChannelId"]["value"],
        data["snippet"]["textOriginal"],
        published_at,
        updated_at,
        is_reply,
        parent_id,
    )
    return parsed_data


async def fetch_recent_comment_threads(video_id: str, pool: asyncpg.Pool):
    url = f"{YOUTUBE_API_URL}/commentThreads?part=snippet,replies&videoId={
        video_id}&key={YOUTUBE_API_KEY}&maxResults=100"
    all_comments = []
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        data = response.json()
        resp = data.get('items', [])
        if resp:
            print("GOT RESP")
            comment_data = []
            for item in resp:
                top_comment = item["snippet"]["topLevelComment"]
                top_comment_id = top_comment["id"]
                comment_data.append(com_to_tup(top_comment, False, video_id))
                reply_c = item["snippet"]["totalReplyCount"]
                replies = []
                if reply_c > 1:
                    try:
                        for c in item["replies"]["comments"]:
                            comment_data.append(com_to_tup(
                                c, True, video_id, parent_id=top_comment_id))
                    except KeyError:
                        pass
            # Assuming you have a connection pool named 'pool'
            async with pool.acquire() as connection:
                for comment in comment_data:
                    await connection.execute('''
                        INSERT INTO comments (comment_id, video_id, author_name, author_image, author_id, text, published_at, updated_at, is_reply, parent_id)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                        ON CONFLICT DO NOTHING;
                    ''', *comment)
    return all_comments


async def fetch_all_comment_threads(video_id: str, pool: asyncpg.Pool):
    url = f"{YOUTUBE_API_URL}/commentThreads?part=snippet,replies&videoId={
        video_id}&key={YOUTUBE_API_KEY}&maxResults=100"
    all_comments = []
    nextPageToken = None

    async with httpx.AsyncClient() as client:
        while True:
            if nextPageToken:
                response = await client.get(f"{url}&pageToken={nextPageToken}")
            else:
                response = await client.get(url)

            data = response.json()
            print(data)
            resp = data.get('items', [])
            if resp:
                print("GOT RESP")
                comment_data = []
                for item in resp:
                    top_comment = item["snippet"]["topLevelComment"]
                    top_comment_id = top_comment["id"]
                    comment_data.append(com_to_tup(
                        top_comment, False, video_id))
                    reply_c = item["snippet"]["totalReplyCount"]
                    replies = []
                    if reply_c > 1:
                        try:
                            for c in item["replies"]["comments"]:
                                comment_data.append(com_to_tup(
                                    c, True, video_id, parent_id=top_comment_id))
                        except KeyError:
                            pass
                # Assuming you have a connection pool named 'pool'
                async with pool.acquire() as connection:
                    for comment in comment_data:
                        await connection.execute('''
                            INSERT INTO comments (comment_id, video_id, author_name, author_image, author_id, text, published_at, updated_at, is_reply, parent_id)
                            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                            ON CONFLICT DO NOTHING;
                        ''', *comment)

            nextPageToken = data.get('nextPageToken')
            if not nextPageToken:
                break

    return all_comments


async def main():
    pool = await asyncpg.create_pool(user='postgres', password=os.getenv("DATABASE_PASSWORD"),
                                     database='videodata', host='127.0.0.1')
    async with pool.acquire() as connection:
        vids = await connection.fetch("SELECT * FROM videos WHERE manual=false")
        for video in vids:
            vi = video["video_id"]
            print(vi)
            # await fetch_all_comment_threads(vi, pool)
            await fetch_all_comment_threads(vi, pool)

    # with open("video_ids.txt", "r")  as file:
    #     lines = file.readlines()
    #     for line in lines:
    #         await fetch_all_comment_threads(line.strip(), pool)

if __name__ == "__main__":
    asyncio.run(main())
