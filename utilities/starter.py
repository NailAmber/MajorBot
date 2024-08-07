from utilities.major import MajorBot
from asyncio import sleep
from random import uniform
from data import config
from utilities.core import logger
import asyncio
from aiohttp.client_exceptions import ContentTypeError
from utilities.telegram import Accounts
import datetime
import pandas as pd
import os

async def majorStart(thread: int, session_name: str, phone_number: str, proxy: [str, None]):
    major = await MajorBot.create(session_name=session_name, phone_number=phone_number, thread=thread, proxy=proxy)
    account = session_name + '.session'

    await sleep(uniform(config.DELAYS['ACCOUNT'][0], config.DELAYS['ACCOUNT'][1]))

    while True:
        try:
            
            await major.login()

            await sleep(30)

        except ContentTypeError as e:
            logger.error(f"Major | Thread {thread} | {account} | Error: {e}")
            await asyncio.sleep(120)

        except Exception as e:
            logger.error(f"Major | Thread {thread} | {account} | Error: {e}")


async def majorStats():
    accounts = await Accounts().get_accounts()
    tasks = []
    for thread, account in enumerate(accounts):
        session_name, phone_number, proxy = account.values()
        # Создаем экземпляр Major, используя метод create
        major_instance = await MajorBot.create(thread=thread, session_name=session_name, phone_number=phone_number, proxy=proxy)
        # Добавляем задачу вызова stats() для созданного экземпляра
        tasks.append(asyncio.create_task(major_instance.stats()))
    
    data = await asyncio.gather(*tasks)
    path = f"statistics/statistics_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.csv"
    columns = ['Phone number', 'Name', 'Rating', 'Position', 'Proxy (login:password@ip:port)']
    if not os.path.exists('statistics'): os.mkdir('statistics')
    df = pd.DataFrame(data, columns=columns)
    df.to_csv(path, index=False, encoding='utf-8-sig')
    logger.success(f"Saved statistics to {path}")