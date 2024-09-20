
import asyncio
import random
from urllib.parse import quote, unquote

from aiohttp_socks import ProxyConnector
import aiohttp
from pyrogram import Client
from pyrogram.raw.functions.messages import RequestWebView
from pyrogram.raw.types import WebViewResultUrl
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

    async def logout(self) -> None:
        await self.session.close()

    async def login(self) -> bool:
        await asyncio.sleep(random.uniform(*config.DELAY_CONN_ACCOUNT))
        query = await self.get_tg_web_data()

        if query is None:
            logger.error(f"{self.session_name} | Session {self.session_name}.session invalid")
            await self.logout()
            return

        resp = await self.session.post(url='https://interface.carv.io/banana/login',
                                       json={'tgInfo': query})
        resp_json = await resp.json()

        self.session.headers["Authorization"] = resp_json['data']['token']
        return True

    async def get_tg_web_data(self):
        try:
            await self.tg_client.connect()
            await self.tg_client.send_message('OfficialBananaBot', '/start')
            await asyncio.sleep(random.uniform(1.5, 2))

            web_view: WebViewResultUrl = await self.tg_client.invoke(RequestWebView(
                peer=await self.tg_client.resolve_peer('OfficialBananaBot'),
                bot=await self.tg_client.resolve_peer('OfficialBananaBot'),
                platform="android",
                from_bot_menu=False,
                url="https://banana.carv.io/"
            ))
            await self.tg_client.disconnect()
            auth_url = web_view.url

            query = unquote(string=unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0]))
            query_id = query.split('query_id=')[1].split('&user=')[0]
            user = quote(query.split("&user=")[1].split('&auth_date=')[0])
            auth_date = query.split('&auth_date=')[1].split('&hash=')[0]
            hash_ = query.split('&hash=')[1]

            print(f"query_id={query_id}&user={user}&auth_date={auth_date}&hash={hash_}")

            return f"query_id={query_id}&user={user}&auth_date={auth_date}&hash={hash_}"
        except Exception as err:
            return
