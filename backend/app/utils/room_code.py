import secrets
import string


ROOM_CODE_LENGTH = 6
ROOM_CODE_ALPHABET = string.ascii_uppercase + string.digits


def generate_room_code() -> str:
    return "".join(
        secrets.choice(ROOM_CODE_ALPHABET)
        for _ in range(ROOM_CODE_LENGTH)
    )