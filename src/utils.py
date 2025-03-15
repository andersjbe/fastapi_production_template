import logging
import random
import string

from passlib.context import CryptContext

logger = logging.getLogger(__name__)

ALPHA_NUM = string.ascii_letters + string.digits


def generate_random_alphanum(length: int = 20) -> str:
    return "".join(random.choices(ALPHA_NUM, k=length))


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
