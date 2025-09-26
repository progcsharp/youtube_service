from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from fastapi import FastAPI

from config import close_redis
from services.scheduler.scheduler_stats import collection_statistics

from routers.auth import router as auth_router
from routers.upload import router as upload_router
from routers.stats import router as stats_router
from routers.channel import router as channel_router

app = FastAPI(debug=False)
scheduler = AsyncIOScheduler()


@app.on_event("startup")
async def startup_event():
    scheduler.add_job(
        collection_statistics,
        trigger=IntervalTrigger(hours=5),
        id="video_stats_collection",
        name="Сбор статистики видео",
        replace_existing=True
    )

    scheduler.start()


@app.on_event("shutdown")
async def shutdown_event():
    """Закрытие соединения с Redis при завершении приложения"""
    await close_redis()
    print("Redis connection closed")
    # scheduler.shutdown()


app.include_router(router=auth_router)
app.include_router(router=upload_router)
app.include_router(router=stats_router)
app.include_router(router=channel_router)


