
import asyncio
from pprint import pprint
import random
from urllib.parse import quote, unquote

from aiohttp_socks import ProxyConnector
import aiohttp
from pyrogram import Client
from pyrogram.raw.functions.messages import RequestWebView
from pyrogram.raw.types import WebViewResultUrl
from fake_useragent import UserAgent

from utils.core import logger
from utils.core.schemas import UserInfo
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

    async def get_user_info(self) -> UserInfo:
        resp = await self.session.get(url='https://interface.carv.io/banana/get_user_info')
        resp_json = await resp.json()

        user_data = resp_json['data']

        return UserInfo(
            max_click_count=user_data['max_click_count'],
            peel_count=user_data['peel'],
            equiped_banana_peel_limit=user_data['equip_banana']['daily_peel_limit'],
            can_claim_lottery=user_data['lottery_info']['countdown_end']
        )

    async def do_click(self, taps_count: int) -> dict:
        # max_click_count = (await self.get_user_info()).max_click_count
        # max_random_clicks = config.RANDOM_TAPS_COUNT[1] if max_click_count > 400 else max_click_count // 3
        # print('max_random_clicks', max_random_clicks)
        # бля это то я в стартере должен прописывать

        resp = await self.session.post(url='https://interface.carv.io/banana/login',
                                       json={'clickCount': taps_count})
        resp_json = await resp.json()

        return resp_json

    async def get_quests(self) -> tuple[list[dict], str, bool]:
        resp = await self.session.get(url='https://interface.carv.io/banana/get_quest_list')
        resp_json = await resp.json()

        return resp_json['data']['quest_list'], resp_json['data']['progress'], resp_json['data']['is_claimed']

    async def achieve_quest(self, quest_id: int) -> bool:
        resp = await self.session.post(url='https://interface.carv.io/banana/achieve_quest',
                                       json={'quest_id': quest_id})
        resp_json = await resp.json()

        return resp_json['data']['is_achieved']

    async def claim_quest(self, quest_id: int) -> int:
        resp = await self.session.post(url='https://interface.carv.io/banana/claim_quest',
                                       json={'quest_id': quest_id})
        resp_json = await resp.json()
        pprint(resp_json)

        return resp_json['data']['peel']  # earned

    async def claim_lottery(self) -> str:
        # TODO: Сделать проверку что get_user_info.can_claim_lottery == true -> тогда делать claim
        resp = await self.session.post(url='https://interface.carv.io/banana/claim_lottery',
                                       json={'claimLotteryType': 1})
        resp_json = await resp.json()

        return resp_json['msg']  # TODO: Возвращать отсюда еще banana_info

    async def get_lottery_info(self) -> dict:
        resp = await self.session.get(url='https://interface.carv.io/banana/get_lottery_info')
        resp_json = await resp.json()

        return resp_json['data']

    async def do_lottery(self):
        """Если в get_lottery есть remain_lottery_count - запускать do_lottery"""
        try:
            resp = await self.session.post(url='https://interface.carv.io/banana/do_lottery',
                                           json={})
            resp_json = await resp.json()

            # name, sell_exchange_peel, sell_exchange_usdt, count, banana_id (чтоб надеть если че)
            return resp_json['data']
            # TODO: сделать проверку что это пизже чем выбранный банан (daily_peel_limit больше), и тогда надеть его

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when Do lottery: {error}")
            await asyncio.sleep(delay=3)

    async def claim_quest_lottery(self):
        resp = await self.session.post(url='https://interface.carv.io/banana/claim_quest_lottery',
                                       json={})
        resp_json = await resp.json()

        return resp_json

    async def equip_banana(self, banana_id: int):
        resp = await self.session.post(url='https://interface.carv.io/banana/do_equip',
                                       json={'bananaId': banana_id})
        resp_json = await resp.json()

        return resp_json

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

            return f"query_id={query_id}&user={user}&auth_date={auth_date}&hash={hash_}"
        except Exception as err:
            return
