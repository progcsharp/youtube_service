import json
from datetime import datetime

from db import make_session
from db.handler.create import create_post


async def save_video_post(video_data):

    data = json.loads(video_data)
    # data["published_at"] = datetime.fromisoformat(data["published_at"].replace('Z', '+00:00')).isoformat()
    session = make_session()
    await create_post(data, session)
    await session.close()
    