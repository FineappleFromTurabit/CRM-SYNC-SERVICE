# app/redis_client.py
import redis.asyncio as redis
from app.config import REDIS_URL

redis_client = redis.from_url(REDIS_URL, decode_responses=True)

async def set_value(key: str, value: str):
    await redis_client.set(key, value)

async def get_value(key: str):
    return await redis_client.get(key)
