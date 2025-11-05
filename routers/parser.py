from fastapi import APIRouter, Depends
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
import json
from db.engine import get_db
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from config import redis
from db.handler.get import get_credentials_by_channel_id

router = APIRouter(prefix="/parser", tags=["parser"])

@router.get("/search")
async def search(query: str):
    return {"message": "Hello, World!"}

@router.get("/channel")
async def channel(channel_id: str, account_id: UUID, db: AsyncSession = Depends(get_db)):
    credentials_json = redis.get(f"credentials:{account_id}")

    if credentials_json is None:
        async with db() as session:
            credentials_json = await get_credentials_by_channel_id(account_id, session)

    credentials_dict = json.loads(credentials_json)
    credentials = Credentials.from_authorized_user_info(credentials_dict)

    youtube = build('youtube', 'v3', credentials=credentials)

    response = youtube.channels().list(
        part="id",
        id=channel_id
    ).execute()

    token = credentials.valid
    return {
        "token": token,
        "response": response
    }