import asyncio
import os

from pyrogram import Client

from data import config
from utils.core import logger, load_from_json, save_accounts_to_file, save_to_json


class Accounts:
    def __init__(self) -> None:
        self.workdir = config.WORKDIR
        self.api_id = config.API_ID
        self.api_hash = config.API_HASH

    @staticmethod
    def get_available_accounts(sessions: list[str]) -> list:
        accounts_from_json = load_from_json('sessions/accounts.json')

        if not accounts_from_json:
            raise ValueError("Haven`t accounts in sessions/accounts.json")

        available_accounts = []
        for session in sessions:
            for saved_account in accounts_from_json:
                if saved_account['session_name'] == session:
                    available_accounts.append(saved_account)
                    break

        return available_accounts

    def parse_sessions(self) -> list[str]:
        sessions = []
        for file in os.listdir(self.workdir):
            if file.endswith('.session'):
                sessions.append(file.replace('.session', ''))

        logger.info(f"Searched sessions: {len(sessions)}.")
        return sessions

    async def check_valid_account(self, account: dict) -> dict | None:
        session_name, _, proxy = account.values()

        try:
            proxy_dict = {
                "scheme": config.PROXY_TYPE_TG,
                "hostname": proxy.split(':')[1].split('@')[1],
                "port": int(proxy.split(':')[2]),
                "username": proxy.split(':')[0],
                "password": proxy.split(':')[1].split('@')[0],
            } if proxy else None

            client = Client(
                name=session_name,
                api_id=self.api_id,
                api_hash=self.api_hash,
                workdir=self.workdir,
                proxy=proxy_dict
            )

            connect = await asyncio.wait_for(client.connect(), timeout=config.TIMEOUT)
            if connect:
                await client.get_me()
                await client.disconnect()
                return account
            await client.disconnect()

        except Exception as err:
            raise err

    async def check_valid_accounts(self, accounts: list) -> tuple[list]:
        logger.info(f"Checking accounts for valid...")

        tasks = []
        for account in accounts:
            tasks.append(asyncio.create_task(
                self.check_valid_account(account)
            ))

        checked_accounts = await asyncio.gather(*tasks)

        valid_accounts = [account for account, is_valid in zip(accounts, checked_accounts) if is_valid]
        invalid_accounts = [account for account, is_valid in zip(accounts, checked_accounts) if not is_valid]
        logger.success(f"Valid accounts: {len(valid_accounts)}; Invalid: {len(invalid_accounts)}")

        return valid_accounts, invalid_accounts

    async def get_accounts(self) -> list[dict]:
        sessions = self.parse_sessions()
        available_accounts = self.get_available_accounts(sessions)

        if not available_accounts:
            raise ValueError("Haven`t available accounts!")
        else:
            logger.success(f"Search available accounts: {len(available_accounts)}")

        valid_accounts, invalid_accounts = await self.check_valid_accounts(available_accounts)

        if invalid_accounts:
            save_accounts_to_file(path=f"{self.workdir}invalid_accounts.txt", accounts=invalid_accounts)
            logger.info(f"Saved {len(invalid_accounts)} invalid account(s) to {self.workdir}invalid_accounts.txt")

        if not valid_accounts:
            raise ValueError("Haven`t valid sessions!")
        return valid_accounts

    async def create_sessions(self):
        while True:
            session_name = input('\nInput the name of the session (press Enter to exit): ')
            if not session_name:
                return

            proxy = input("Input the proxy in the format login:password@ip:port (press Enter to use without proxy): ")
            if proxy:
                client_proxy = {
                    "scheme": config.PROXY_TYPE_TG,
                    "hostname": proxy.split(":")[1].split("@")[1],
                    "port": int(proxy.split(":")[2]),
                    "username": proxy.split(":")[0],
                    "password": proxy.split(":")[1].split("@")[0]
                }
            else:
                proxy, client_proxy = None, None

            phone_number = (input("Input the phone number of the account: ")).replace(' ', '')
            phone_number = '+' + phone_number if not phone_number.startswith('+') else phone_number

            client = Client(
                name=session_name,
                api_id=self.api_id,
                api_hash=self.api_hash,
                workdir=self.workdir,
                phone_number=phone_number,
                proxy=client_proxy
            )

            async with client:
                me = await client.get_me()

            save_to_json(path=f"{self.workdir}accounts.json", new_data={
                "session_name": session_name,
                "phone_number": phone_number,
                "proxy": proxy
            })

            logger.success(f"Added an account {me.username} ({me.first_name} | {me.phone_number})")
