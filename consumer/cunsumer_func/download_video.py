import datetime
import json

import aiohttp
import aiofiles
import os

from redis import StrictRedis


async def download_file(data):
    data = json.loads(data)
    download_dir = "videos"

    redis_broker = StrictRedis(host="localhost", port=6379, db=0, decode_responses=True)

    for download_data in data:
        list_url = download_data['urls']
        user_id = download_data["user_id"]
        for i, url in enumerate(list_url):
            filename = f"video_{i}_{user_id}_{str(datetime.datetime.now().timestamp())}.mp4"
            filepath = os.path.join(download_dir, filename)

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        async with aiofiles.open(filepath, 'wb') as f:
                            async for chunk in response.content.iter_chunked(1024 * 1024):  # 1MB chunks
                                await f.write(chunk)
                        download_data["video_data"]["file_path"] = filepath
                        redis_broker.publish("upload_video", json.dumps(download_data))
                        return filepath
                    else:
                        raise Exception(f"HTTP error: {response.status}")
