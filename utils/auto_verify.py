from typing import TYPE_CHECKING
from naff import Client
import requests

if TYPE_CHECKING:
    from main import Client

def autoverify(self, gamertag: str):
    url = self.bot.config.urls.players.format(gamertag)

    try: 
        r = requests.get(url)
        if r.status_code == 200:
            if r.json()[0] is None:
                raise IndexError
            else:
                if r.json()[0]['title']['rendered'] == gamertag:
                    return True 
                else:
                    return False
    except IndexError:
        return False
