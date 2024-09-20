
from aiohttp_socks import ProxyConnector
import aiohttp
from pyrogram import Client
from fake_useragent import UserAgent

from utils.core import logger
from data import config


class Banana:
    def __init__(self, tg_client: Client, proxy: str | None = None) -> None:
        self.tg_client = tg_client
        self.session_name = tg_client.name
        self.proxy = f"{config.PROXY_TYPE_REQUESTS}://{proxy}" if proxy else None
        connector = ProxyConnector.from_url(url=self.proxy) if proxy else aiohttp.TCPConnector(verify_ssl=False)

        if proxy:
            proxy = {
                "scheme": config.PROXY_TYPE_TG,
                "hostname": proxy.split(":")[1].split("@")[1],
                "port": int(proxy.split(":")[2]),
                "username": proxy.split(":")[0],
                "password": proxy.split(":")[1].split("@")[0]
            }

        headers = {"User-Agent": UserAgent(os='android').random}
        self.session = aiohttp.ClientSession(headers=headers, trust_env=True, connector=connector)
