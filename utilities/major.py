from utilities.core import logger
from pyrogram import Client, raw 
from urllib.parse import unquote, quote
import asyncio
from fake_useragent import UserAgent
from random import uniform
from data import config
from pyrogram.raw.functions.messages import RequestAppWebView
from pyrogram.raw.types import InputBotAppShortName
import json
import os
import httpx
import time
from pyrogram.raw.functions.messages import RequestWebView

class MajorBot:
    def __init__(self, thread: int, session_name: str, phone_number: str, proxy: [str, None]):
        self.account = session_name + '.session'
        self.thread = thread
        self.proxy = f"{config.PROXY_TYPES['REQUESTS']}://{proxy}" if proxy is not None else None
        self.user_agent_file = "./sessions/user_agents.json"
        self.statistics_file = "./statistics/stats.json"
        self.ref_link_file = "./sessions/ref_links.json"
        self.major_refs = './sessions/major_refs.json'
        

        if proxy:
            proxy = {
                "scheme": config.PROXY_TYPES['TG'],
                "hostname": proxy.split(":")[1].split("@")[1],
                "port": int(proxy.split(":")[2]),
                "username": proxy.split(":")[0],
                "password": proxy.split(":")[1].split("@")[0]
            }

        with open("./data/api_config.json", "r") as f:
            apis = json.load(f)
            phone_number = apis[phone_number]
            api_id = phone_number[0]
            api_hash = phone_number[1]


        self.client = Client(
            name=session_name,
            api_id=api_id,
            api_hash=api_hash,
            workdir=config.WORKDIR,
            proxy=proxy,
            lang_code="ru"
        )

    async def init_async(self, proxy):
        # self.refferal_link = await self.get_ref_link()
        user_agent = await self.get_user_agent()
        headers = {'User-Agent': user_agent}
        self.session = httpx.AsyncClient(headers=headers)
        self.initialized = True


    @classmethod
    async def create(cls, thread: int, session_name: str, phone_number: str, proxy: [str, None]):
        instance = cls(session_name=session_name, phone_number=phone_number, thread=thread, proxy=proxy)
        await instance.init_async(proxy)
        return instance


    async def referrals_check(self, ref_number):
            if self.refferal_link is None:
                ref_links = await self.load_ref_links()
                if self.account not in ref_links:
                    ref_links[self.account] = {"Major": ref_number}
                else:
                    Major_ref = ref_links[self.account] 
                    Major_ref["Major"] = ref_number
                await self.save_ref_links(ref_links)


    async def get_user_agent(self):
        user_agents = await self.load_user_agents()
        if self.account in user_agents:
            return user_agents[self.account]
        else:
            new_user_agent = UserAgent(os='ios').random
            user_agents[self.account] = new_user_agent
            await self.save_user_agents(user_agents)
            return new_user_agent
        

    async def load_user_agents(self):
        if os.path.exists(self.user_agent_file):
            with open(self.user_agent_file, "r") as f:
                return json.load(f)
        else:
            return {}
        

    async def save_user_agents(self, user_agents):
        os.makedirs(os.path.dirname(self.user_agent_file), exist_ok=True)
        with open(self.user_agent_file, "w") as f:
            json.dump(user_agents, f, indent=4)

    async def load_major_refs(self):
        if os.path.exists(self.major_refs):
            with open(self.major_refs, 'r') as f:
                return json.load(f)
        else:
            return {}
        
    async def save_major_refs(self, major_refs):
        os.makedirs(os.path.dirname(self.major_refs), exist_ok=True)
        with open(self.major_refs, 'w') as f:
            json.dump(major_refs, f, indent=4)

    async def get_stats(self, query):
        resp = await self.session.get("https://api.altooshka.io/user/", params=query)
        resp_json = await resp.json()
        logger.info(f"Major | Thread {self.thread} | {self.account} | Balance: {resp_json["data"]["user"]["gems"]}")
        stats = await self.load_stats()
        
        balance = resp_json["data"]["user"]["gems"]
        if self.account not in stats:
            stats[self.account] = {"Altooshka":balance}
        elif "Altooshka" not in stats[self.account]:
            stats[self.account]["Altooshka"] = balance
        else:
            stats[self.account]["Altooshka"] = balance
        await self.save_stats(stats)
        

    async def load_stats(self):
        if os.path.exists(self.statistics_file):
            with open(self.statistics_file, "r") as f:
                return json.load(f)
        else:
            return {}


    async def save_stats(self, stats):
        os.makedirs(os.path.dirname(self.statistics_file), exist_ok=True)
        with open(self.statistics_file, "w") as f:
            json.dump(stats, f, indent=4)


    async def make_cd_holder_task(self):
        await self.client.connect()
        web_view = await self.client.invoke(RequestWebView(
                peer=await self.client.resolve_peer('cityholder'),
                bot=await self.client.resolve_peer('cityholder'),
                platform='ios',
                from_bot_menu=False,
                url='https://t.me/cityholder/app'
            ))
        await self.client.disconnect()

        auth_url = web_view.url
        query = unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0])
        
        json_data = {
            'auth': f'{query}'
        }
        # print('holder query ', query)
        resp = await self.session.post('https://gp.city-holder.com/', json=json_data)
        resp_json = resp.json()
        # print('resp_json ', resp_json)

    async def make_task(self, resp_json, headers):
        for task in resp_json:
            if 'https://t.me/' in task['payload']['url'] and not 'boost' in task['payload']['url']:

                if 'startapp' in task['payload']['url']:
                    bot_username = task['payload']['url'].split('/')[3]
                    start_param = task['payload']['url'].split('/')[4].split('=')[1]

                    await self.client.connect()
                    try:
                        result = await self.client.invoke(
                            raw.functions.messages.StartBot(
                                bot=await self.client.resolve_peer(bot_username),
                                peer=await self.client.resolve_peer(bot_username),
                                random_id=int(time.time() * 1000),
                                start_param=start_param
                            )
                        )
                    except Exception as e:
                        print("e = ", e)   
                    await self.client.disconnect() 

                    if 'cityholder' in task['payload']['url']:
                        await self.make_cd_holder_task()
                else:
                    await self.client.connect()
                    try:
                        if '+' in task['payload']['url']:
                            await self.client.join_chat(task['payload']['url'])
                        else:
                            await self.client.join_chat(task['payload']['url'].split('/')[3])
                    except Exception as e:
                        print("e = ", e)
                    await self.client.disconnect()
                    
                await asyncio.sleep(1)
            # print('task =', task)
            json_data = {
                'task_id': task['id']
            }
            resp = await self.session.post('https://major.glados.app/api/tasks/', json=json_data, headers=headers)
            resp_json = resp.json()
            logger.info(f"Major | Thread {self.thread} | {self.account} | Try task {resp_json['task_id']}")
            await asyncio.sleep(2)

    async def login(self):
        query = await self.get_tg_web_data()
        headers = {
        'Host': 'major.glados.app',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'Sec-Ch-Ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        'Sec-Ch-Ua-Mobile': '0',
        'Sec-Ch-Ua-Platform': '"Android"',
        'Upgrade-Insecure-Requests': '0',
        'Sec-Fetch-User': '0',
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'Origin': 'https://major.glados.app',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Priority': 'u=1, i'
        }
        json_data = {
            'init_data': query
        }
        # print(f'query {self.account} :', query)
        await asyncio.sleep(2)
        resp = await self.session.post('https://major.glados.app/api/auth/tg/', json=json_data, headers=headers)
        resp_json = resp.json()
        user_id = ''
        if 'user' in resp_json and 'id' in resp_json['user']:
            user_id = resp_json['user']['id']
        logger.info(f"Major | Thread {self.thread} | {self.account} | Auth in app, code {resp.status_code}")
        self.session.headers.pop('Authorization', None)
        self.session.headers['Authorization'] = "Bearer " + resp_json.get("access_token")

        resp = await self.session.post('https://major.glados.app/api/user-visits/visit/?', headers=headers)
        resp_json = resp.json()
        await asyncio.sleep(3)

        resp = await self.session.get("https://major.glados.app/api/tasks/?is_daily=true", headers=headers)
        resp_json_daily = resp.json()
        logger.info(f"Major | Thread {self.thread} | {self.account} | Daily tasks, {[task['title'] for task in resp_json_daily]}")
        await asyncio.sleep(10)
        await self.make_task(resp_json_daily, headers)

        resp_json_daily = resp.json()
        logger.info(f"Major | Thread {self.thread} | {self.account} | Repeat Daily tasks, {[task['title'] for task in resp_json_daily]}")
        await asyncio.sleep(10)
        await self.make_task(resp_json_daily, headers)

        resp = await self.session.get("https://major.glados.app/api/tasks/?is_daily=false", headers=headers)
        resp_json_not_daily = resp.json()
        logger.info(f"Major | Thread {self.thread} | {self.account} | Not Daily tasks, {[task['title'] for task in resp_json_not_daily]}")
        await asyncio.sleep(1)
        await self.make_task(resp_json_not_daily, headers)

        resp = await self.session.post("https://major.glados.app/api/roulette?", headers=headers)
        resp_json_not_daily = resp.json()
        logger.success(f"Major | Thread {self.thread} | {self.account} | Roulette done")
        await asyncio.sleep(1)

        try:
            resp = await self.session.get(f'https://major.glados.app/api/users/{user_id}/', headers=headers)
            resp_json = resp.json()
            rating = resp_json['rating']
            await asyncio.sleep(1)
            resp = await self.session.get(f'https://major.glados.app/api/users/top/position/{user_id}/?', headers=headers)
            resp_json = resp.json()
            position = resp_json['position']
            logger.success(f"Major | Thread {self.thread} | {self.account} | Rating: {rating}, Pos: {position}")
        except Exception as e:
            logger.error(f"Major | Thread {self.thread} | {self.account} | e = {e}")
        sleep_time = 60 * 60 * 12 + uniform(config.DELAYS['MAJOR_SLEEP'][0], config.DELAYS['MAJOR_SLEEP'][1])
        logger.info(f"Major | Thread {self.thread} | {self.account} | Sleep {sleep_time}")
        for _ in range(int(sleep_time / 60)):
            await asyncio.sleep(60)


    async def get_tg_web_data(self):
        try:
            await self.client.connect()
            bot_username = "major"
            bot = await self.client.get_users(bot_username)
            not_found = True
            # Пробуем получить чат по username бота
            try:
                messages = self.client.get_chat_history(bot.id, limit=1)
                async for message in messages:
                    logger.info(f"Major | Thread {self.thread} | {self.account} | Button found")
                else:
                    not_found = False
            except Exception as e:
                clicked = False
                print("Error:", e)        
            major_refs = await self.load_major_refs()
            if major_refs == {}:
                for refka in config.MAJOR_REFS:
                    major_refs[refka] = {'current': 0, 'max': int(uniform(config.MAJOR_REFS_NUMBER[0], config.MAJOR_REFS_NUMBER[1]))}
            # print('refki =',major_refs)
            max_ref_session = -1
            good_ref_link = ''
            for ref in major_refs:
                if max_ref_session < major_refs[ref]['current'] and major_refs[ref]['current'] < major_refs[ref]['max']:
                    max_ref_session = major_refs[ref]['current']
                    good_ref_link = ref
            if good_ref_link == '':
                good_ref_link = '374069367'
            else:
                if not_found:
                    major_refs[good_ref_link]['current'] += 1
            
            await self.save_major_refs(major_refs)
            # logger.info(f"Major | Thread {self.thread} | {self.account} | Loging under ref: {good_ref_link}")

            web_view = await self.client.invoke(RequestAppWebView(
                peer=await self.client.resolve_peer('major'),
                app=InputBotAppShortName(bot_id=await self.client.resolve_peer('major'), short_name="start"),
                platform='ios',
                write_allowed=True,
                start_param=good_ref_link
            ))
            await self.client.disconnect()

            auth_url = web_view.url
            query = unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0])
            return query
        except:
            return None
        

    async def logout(self):
        await self.session.close()

    async def stats(self):
        query = await self.get_tg_web_data()
        headers = {
        'Host': 'major.glados.app',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'Sec-Ch-Ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        'Sec-Ch-Ua-Mobile': '0',
        'Sec-Ch-Ua-Platform': '"Android"',
        'Upgrade-Insecure-Requests': '0',
        'Sec-Fetch-User': '0',
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'Origin': 'https://major.glados.app',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Priority': 'u=1, i'
        }
        json_data = {
            'init_data': query
        }
        # print(f'query {self.account} :', query)
        await asyncio.sleep(2)
        resp = await self.session.post('https://major.glados.app/api/auth/tg/', json=json_data, headers=headers)
        resp_json = resp.json()
        user_id = ''
        if 'user' in resp_json and 'id' in resp_json['user']:
            user_id = resp_json['user']['id']
        logger.info(f"Major | Thread {self.thread} | {self.account} | Auth in app, {resp.status_code}")
        self.session.headers.pop('Authorization', None)
        self.session.headers['Authorization'] = "Bearer " + resp_json.get("access_token")


        try:
            resp = await self.session.get(f'https://major.glados.app/api/users/{user_id}/', headers=headers)
            resp_json = resp.json()
            rating = resp_json['rating']
            await asyncio.sleep(1)
            resp = await self.session.get(f'https://major.glados.app/api/users/top/position/{user_id}/?', headers=headers)
            resp_json = resp.json()
            position = resp_json['position']
        except Exception as e:
            logger.error(f"Major | Thread {self.thread} | {self.account} | e = {e}")
        await self.client.connect()
        me = await self.client.get_me()
        phone_number, name = "'" + me.phone_number, f"{me.first_name} {me.last_name if me.last_name is not None else ''}"
        await self.client.disconnect()
        proxy = self.proxy.replace(f'{config.PROXY_TYPES["REQUESTS"]}://', "") if self.proxy is not None else '-'
        
        return [phone_number, name, str(rating), str(position), proxy]