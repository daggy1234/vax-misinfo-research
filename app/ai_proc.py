import asyncpg
import openai
import asyncio
import os

openai.api_key = os.getenv("OPENAI_KEY")


async def fetch_and_classify_videos(pool: asyncpg.Pool):
    rows = None
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM videos WHERE processed=false;")
        for row in rows:
            print(dict(row))
            result = await asyncio.get_event_loop().run_in_executor(None, process_video, row['title'], row["description"], row["tags"])
            print(result)
            await conn.execute("UPDATE videos SET processed=true, vax_related=$1 WHERE id=$2", result, row["id"])
            print("DONE")


def process_video(video_title: str, video_description: str, tags: str) -> bool:
    MODEL = "gpt-4-1106-preview"
    TEMP = 0.0
    MAX_TOKENS = 1
    PROMPT = f"You will be given a video title and tags. Please return whether the text is relevant to my research. It is related to my research if it mentions vaccines in some way and vaccination in reference to humans, indirectly or directly. Note that the sentences may be vaccine relevant even if there aren't any keywords like \"vaccine\" or \"vaccination\". Think carefully about your answer as this task is important, then return a 'Y' or 'N' indicating if the video data is relevant to my research. \n Title: {
        video_title}\nTags: {tags}"
    message = [{"role": "user", "content": PROMPT}]
    resp = openai.chat.completions.create(
        model=MODEL,
        messages=message,
        temperature=TEMP,
        max_tokens=MAX_TOKENS
    )
    f_resp = resp.choices[0].message.content
    return f_resp == "Y"


async def main():
    pool = await asyncpg.create_pool(user='postgres', password='ARnav123#',
                                     database='videodata', host='127.0.0.1')
    await fetch_and_classify_videos(pool)

if __name__ == "__main__":
    asyncio.run(main())
