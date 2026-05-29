from random import randint

import httpx
from redis import Redis

from database.user import User
from root.config import settings


class OTPService:
    def __init__(self):
        self.redis_client = Redis.from_url(settings.REDIS_URL)

    async def send_telegram_message(self, telegram_id: int, code: int):
        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        text = f"Sizni kodingiz {code} 🔑"
        payload = {"chat_id": telegram_id, "text": text}

        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=payload)
            if response.status_code != 200:
                raise Exception("Telegram server error")
        return response.json()

    async def send_otp(self, user: User, code: int, exp=60) -> type[bool, int]:
        key = user.phone
        ttl = self.redis_client.ttl(key)
        if ttl > 0:
            return False, ttl
        self.redis_client.set(key, code, ex=exp)
        await self.send_telegram_message(user.telegram_id, code)

        return True, ttl

    async def verify_otp(self, phone, code: int) -> bool:
        cached_code = self.redis_client.get(phone)
        if not code or cached_code is None:
            return False

        cached_code = cached_code.decode()

        return int(cached_code) == code


def generate_code() -> int:
    return randint(100000, 999999)
