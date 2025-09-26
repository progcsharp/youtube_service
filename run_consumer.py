from consumer.consumer import consumer
from consumer.cunsumer_func.download_video import download_file
from consumer.cunsumer_func.remove_video import delete_file
from consumer.cunsumer_func.save_video import save_video_post
from consumer.cunsumer_func.upload_video import message_processing

import asyncio
from multiprocessing import Process


def run_consumer(processing_func, channel):
    asyncio.run(consumer(processing_func, channel))


def main():
    consumers_func = [
        {"processing_func": message_processing, "channel": "upload_video"},
        {"processing_func": download_file, "channel": "download_video"},
        {"processing_func": delete_file, "channel": "remove_video"},
        {"processing_func": save_video_post, "channel": "save_video"},
    ]

    processes = []
    for callback in consumers_func:
        p = Process(target=run_consumer, kwargs=callback)
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

if __name__ == "__main__":
    main()