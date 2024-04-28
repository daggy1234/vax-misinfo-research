import asyncpg
from redis import asyncio as aioredis
import json


async def run_video_analysis(pool: asyncpg.Pool, redis_pool: aioredis.Redis):
    async with pool.acquire() as conn:
        video_count = (await conn.fetchrow("SELECT COUNT(*) FROM videos;"))["count"]
        await redis_pool.set('video_count', video_count)
        vax_video_count = (await conn.fetchrow("SELECT COUNT(*) FROM videos WHERE vax_related=true;"))
        await redis_pool.set('vax_video_count', vax_video_count["count"])
        # video_comment_count_l =  await conn.fetch("SELECT comments.video_id, COUNT(*) FROM comments, (SELECT video_id FROM videos WHERE vax_related=true) as vax_vid WHERE comments.video_id=vax_vid.video_id GROUP BY comments.video_id;");
        # await redis_pool.set('vax_video_comments', json.dumps(video_comment_count_l))

        avg_comments_per_vid = (await conn.fetchrow("SELECT AVG(cpm_c_tab.count) FROM (SELECT comments.video_id, COUNT(*) FROM comments, (SELECT video_id FROM videos WHERE vax_related=true) as vax_vid WHERE comments.video_id=vax_vid.video_id GROUP BY comments.video_id) AS cpm_c_tab;"))
        await redis_pool.set('avg_vax_video_comments', float(avg_comments_per_vid["avg"]))
        author_frequency = (await conn.fetch("SELECT channel_id,channel_title ,count(*) FROM videos WHERE videos.vax_related=true GROUP BY channel_id, channel_title ORDER BY count DESC;"))
        proc_author_freq = [dict(row) for row in author_frequency]
        await redis_pool.set('author_frequency', json.dumps(proc_author_freq))

        title_word_freqs = await conn.fetch("""WITH normalized_words AS (
                                                SELECT unnest(regexp_split_to_array(lower(title || ' '), '\s+')) AS word
                                                FROM videos
                                            ),
                                            filtered_words AS (
                                                SELECT word
                                                FROM normalized_words
                                                WHERE word ~ '^[a-zA-Z]+$' AND length(word) > 4
                                            )
                                            SELECT word, count(*) AS frequency
                                            FROM filtered_words
                                            GROUP BY word
                                            ORDER BY frequency DESC LIMIT 500;
                                            """)
        proc_title_word_freq = [[d := dict(
            row), {"text": d["word"], "value": d["frequency"]}][1] for row in title_word_freqs]
        await redis_pool.set('title_word_frequency', json.dumps(proc_title_word_freq))
        tag_word_freqs = await conn.fetch("""WITH normalized_words AS (
                                                SELECT unnest(regexp_split_to_array(lower(tags || ' '), '\s+')) AS word
                                                FROM videos
                                            ),
                                            filtered_words AS (
                                                SELECT word
                                                FROM normalized_words
                                                WHERE word ~ '^[a-zA-Z]+$' AND length(word) > 4
                                            )
                                            SELECT word, count(*) AS frequency
                                            FROM filtered_words
                                            GROUP BY word
                                            ORDER BY frequency DESC LIMIT 500;
                                            """)
        proc_tag_word_freq = [[d := dict(
            row), {"text": d["word"], "value": d["frequency"]}][1] for row in tag_word_freqs]
        await redis_pool.set('tag_word_frequency', json.dumps(proc_tag_word_freq))
        comment_count = (await conn.fetchrow("SELECT COUNT(*) FROM comments;"))["count"]
        await redis_pool.set('comment_count', comment_count)
        comment_length = float((await conn.fetchrow("SELECT AVG(length(text)) FROM comments WHERE is_reply=false;"))["avg"])
        await redis_pool.set('avg_top_comment_length', comment_length)
        avg_child_comments = float((await conn.fetchrow("SELECT avg(cc.count) FROM (SELECT count(*) FROM comments WHERE is_reply=true GROUP BY parent_id) as cc;"))["avg"])
        await redis_pool.set('avg_child_comments', avg_child_comments)
        comment_author_freq = await conn.fetch("""
                                                    SELECT
                                                        author_id,
                                                        author_name,
                                                        author_image,
                                                        COUNT(*)
                                                    FROM
                                                        comments
                                                    GROUP BY
                                                        author_id, author_name, author_image
                                                    HAVING
                                                        COUNT(*) > 1
                                                    ORDER BY
                                                        count DESC LIMIT 100;
                                                    """)
        proc_com_author_freq = [dict(row) for row in comment_author_freq]
        await redis_pool.set('comment_author_frequency', json.dumps(proc_com_author_freq))
        comment_freq_analysis = await conn.fetch("""
                                                 WITH normalized_words AS (
                                                    SELECT unnest(regexp_split_to_array(lower(text || ' '), '\s+')) AS word
                                                    FROM comments
                                                ),
                                                filtered_words AS (
                                                    SELECT word
                                                    FROM normalized_words
                                                    WHERE word ~ '^[a-zA-Z]+$' AND length(word) > 4 -- This filters out any strings that aren't purely alphabetical (ignoring numbers and punctuation)
                                                )
                                                SELECT word, count(*) AS frequency
                                                FROM filtered_words
                                                GROUP BY word
                                                ORDER BY frequency DESC LIMIT 500;
                                                """)

        comm_word_freq_a = [[d := dict(
            row), {"text": d["word"], "value": d["frequency"]}][1] for row in comment_freq_analysis]
        await redis_pool.set('comment_word_freqs', json.dumps(comm_word_freq_a))
        # SELECT comment_id,comments.video_id, text, length(text) AS text_length FROM comments, (SELECT video_id FROm videos WHERE vax_related=true) as vid_ids WHERE comments.video_id=vid_ids.video_id AND comments.is_reply=false ORDER by text_length DESC LIMIT 1000;
