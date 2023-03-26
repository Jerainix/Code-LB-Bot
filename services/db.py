from datetime import datetime
from os import environ
from typing import Union

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()


class DB:
    def __init__(self) -> None:
        self.client = AsyncIOMotorClient(environ['DB-LINK'])
        self.db = self.client['randprog']

    async def add_user(self, user_id: int, choice: str, skills=None) -> None:
        if skills is None:
            skills = []
        await self.db.users.insert_one({'_id': user_id, 'choice': choice, 'skills': skills,
                                        'date': str(datetime.now().date())})

    async def find_user(self, user_id: int, key_data: str = None) -> Union[dict, None, str, int, list]:
        data = await self.db.users.find_one({'_id': user_id})

        if key_data is not None and data is not None:
            data = data[key_data]
        return data

    async def add_user_to_queue(self, user_id: int, choice: str, skills: list) -> None:
        await self.db.queue.insert_one({'_id': user_id, 'choice': choice, 'skills': skills})

    async def find_queue(self, user_id: int) -> Union[dict, None]:
        return await self.db.queue.find_one({'_id': user_id})

    async def new_chat(self, user1: int, user2: int):
        await self.db.chats.insert_one({'_id': f'{user1}{user2}', 'users': [user1, user2]})

    async def find_companion(self, user_id: int, choice: str, skills: list) -> bool:
        companion = await self.db.queue.find_one(
            {'_id': {'$ne': user_id}, 'choice': {'$ne': choice}, 'skills': {'$in': skills}})
        user_in_queue = await self.find_queue(user_id)

        if companion is None and user_in_queue is None:
            await self.add_user_to_queue(user_id, choice, skills)
            return False
        else:
            await self.db.queue.delete_one(companion)
            await self.new_chat(user_id, companion['_id'])
            return True

    async def find_chat(self, user_id: int) -> Union[dict, None]:
        result = await self.db.chats.find_one({'users': {'$in': [user_id]}})
        return result

    async def other(self, key: str, key_data: str = None) -> Union[dict, None, str, int, list]:
        data = await self.db.other.find_one({'_id': key})

        if key_data is not None:
            data = data[key_data]
        return data
