from utilities.core import create_sessions
from utilities.telegram import Accounts
from utilities.starter import majorStart, majorStats
import asyncio
import os
import json

async def main():
    print('\nNailambe\'s MajorBot (https://github.com/NailAmber)')
    action = int(input("Select action:\n1. Start soft\n2. Print stats\n3. Create sessions\n\n> "))

    if not os.path.exists('sessions'): os.mkdir('sessions')
    if not os.path.exists('statistics'): os.mkdir('statistics')
    if not os.path.exists('sessions/accounts.json'):
        with open("sessions/accounts.json", 'w') as f:
            f.write("[]")

    if action == 3:
        await create_sessions()

    if action == 2:
        await majorStats()

    if action == 1:
        accounts = await Accounts().get_accounts()

        tasks = []
        for thread, account in enumerate(accounts):
            session_name, phone_number, proxy = account.values()
            tasks.append(asyncio.create_task(majorStart(session_name=session_name, phone_number=phone_number, thread=thread, proxy=proxy)))
           
        await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())