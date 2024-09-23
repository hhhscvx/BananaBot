import asyncio

from pyrogram import Client

from utils.banana import Banana
from utils.core import logger
from data import config


async def start(tg_client: Client, proxy: str | None = None):
    banana = Banana(tg_client=tg_client, proxy=proxy)
    session_name = tg_client.name + '.session'

    if await banana.login():
        while True:
            try:
                user_info = await banana.get_user_info()
                logger.success(f"{session_name} | Successfully connected! | "
                               f"Peels: {user_info.peel_count} | Max click count: {user_info.max_click_count}")

                # QUESTS:
                quests, _, _ = await banana.get_quests()

                for quest in quests:
                    quest_id = quest['quest_id']
                    quest_name = quest['quest_name']

                    if quest['is_achieved'] and not quest['is_claimed']:
                        earned_peel = await banana.claim_quest(quest_id=quest_id)
                        logger.success(
                            f"{session_name} | Claimed quest «{quest_name}» | Earned: {earned_peel} peel")
                        await asyncio.sleep(1)
                        continue

                    if quest['quest_name'] in config.BLACKLIST_QUESTS:
                        logger.info(f"{session_name} | Skipped Blacklist quest «{quest_name}»")
                        continue
                    try:
                        if quest['args']['Verify'] is True:
                            logger.info(f"{session_name} | Skipped Verify quest «{quest_name}»")
                            continue
                    except:
                        pass
                    if quest['is_claimed']:
                        logger.info(f"{session_name} | Skipped is_claimed quest «{quest_name}»")
                        continue

                    await banana.achieve_quest(quest_id=quest_id)
                    await asyncio.sleep(1)
                    earned_peel = await banana.claim_quest(quest_id=quest_id)
                    logger.success(
                        f"{session_name} | Completed quest «{quest_name}» | Earned: {earned_peel} peel")
                    await asyncio.sleep(0.5)

                while True:
                    quests, _, can_claim = await banana.get_quests()
                    if not can_claim:
                        break
                    await banana.claim_quest_lottery()
                    logger.success(f"{session_name} | Claimed lottery by completing quests")

                # LOTTERY:
                lottery_info = await banana.get_lottery_info()
                if lottery_info['countdown_end']:
                    await banana.claim_lottery()
                    logger.success(f"{session_name} | Claimed daily lottery")
                for _ in range(lottery_info['remain_lottery_count']):
                    lottery = await banana.do_lottery()
                    logger.success(f"{session_name} | Claimed Banana in lottery: «{lottery['name']}»")

            except Exception as error:
                logger.error(f"{session_name} | Error: {error}")
                await asyncio.sleep(2)
                raise error

    else:
        await banana.logout()
