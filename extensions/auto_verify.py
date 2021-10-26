from extensions import default
import requests
import motor.motor_asyncio as motor
import re

config = default.config()


def verify(name):
    default_url = config['urls']['players']

    if bool(re.search(r"\s", name)):
        lookup_tag = name.replace(" ", "-")
    else:
        lookup_tag = name

    try:
        url = default_url.format(lookup_tag)
        player_page = requests.get(url)
        try:
            player_page.json()[0]['id'] is None
        except IndexError:
            return False
        else:
            return True
    except requests.exceptions.ConnectionError:
        return False

