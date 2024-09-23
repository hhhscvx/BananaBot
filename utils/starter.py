import asyncio
from random import randint, uniform

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
                await asyncio.sleep(2)

                # QUESTS:
                quests, _, _ = await banana.get_quests()
                await asyncio.sleep(1)

                for quest in quests:
                    quest_id = quest['quest_id']
                    quest_name = quest['quest_name']

                    if quest['is_achieved'] and not quest['is_claimed']:
                        claimed_quest = await banana.claim_quest(quest_id=quest_id)
                        if claimed_quest['msg'] == 'Success':
                            logger.success(
                                f"{session_name} | Claimed quest «{quest_name}» | Earned: {claimed_quest['data']['peel']} peel")
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
                    await asyncio.sleep(1.5)
                    earned_peel = await banana.claim_quest(quest_id=quest_id)
                    logger.success(
                        f"{session_name} | Completed quest «{quest_name}» | Earned: {earned_peel} peel")
                    await asyncio.sleep(1)

                while True:
                    quests, _, can_claim = await banana.get_quests()
                    await asyncio.sleep(1.7)
                    if not can_claim:
                        break
                    await banana.claim_quest_lottery()
                    logger.success(f"{session_name} | Claimed lottery by completing quests")

                # LOTTERY:
                lottery_info = await banana.get_lottery_info()
                if lottery_info['countdown_end']:
                    await banana.claim_lottery()
                    logger.success(f"{session_name} | Claimed daily lottery")
                    await asyncio.sleep(1)
                for _ in range(lottery_info['remain_lottery_count']):
                    lottery = await banana.do_lottery()
                    await asyncio.sleep(3.5)
                    logger.success(f"{session_name} | Claimed Banana in lottery: «{lottery['name']}»")

                # EQUIP BANANA:
                if config.AUTO_EQUIP_BANANA:
                    banana_list = await banana.get_banana_list()
                    await asyncio.sleep(1)
                    banana_with_max_peel = max(
                        (banana for banana in banana_list if banana["count"] > 0),
                        key=lambda b: b["daily_peel_limit"],
                    )
                    banana_id = banana_with_max_peel["banana_id"]
                    banana_name = banana_with_max_peel["name"]
                    banana_peel_limit = banana_with_max_peel["daily_peel_limit"]
                    banana_peel_price = banana_with_max_peel["sell_exchange_peel"]
                    banana_usdt_price = banana_with_max_peel["sell_exchange_usdt"]
                    equip_status = await banana.equip_banana(banana_id=banana_id)
                    await asyncio.sleep(1)
                    if equip_status == 'Success':
                        logger.success(f"{session_name} | Equiped banana «{banana_name}» | Peel limit: {banana_peel_limit} | "
                                       f"Peel price: {banana_peel_price} | USDT Price: {banana_usdt_price}")

                # AUTO CLICK
                max_click_count = (await banana.get_user_info()).max_click_count
                await asyncio.sleep(1)
                max_random_clicks = config.RANDOM_TAPS_COUNT[1] if max_click_count > 400 else max_click_count // 3
                while True:
                    taps_count = randint(config.RANDOM_TAPS_COUNT[0], max_random_clicks)
                    print('max_random_clicks:', max_random_clicks)
                    clicked = await banana.do_click(taps_count=taps_count)
                    if clicked['msg'] == 'Success':
                        logger.success(f"{session_name} | Clicked! +{clicked['data']['peel']} peel")
                    await asyncio.sleep(uniform(*config.SLEEP_BETWEEN_TAPS))
                    user_info = await banana.get_user_info()
                    if (user_info.max_click_count - user_info.today_click_count) < 50:
                        sleep_time = randint(*config.SLEEP_BY_MIN_TAPS)
                        logger.info(f"{session_name} | Sleep {sleep_time}s...")
                        await asyncio.sleep(sleep_time)

            except Exception as error:
                logger.error(f"{session_name} | Error: {error}")
                await asyncio.sleep(2)

    else:
        await banana.logout()
