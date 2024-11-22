import asyncio

from playwright.async_api import async_playwright
from loguru import logger

import settings
# from format_proxy import format_proxy
from restore_wallet import restore_wallet
from fake_useragent import FakeUserAgent
from wallets import WALLETS
from meteora import Meteora


async def down(wallet):
    async with async_playwright() as p:
        # if wallet.proxy:
        #     proxy = await format_proxy(wallet.proxy)
        args: list = [
            f"--disable-extensions-except={settings.EXTENTION_PATH}",
            f"--load-extension={settings.EXTENTION_PATH}",
            f"--disable-blink-features=AutomationControlled",
        ]
        if settings.HEADLESS:
            args.append(f"--headless=new")
        user_agent = FakeUserAgent().random
        context = await p.chromium.launch_persistent_context(
            '',
            headless=False,
            args=args,
            user_agent=user_agent,
            # proxy=proxy,
            slow_mo=settings.SLOW_MO
        )

        if not await restore_wallet(context=context, wallet=wallet):
            logger.error(f'{wallet.address}: Can not restore wallet')
            return

        logger.success('Start closing a trade')
        meteora = Meteora(context=context, wallet=wallet)
        await meteora.connect_wallet_to_meteora()
        await asyncio.sleep(2)
        await meteora.withdraw_liquidity()
        await asyncio.sleep(2)
        await meteora.connect_wallet_to_jupiter()
        await asyncio.sleep(2)
        await meteora.swap_from_token_to_sol()
        await asyncio.sleep(2)

#
# async def main():
#     await down(wallet=WALLETS[0])
#
#
# if __name__ == '__main__':
#     asyncio.run(main())