import os
import time
import asyncio
from typing import Dict


from nonebot import on_command
from nonebot.params import CommandArg, ArgStr
from nonebot.matcher import Matcher
from nonebot.typing import T_State
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import MessageEvent, Message, MessageSegment
from nonebot.plugin import PluginMetadata
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from PIL import Image
img_path = str(os.getcwd()).replace('\\', '/') + '/src/plugins/pluto/_cache'


__plugin_meta__ = PluginMetadata(
    name='战雷查水表',
    description='搜索warthunder社区查询玩家履历',
    usage='/战雷查水表 [玩家id]',
    type='`application`',
    homepage='https://github.com/0Neptune0/nonebot-plugin-warthunder-player-check',
    supported_adapters={'~onebot.v11'}
)


options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')


def start_background_loop(loop: asyncio.AbstractEventLoop) -> None:
    asyncio.set_event_loop(loop)
    loop.run_forever()


def get_player_list(search_name: str) -> Dict[int, str]:
    search_rul = f'https://warthunder.com/zh/community/searchplayers?name={search_name}'
    driver = webdriver.Chrome(options=options)
    driver.get(search_rul)
    WebDriverWait(driver, 30).until(
        ec.visibility_of_element_located((By.XPATH, '/html/body/div[4]/div[3]')))
    width = driver.execute_script("return document.documentElement.scrollWidth")
    height = driver.execute_script("return document.documentElement.scrollHeight")
    driver.set_window_size(width, height)
    driver.find_element(By.XPATH, '/html/body/div[4]/div[2]/div[3]/div/section[2]/div/table').screenshot(
        img_path + '/warthunder_search.png')
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.close()
    player_dict = dict()
    for player in soup.find('tbody').find_all('tr'):
        index = int(player.find('td', attrs={'class': 'first_column'}).text)
        search_name = player.find('td', attrs={'class': 'scp_td2'}).text
        player_dict.update({index: search_name})
    return player_dict


def get_playerInfo(name: str):
    playerInfo_url = 'https://warthunder.com/zh/community/userinfo/?nick={}'.format(name.replace(' ', '%'))
    driver = uc.Chrome()
    driver.get(playerInfo_url)
    WebDriverWait(driver, 180).until(ec.visibility_of_element_located((By.XPATH, '/html/body/div[4]/div[3]')))
    driver.execute_script("window.scrollBy(0,180)")
    driver.find_element(By.XPATH, '/html/body/div[4]/div[5]/div/button[1]').click()
    time.sleep(1)
    driver.save_screenshot(img_path + '/warthunder_cache1.png')
    driver.find_element(By.XPATH, '/html/body/div[4]/div[2]/div[3]/div/section/div[2]/div[2]/div[2]/div').screenshot(
        img_path + '/warthunder_cache2.png')
    driver.find_element(By.XPATH, '/html/body/div[4]/div[2]/div[3]/div/section/div[2]/div[2]/div[2]/ul/li[2]').click()
    time.sleep(1)
    driver.find_element(By.XPATH, '/html/body/div[4]/div[2]/div[3]/div/section/div[2]/div[2]/div[2]/div').screenshot(
        img_path + '/warthunder_cache3.png')
    driver.find_element(By.XPATH, '/html/body/div[4]/div[2]/div[3]/div/section/div[2]/div[2]/div[2]/ul/li[3]').click()
    time.sleep(1)
    driver.find_element(By.XPATH, '/html/body/div[4]/div[2]/div[3]/div/section/div[2]/div[2]/div[2]/div').screenshot(
        img_path + '/warthunder_cache4.png')
    driver.find_element(By.XPATH, '/html/body/div[4]/div[2]/div[3]/div/section/div[2]/div[3]').screenshot(
        img_path + '/warthunder_cache5.png')
    driver.close()
    img1 = Image.open(img_path + '/warthunder_cache1.png')
    im_copy = img1.copy()
    im_crop = im_copy.crop((215, 90, 1690, 950))
    img = Image.new('RGB', (1475, 3190))
    img.paste(im_crop, (0, 0))
    img2 = Image.open(img_path + '/warthunder_cache2.png')
    img.paste(img2.resize((1475, 479 * 1475 // 1180)), (0, 860))
    img3 = Image.open(img_path + '/warthunder_cache3.png')
    img.paste(img3.resize((1475, 479 * 1475 // 1180)), (0, 1450))
    img4 = Image.open(img_path + '/warthunder_cache4.png')
    img.paste(img4.resize((1475, 479 * 1475 // 1180)), (0, 2040))
    img5 = Image.open(img_path + '/warthunder_cache5.png')
    img.paste(img5.resize((1475, 449 * 1475 // 1180)), (0, 2630))
    img.save(img_path + '/warthunder_cache.png')


warthunder = on_command('warthunder', aliases={'战雷查水表'}, priority=99, block=True)


@warthunder.handle()
async def handle_first_receive(matcher: Matcher, event: MessageEvent, args: Message = CommandArg()):
    plain_text = args.extract_plain_text()
    if plain_text:
        matcher.set_arg("search_player", args)


@warthunder.got('search_player', prompt="请输入要查找的玩家id(如果id中有空格用%替代)")
async def player_dict_receive(event: MessageEvent, state: T_State, search_name: str = ArgStr("search_player")):
    try:
        search_name = search_name.replace('%', '%20')
        player_dict = (await asyncio.to_thread(get_player_list, search_name=search_name))
        state.update({'player_dict': player_dict})
        await warthunder.send(MessageSegment.image('file:///' + img_path + '/warthunder_search.png'))
    except Exception as e:
        logger.error(e)
        await warthunder.finish('出现错误, 请重试')


@warthunder.got('player_index', prompt="请输入对应序号")
async def get_player_info(event: MessageEvent, state: T_State, index: str = ArgStr("player_index")):
    try:
        await warthunder.send('查询中, 查询速度较慢请耐心等待')
        index = int(index)
        name = state['player_dict'].get(index)
        if name:
            name.replace(' ', '%')
            await asyncio.to_thread(get_playerInfo, name=name)
            await warthunder.finish(MessageSegment.image('file:///' + img_path + '/warthunder_cache.png'))
        else:
            raise ValueError
    except ValueError:
        await warthunder.reject('错误的序号，请重新输入')
