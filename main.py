import argparse
import asyncio
import os
from itertools import zip_longest

from pyrogram import Client

from data import config
from utils.banana import Banana
from utils.core.file_manager import get_all_lines
from utils.core.telegram import Accounts
from utils.starter import start


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--action", type=int, help="Action to perform")

    action = parser.parse_args().action
    if not action:
        action = int(input("Select action:\n1. Start soft\n2. Create sessions\n\n> "))

    if not os.path.exists('sessions'):
        os.mkdir('sessions')

    if config.USE_PROXY_FROM_FILE:
        if not os.path.exists(config.PROXY_PATH):
            with open(config.PROXY_PATH, 'w') as f:
                f.write("")
    else:
        if not os.path.exists('sessions/accounts.json'):
            with open("sessions/accounts.json", 'w') as f:
                f.write("[]")

    if action == 2:
        await Accounts().create_sessions()

    if action == 1:
        accounts = await Accounts().get_accounts()

        tasks = []

        if config.USE_PROXY_FROM_FILE:
            proxys = get_all_lines(filepath=config.PROXY_PATH)
            for account, proxy in zip_longest(accounts, proxys):
                if not account:
                    break
                _, _, proxy = account.values()
                client = get_client_by_account(account)
                tasks.append(asyncio.create_task(start(tg_client=client, proxy=proxy)))
        else:
            for account in accounts:
                _, _, proxy = account.values()
                client = get_client_by_account(account)
                tasks.append(asyncio.create_task(start(tg_client=client, proxy=proxy)))

        await asyncio.gather(*tasks)


def get_client_by_account(account: dict) -> Client:
    session_name, _, proxy = account.values()
    
    return Client(
        name=session_name,
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        proxy=proxy,
        workdir=config.WORKDIR
    )


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
