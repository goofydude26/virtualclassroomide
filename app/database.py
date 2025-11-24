import os
from motor.motor_asyncio import AsyncIOMotorClient

import certifi

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGO_URL, tlsCAFile=certifi.where())
db = client.virtual_classroom

async def get_database():
    return db
