import random
import string

import redis
from django.conf import settings

r = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)


def generate_verification_code() -> str:
    """Generate a random 6-digit code

    Returns:
        str: a 6-digit code in string format .e.g '654874'
    """
    return "".join(random.choices(string.digits + string.digits, k=6))


def set_verification_code(email: str, code: str) -> None:
    """Set a key and value in Redis

    Args:
        email (str): The key that will be used to save code in Redis
        code (str): A random 6-digit string
    """
    r.set(email, code, ex=settings.VERIFICATION_CODE_EXPIRY)


def is_code_in_redis(email: str) -> bool:
    """Check redis with `email` key .e.g `test@example.com`
    return True if any code is associated with the email

    Args:
        email (str): user provided email

    Returns:
        bool: whether there is a code in Redis or not
    """
    code = r.get(email)
    return code != None


def is_code_correct(email: str, user_provided_code: str) -> bool:
    """Get the code from Redis using `email` as key

    Args:
        email (str): Email will be used as a key to get data from Redis
        user_provided_code (str): The code that user sends to API

    Returns:
        bool: if the code in Redis is equal to user provided code then return True
    """
    code_in_db = r.get(email).decode()
    return str(user_provided_code) == code_in_db
