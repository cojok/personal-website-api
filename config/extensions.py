import os
from typing import cast
import redis

redis_client = None


def get_redis_client() -> redis.Redis:
    global redis_client
    host: str = os.getenv('REDIS_HOST', 'localhost')
    port: int = cast(int, os.getenv('REDIS_PORT', 6379))
    db: int = cast(int, os.getenv('REDIS_DB', 0))
    password: str = os.getenv('REDIS_PASSWORD', '')
    if not redis_client:
        # get credentials from environment variables
        redis_client = redis.Redis(
            host = host,
            db = db,
            port = port,
            password = password
        )
    assert redis_client.ping()  # check if connection is successful
    return redis_client
