import asyncio
from typing import Dict


from nonebot import on_command, get_driver
from nonebot.params import CommandArg, ArgStr
from nonebot.matcher import Matcher
from nonebot.typing import T_State
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import MessageEvent, Message, MessageSegment
from nonebot.plugin import PluginMetadata
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from PIL import Image
from pydantic import BaseModel


class Config(BaseModel):
    cache_path: str


config = Config.parse_obj(get_driver().config)


__plugin_meta__ = PluginMetadata(
    name='战雷查水表',
    description='搜索warthunder社区查询玩家履历',
    usage='/战雷查水表 [玩家id]',
    type='application',
    homepage='https://github.com/0Neptune0/nonebot-plugin-warthunder-player-check',
    supported_adapters={'~onebot.v11'}
)


async def get_player_list(search_name: str) -> Dict[int, str]:
    search_url = f'https://warthunder.com/zh/community/searchplayers?name={search_name}'
    async with async_playwright() as p:
        browser_type = p.firefox
        browser = await browser_type.launch(headless=True, args=['--start-maximized'])
        page = await browser.new_page()
        await page.goto(search_url, timeout=0, wait_until="commit")
        await asyncio.sleep(1)
        await page.locator("""//*[@id="bodyRoot"]/div[4]/div[2]/div[3]/div/section[2]/div/table""").screenshot(
            path="file:///" + config.cache_path + '/warthunder_search.png',)
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        player_dict = dict()
        for player in soup.find('tbody').find_all('tr'):
            index = int(player.find('td', attrs={'class': 'first_column'}).text)
            search_name = player.find('td', attrs={'class': 'scp_td2'}).text
            player_dict.update({index: search_name})
        return player_dict


async def get_player_detailed_info(name: str):
    player_info_url = 'https://warthunder.com/zh/community/userinfo/?nick={}'.format(name.replace(' ', '%'))
    async with async_playwright() as p:
        browser_type = p.firefox
        browser = await browser_type.launch(headless=True, args=['--start-maximized'])
        content = await browser.new_context(viewport={'width': 1920, 'height': 1920})
        page = await browser.new_page()
        await page.goto(player_info_url, timeout=0)
        await page.locator("xpath=/html/body/div[4]/div[5]/div/button[1]").click()
        await asyncio.sleep(0.5)
        await page.locator(
            """xpath=//*[@id="bodyRoot"]/div[4]/div[2]/div[3]/div/section/div[2]/div[1]""").screenshot(
            type="png", path="file:///" + config.cache_path + '/warthunder_cache1.png')
        await page.locator(
            """xpath=//*[@id="bodyRoot"]/div[4]/div[2]/div[3]/div/section/div[2]/div[2]/div[1]""").screenshot(
            type="png", path="file:///" + config.cache_path + '/warthunder_cache2.png')
        await page.locator(
            """xpath=//*[@id="bodyRoot"]/div[4]/div[2]/div[3]/div/section/div[2]/div[2]/div[2]/div""").screenshot(
            type="png", path="file:///" + "file:///" + config.cache_path + '/warthunder_cache3.png')
        await page.locator(
            """xpath=//*[@id="bodyRoot"]/div[4]/div[2]/div[3]/div/section/div[2]/div[2]/div[2]/ul/li[2]""").click()
        await asyncio.sleep(0.5)
        await page.locator(
            """xpath=//*[@id="bodyRoot"]/div[4]/div[2]/div[3]/div/section/div[2]/div[2]/div[2]/div""").screenshot(
            type="png", path="file:///" + config.cache_path + '/warthunder_cache4.png')
        await page.locator(
            """xpath=//*[@id="bodyRoot"]/div[4]/div[2]/div[3]/div/section/div[2]/div[2]/div[2]/ul/li[3]""").click()
        await asyncio.sleep(0.5)
        await page.locator(
            """xpath=/html/body/div[4]/div[2]/div[3]/div/section/div[2]/div[2]/div[2]/div/div[3]""").screenshot(
            type="png", path="file:///" + config.cache_path + '/warthunder_cache5.png')
        await page.locator("""xpath=//*[@id="bodyRoot"]/div[4]/div[2]/div[3]/div/section/div[2]/div[3]""").screenshot(
            type="png", path="file:///" + config.cache_path + '/warthunder_cache6.png')
        img1 = Image.open("file:///" + config.cache_path + '/warthunder_cache1.png')
        im_copy = img1.copy()
        img = Image.new('RGB', (1475, 3090))
        img.paste(im_copy, (170, 5))
        img2 = Image.open("file:///" + config.cache_path + '/warthunder_cache2.png')
        img.paste(img2.resize((1475, 479 * 1475 // 1180)), (0, 160))
        img3 = Image.open("file:///" + config.cache_path + '/warthunder_cache3.png')
        img.paste(img3.resize((1475, 479 * 1475 // 1180)), (0, 755))
        img4 = Image.open("file:///" + config.cache_path + '/warthunder_cache4.png')
        img.paste(img4.resize((1475, 479 * 1475 // 1180)), (0, 1355))
        img5 = Image.open("file:///" + config.cache_path + '/warthunder_cache5.png')
        img.paste(img5.resize((1475, 449 * 1475 // 1180)), (0, 1955))
        img6 = Image.open("file:///" + config.cache_path + '/warthunder_cache6.png')
        img.paste(img6.resize((1475, 449 * 1475 // 1180)), (0, 2515))
        img.save("file:///" + config.cache_path + '/warthunder_cache.png')


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
        player_dict = await get_player_list(search_name=search_name)
        state.update({'player_dict': player_dict})
        await warthunder.send(MessageSegment.image('file:///' + "file:///" + config.cache_path + '/warthunder_search.png'))
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
            await get_player_detailed_info(name)
            await warthunder.finish(MessageSegment.image('file:///' + "file:///" + config.cache_path + '/warthunder_cache.png'))
        else:
            raise ValueError
    except ValueError:
        await warthunder.reject('错误的序号，请重新输入')
