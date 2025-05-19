import hashlib
import hmac
import json
import os
from operator import itemgetter
from urllib.parse import parse_qsl, parse_qs, unquote

from src.config import settings


def check_webapp_signature(init_data: str) -> bool:
    """
    Check incoming WebApp init data signature

    Source: https://core.telegram.org/bots/webapps#validating-data-received-via-the-web-app

    :param init_data:
    :return:
    """
    try:
        parsed_data = dict(parse_qsl(init_data))
    except ValueError:
        # Init data is not a valid query string
        return False
    if "hash" not in parsed_data:
        # Hash is not present in init data
        return False

    hash_ = parsed_data.pop('hash')

    data_check_string = "\n".join(
        f"{k}={v}" for k, v in sorted(parsed_data.items(), key=itemgetter(0))
    )
    secret_key = hmac.new(
        key=b"WebAppData", msg=settings.TELEGRAM_TOKEN.encode(), digestmod=hashlib.sha256
    )
    calculated_hash = hmac.new(
        key=secret_key.digest(), msg=data_check_string.encode(), digestmod=hashlib.sha256
    ).hexdigest()
    return calculated_hash == hash_

def get_user_id(init_data: str) -> int:
    parsed_data = parse_qs(init_data)
    user_json = unquote(parsed_data["user"][0])

    user_data = json.loads(user_json)
    user_id = int(user_data["id"])
    return user_id
