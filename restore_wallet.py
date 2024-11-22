import asyncio

from loguru import logger
from playwright.async_api import BrowserContext, expect

from data.models import Wallet
import settings


async def restore_wallet(context: BrowserContext, wallet: Wallet) -> bool:
    for num in range(1, settings.ATTEMPTS_NUMBER_RESTORE + 1):
        try:
            logger.info(f'{wallet.address} | Starting recover wallet')
            page = context.pages[0]
            await page.goto(f'chrome-extension://{settings.EXTENTION_IDENTIFIER}/options.html?onboarding=true')

            titles = [await p.title() for p in context.pages]
            while "Backpack" not in titles:
                titles = [await p.title() for p in context.pages]
            await page.wait_for_load_state()


            # Import Wallet
            await page.locator(
                # '//*[@id="options"]/span/span/div/div/div/div/div/div[1]/div/div/div[3]/div/button[2]'
                '//*[@id="options"]/span/span/div/div/div/div/div/div[1]/div/div/div[3]/div/span[2]/button'
            ).click()
            await page.get_by_text(text='Solana').click()
            # Import private key
            await page.locator(
                '//*[@id="options"]/span/span/div/div/div/div/div[1]/div[1]/div/div/div[2]/span[4]/button'
            ).click()
            # Enter private key
            await page.locator(
                # '//*[@id="options"]/span/span/div/div/div/div/div[1]/div[1]/div/div/div[2]/span/textarea'
                '//*[@id="options"]/span/span/div/div/div/div/div[1]/div[1]/div/div/div[2]/span/span/textarea'
            ).fill(
                f'{wallet.private_key}'
            )

            # Import
            await page.locator(
                # '//*[@id="options"]/span/span/div/div/div/div/div[1]/div[1]/div/div/div[3]/button'
                '//*[@id="options"]/span/span/div/div/div/div/div[1]/div[1]/div/div/div[3]/span/button'
            ).click()

            # fill password
            await page.locator(
                # '//*[@id="options"]/span/span/div/div/div/div/div[1]/div[1]/div/form/div[2]/div[1]/span/input'
                '//*[@id="options"]/span/span/div/div/div/div/div[1]/div[1]/div/form/div[2]/div[1]/span/span/input'
            ).type(
                settings.EXTENTION_PASSWORD
            )
            # fill password 2
            await page.locator(
                # '//*[@id="options"]/span/span/div/div/div/div/div[1]/div[1]/div/form/div[2]/div[2]/span/input'
                '//*[@id="options"]/span/span/div/div/div/div/div[1]/div[1]/div/form/div[2]/div[2]/span/span/input'
            ).type(
                settings.EXTENTION_PASSWORD
            )

            # agree
            await page.locator('input[type="checkbox"]').click()

            # next
            await page.locator(
                # '//*[@id="options"]/span/span/div/div/div/div/div[1]/div[1]/div/form/div[3]/button[2]'
                '//*[@id="options"]/span/span/div/div/div/div/div[1]/div[1]/div/form/div[3]/span/button'
            ).click()

            await expect(page.get_by_role('button', name='Open Backpack')).to_be_visible()
            await asyncio.sleep(3)
            # change rpc  node
            await page.goto(f'chrome-extension://{settings.EXTENTION_IDENTIFIER}/popout.html')

            await page.locator(
                '//*[@id="root"]/span[1]/span/div/div/div[6]/div/div/div[2]/div[1]/div/div[2]/div[2]/div/div/div/div[1]/div/div[1]/div/div/div/div/div/div/div[1]/div/div[2]/div[2]/div/div/div/div[2]/div/div[2]/div[2]/div[1]/div/div/button'
            ).click()
            await asyncio.sleep(2)
            await page.get_by_text(
                'Settings'
            ).click()
            await asyncio.sleep(2)
            await page.get_by_test_id(
                'Solana'
            ).click()
            await asyncio.sleep(2)
            await page.locator(
                '//*[@id="root"]/span[1]/span/div/div/div[6]/div/div/div[2]/div[1]/div[2]/div[2]/div[2]/div/div/div/div[1]/div/div/div/div[1]/div[2]/div[2]/div[2]/div/div/div/div[1]/div/div[1]/ul/div[1]'
            ).click()

            await page.get_by_test_id('Custom').click()

            await page.get_by_placeholder(
                'RPC URL'
            ).type(str(settings.own_node_rpc))

            await page.locator(
                '//*[@id="root"]/span[1]/span/div/div/div[6]/div/div/div[2]/div[1]/div[2]/div[2]/div[2]/div/div/div/div[1]/div/div/div/div[1]/div[4]/div[2]/div[2]/div/div/div/div[1]/div/div[1]/div/form/div[2]/button'
            ).click()
            logger.success(f'{wallet.address} | Wallet Ready To Work')
            await page.close()
            return True

        except Exception as err:
            logger.error(f'{wallet.address} | Not Recovered ({err})')
            logger.info(f'Error when getting an account, trying again, attempt No.{num}')

    return False
