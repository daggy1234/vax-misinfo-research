CREATE TABLE videos (
    id  SERIAL PRIMARY KEY,
    video_id VARCHAR(255) UNIQUE NOT NULL,
    channel_id VARCHAR(255),
    channel_id TEXT,
    description TEXT,
    channel_title TEXT,
    thumbnail_url TEXT,
    published_at TIMESTAMP,
    tags TEXT,
    topics TEXT
    manual BOOLEAN,
);

ALTER TABLE videos ADD COLUMN vax_related BOOLEAN DEFAULT FALSE;

CREATE TABLE comments (
    id  SERIAL PRIMARY KEY,
    video_id VARCHAR(255),
    author_name TEXT,
    author_image TEXT,
    author_id VARCHAR(255),
    comment_id VARCHAR(255) UNIQUE NOT NULL,
    text TEXT,
    published_at TIMESTAMP,
    updated_at TIMESTAMP,
    is_reply BOOLEAN,
    parent_id VARCHAR(255) DEFAULT NULL,
    FOREIGN KEY(video_id) REFERENCES videos(video_id)
);


SELECT video_id,title,published_at,manual FROM videos WHERE processed=true and vax_related=true ORDER BY published_at DESC;

SELECT * FROM videos WHERE vax_related=false and manual=true;