import random
import requests
import fake_headers
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.domain.entities import Proxy


class ProxyChecker:
    def __init__(self, proxy: Proxy):
        self._proxy = f"{proxy.type.lower()}://{proxy.username}:{proxy.password}@{proxy.ip}:{proxy.port}"

    def is_alive(self) -> bool:
        try:
            session = requests.Session()
            retry = Retry(connect=3, backoff_factor=0.5)
            adapter = HTTPAdapter(max_retries=retry)
            session.mount("http://", adapter)
            session.max_redirects = 300
            session.trust_env = False

            sites = [
                "https://www.youtube.com/",
                "https://www.facebook.com/",
                "https://www.yahoo.com/",
                "https://www.whatsapp.com/",
                "https://www.xvideos.com/",
                "https://www.pornhub.com/",
                "https://www.amazon.com/",
                "https://www.xnxx.com/",
                "https://www.reddit.com/",
                "https://openai.com/",
                "https://www.office.com/",
                "https://discord.com/",
                "https://www.pinterest.com/",
            ]

            random.shuffle(sites)

            for site in sites:
                try:
                    response = session.get(
                        site,
                        proxies={"https": self._proxy},
                        timeout=(3.05, 27),
                        allow_redirects=True,
                        headers=fake_headers.Headers(os="win", headers=True).generate(),
                    )

                except Exception as loop_error:
                    print(loop_error)
                    continue

                return "40" not in str(response.status_code)

            return False

        except Exception as error:
            print(error)
            return False
