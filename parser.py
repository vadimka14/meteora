import asyncio
import json
import aiohttp
import requests
# from bs4 import BeautifulSoup as BS
from fake_useragent import FakeUserAgent
import settings


async def parse_price():
    headers = {
        'user-agent': FakeUserAgent().random
    }

    # meteora = settings.METEORA_API
    # r = requests.get(url=meteora, headers=headers)
    # data = r.json()
    # current_price = 0
    # for group in data["groups"]:
    #     for pair in group["pairs"]:
    #         if pair['name'] == 'aura-SOL':
    #             current_price = pair['current_price']
    #             break
    #     return current_price
    try:
        dexscreener = f"https://api.dexscreener.com/latest/dex/search/?q={settings.TOKEN_NAME}/SOL"
        async with aiohttp.ClientSession() as session:
            async with session.get(dexscreener, headers=headers) as r:
                data = await r.json()

                if not isinstance(data, dict) or "pairs" not in data:
                    raise ValueError("Invalid response format")

                current_price = 0
                for pair in data["pairs"]:
                    if pair.get('pairAddress') == str(settings.PAIR_CONTRACT):
                        price = pair.get('priceNative')
                        if price is not None:
                            current_price = float(price)
                            break

                if current_price == 0:
                    raise ValueError("Price not found for specified pair")

                return current_price

    except aiohttp.ClientError as e:
        raise ValueError(f"Request error: {e}")
    except ValueError as e:
        raise e
    except Exception as e:
        raise ValueError(f"Unexpected error: {str(e)}")
