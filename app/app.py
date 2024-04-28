from fastapi import FastAPI, Depends, BackgroundTasks
from starlette.requests import Request
import asyncpg
import json
from redis import asyncio as aioredis
import os
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from .video_search import main_s
from .comment_proc import fetch_all_comment_threads, fetch_recent_comment_threads
from .ai_proc import fetch_and_classify_videos
from fastapi.middleware.cors import CORSMiddleware
from .metrics import run_video_analysis
from typing import TypedDict


class StateDict(TypedDict):
    pool: asyncpg.Pool
    redis: aioredis.Redis
    scheduler: AsyncIOScheduler


state: StateDict = {}

DATABASE_URL = os.getenv("DATABASE_URL")


async def tick():
    print("SEX ME BB")


async def video_daily_search():
    print("START CRON")
    video_ids = []
    async with state["pool"].acquire() as con:
        videos = await con.fetch('SELECT video_id FROM videos')
        video_ids = [video['video_id'] for video in videos]
    print(video_ids)
    vid_ids = await main_s(state["pool"], video_ids)
    for video in vid_ids:
        if videos not in video_ids:
            await fetch_all_comment_threads(video, state["pool"])


async def comment_cacher():
    print("CACHING COMMENTS")
    video_ids = []
    async with state["pool"].acquire() as con:
        videos = await con.fetch('SELECT video_id FROM videos WHERE vax_related=true;')
        video_ids = [video['video_id'] for video in videos]
    for video in video_ids:
        await fetch_recent_comment_threads(video, state["pool"])

    # video_ids = [video['video_id'] for video in videos]


async def ai_classify():
    await fetch_and_classify_videos(state["pool"])


async def video_analysis():
    await run_video_analysis(state["pool"], state["redis"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(os.getenv("POSTGRES_PASSWORD"))
    state["pool"] = await asyncpg.create_pool(
        user='postgres',
        password=os.getenv("DATABASE_PASSWORD"),
        database='videodata',
        host=os.getenv("DATABSE_HOST", "0.0.0.0")
    )
    state["redis"] = await aioredis.from_url(f'redis://{os.getenv("REDIS_HOST", "0.0.0.0")}:6379')
    # await video_daily_search()
    # await ai_classify()
    await run_video_analysis(state["pool"], state["redis"])
    # await asyncio.get_event_loop().create_task(video_daily_search())
    state["scheduler"] = AsyncIOScheduler()
    state["scheduler"].add_job(video_daily_search, 'interval', hours=24)
    state["scheduler"].add_job(ai_classify, 'interval', hours=12)
    state["scheduler"].add_job(comment_cacher, 'interval', hours=3)
    state["scheduler"].add_job(video_analysis, 'interval', hours=1)
    state["scheduler"].start()
    yield
    state["scheduler"].shutdown()
    state["redis"].close()
    await state["pool"].close()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": f"Hello World"}


@app.get("/videos")
async def video_get():
    conn = await state["pool"].acquire()
    try:
        videos = await conn.fetch('SELECT * FROM videos')
        comment_counts = await conn.fetch("SELECT video_id,COUNT(*) FROM comments GROUP BY video_id;")
    finally:
        await state["pool"].release(conn)

    return {"data": videos}


@app.get("/vax-videos")
async def video_get(desc_sort: bool = True):
    videos = []
    async with state["pool"].acquire() as conn:
        sort_key = "desc" if desc_sort else "asc"
        # videos = await conn.fetch('SELECT * FROM videos, (SELECT video_id, COUNT(*) FROM comments GROUP BY video_id) AS comm_c WHERE vax_related=true AND comm_c.video_id = videos.video_id order by published_at desc;')
        videos = await conn.fetch(f'SELECT * FROM videos, (SELECT video_id, COUNT(*) FROM comments GROUP BY video_id) AS comm_c WHERE vax_related=true AND comm_c.video_id = videos.video_id order by published_at {sort_key};')
    return {"data": videos}


@app.get("/fetch-video")
async def spec_vid_data(video_id: str):
    conn = await state["pool"].acquire()
    try:
        videos = await conn.fetchrow('SELECT * FROM videos WHERE video_id=$1', video_id)
        print(videos)
    finally:
        await state["pool"].release(conn)
    return {"data": videos}


@app.get("/top-comments")
async def video_top_comments(video_id: str):
    conn = await state["pool"].acquire()
    try:
        comments = await conn.fetch('SELECT * FROM comments WHERE video_id=$1 AND is_reply=false', video_id)
    finally:
        await state["pool"].release(conn)
    return {"data": comments}


@app.get("/fetch-comments")
async def video_fetch_comments(video_id: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(
        fetch_all_comment_threads, video_id, state["pool"])
    return {"data": True}


@app.get("/video-metrics")
async def video_fetch_comments():
    to_ret = {}
    to_ret["video_count"] = int(await state["redis"].get("video_count"))
    to_ret["vax_video_count"] = int(await state["redis"].get("vax_video_count"))
    to_ret["avg_vax_video_comments"] = float(await state["redis"].get("avg_vax_video_comments"))
    to_ret["author_frequency"] = json.loads(await state["redis"].get("author_frequency"))
    to_ret["title_word_frequency"] = json.loads(await state["redis"].get("title_word_frequency"))
    to_ret["tag_word_frequency"] = json.loads(await state["redis"].get("tag_word_frequency"))
    to_ret["comment_count"] = int(await state["redis"].get("comment_count"))
    to_ret["avg_top_comment_length"] = float(await state["redis"].get("avg_top_comment_length"))
    to_ret["avg_child_comments"] = float(await state["redis"].get("avg_child_comments"))
    to_ret["comment_author_frequency"] = json.loads(await state["redis"].get("comment_author_frequency"))
    to_ret["comment_word_frequency"] = json.loads(await state["redis"].get("comment_word_freqs"))
    return to_ret
