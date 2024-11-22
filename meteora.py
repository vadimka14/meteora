import asyncio
import random

from playwright.async_api import BrowserContext, expect
from loguru import logger

import settings
from data.models import Wallet


class Meteora:
    def __init__(self, context: BrowserContext, wallet: Wallet):
        self.context = context
        self.wallet = wallet

    async def get_backpack_page(self):
        titles = [await p.title() for p in self.context.pages]
        backpack_page_index = 0

        for title in titles:
            if 'Backpack' in title:
                page = self.context.pages[backpack_page_index]
                await page.reload()
                return page
            backpack_page_index += 1

        backpack_page = await self.context.new_page()
        await backpack_page.goto(f'chrome-extension://{settings.EXTENTION_IDENTIFIER}/options.html?onboarding=true')
        return backpack_page

    # async def get_backpack_popup_page(self):
    #     titles = [await p.title() for p in self.context.pages]
    #     backpack_popup_page_index = 0
    #
    #     for title in titles:
    #         if 'Backpack' in title:
    #             page = self.context.pages[backpack_popup_page_index]
    #             await page.reload()
    #             return page
    #         backpack_popup_page_index += 1
    #
    #     backpack_popup_page = await self.context.new_page()
    #     await backpack_popup_page.goto(f'chrome-extension://{settings.EXTENTION_IDENTIFIER}/popup.html?onboarding=true')
    #     return backpack_popup_page

    async def get_jupiter_page(self):
        titles = [await p.title() for p in self.context.pages]
        jupiter_page_index = 0

        for title in titles:
            if 'Jupiter' in title:
                page = self.context.pages[jupiter_page_index]
                await page.reload()
                return page
            jupiter_page_index += 1

        jupiter_page = await self.context.new_page()
        await jupiter_page.goto(settings.JUP_URL)
        return jupiter_page

    async def get_meteora_pool_page(self):
        titles = [await p.title() for p in self.context.pages]
        meteora_pool_page_index = 0

        for title in titles:
            if 'Jupiter' in title:
                page = self.context.pages[meteora_pool_page_index]
                await page.reload()
                return page
            meteora_pool_page_index += 1

        meteora_pool_page = await self.context.new_page()
        await meteora_pool_page.goto(settings.METEORA_POOL_URL)
        return meteora_pool_page

    async def connect_wallet_to_jupiter(self, max_retries: int = 10) -> None:
        logger.debug(f'{self.wallet.address} | Wallet Connecting To Jupiter')

        for attempt in range(1, max_retries + 1):
            try:
                await asyncio.sleep(5)
                jupiter_page = await self.get_jupiter_page()
                await asyncio.sleep(2)
                backpack_page = await self.get_backpack_page()

                await jupiter_page.bring_to_front()

                await asyncio.sleep(2)

                connect_wallet = jupiter_page.locator(
                    '//*[@id="__next"]/div[2]/div[1]/div/div[4]/div[2]/div/button[2]/div'
                )
                await expect(connect_wallet.first).to_be_visible()
                await connect_wallet.click()
                await asyncio.sleep(3)

                backpack_btn = jupiter_page.get_by_text('Backpack')
                await expect(backpack_btn.first).to_be_enabled()
                await backpack_btn.click()
                await asyncio.sleep(3)

                approve_btn = backpack_page.locator(
                    '//*[@id="options"]/div/div/span/span/div/div/div[2]/div[2]/div[2]/div'
                )
                await expect(approve_btn.first).to_be_enabled()
                await approve_btn.click()
                await asyncio.sleep(3)

                await jupiter_page.bring_to_front()
                logger.debug(f'{self.wallet.address} | Wallet was connected To Jupiter')
                # try soflafdf
                return

            except Exception as e:
                logger.error(f'{self.wallet.address} | Error occurred: {str(e)}')
                if attempt <= max_retries:
                    logger.info(f'Retrying... (Attempt {attempt} of {max_retries})')
                else:
                    logger.error(f'{self.wallet.address} | Unable to connect after {max_retries} attempts')
                    raise

    async def swap_from_sol_to_token(self, max_retries: int = 10) -> None:
        logger.debug(f'{self.wallet.address} | Starting Swap SOL to token')
        backpack_page = await self.get_backpack_page()
        jupiter_page = await self.get_jupiter_page()
        for attempt in range(1, max_retries + 1):
            try:
                await jupiter_page.bring_to_front()
                await asyncio.sleep(2)

                # кнопка списку токена 1
                choose_token_btn = jupiter_page.locator(
                    '//*[@id="__next"]/div[2]/div[3]/div[2]/div[2]/div[2]/div[2]/form/div[1]/div[1]/div[2]/div/button'
                )
                await expect(choose_token_btn.first).to_be_visible()
                await choose_token_btn.click()

                await asyncio.sleep(3)

                # вибір солани
                solana_btn = jupiter_page.get_by_text('Solana')
                await expect(solana_btn.first).to_be_enabled()
                await solana_btn.hover()
                await solana_btn.click()

                await asyncio.sleep(3)
                # заповнення емаунт
                await jupiter_page.get_by_placeholder('0.00').type(str(settings.AMOUNT_SOL_TO_SELL))

                await asyncio.sleep(2)
                # вибір списку токена 2
                choose_token_btn_2 = jupiter_page.locator(
                    '//*[@id="__next"]/div[2]/div[3]/div[2]/div[2]/div[2]/div[2]/form/div[1]/div[3]/div[2]/div/button'
                )
                await expect(choose_token_btn_2.first).to_be_enabled()
                await choose_token_btn_2.click()

                await asyncio.sleep(3)
                # знаходження токена по контракту
                await jupiter_page.locator(
                    '//*[@id="__next"]/div[3]/div[1]/div/div/div[1]/input'
                ).type(str(settings.TOKEN_CONTRACT))
                # вибрі токена 2
                token_btn = jupiter_page.locator(
                    '//*[@id="__next"]/div[3]/div[1]/div/div/div[4]/div/div/div/li'
                )
                await expect(token_btn.first).to_be_enabled()
                await token_btn.click()

                await asyncio.sleep(3)
                # своп
                swap_btn = jupiter_page.locator(
                    '//*[@id="__next"]/div[2]/div[3]/div[2]/div[2]/div[2]/div[2]/form/div[4]/button'
                )
                await expect(swap_btn.first).to_be_enabled()
                await swap_btn.click()
                await asyncio.sleep(3)

                approve_btn = backpack_page.locator(
                    '//*[@id="options"]/div/div/span/span/div/div/div[3]/div[2]'
                )
                await expect(approve_btn.first).to_be_enabled()
                await approve_btn.click()

                await asyncio.sleep(2)

                await jupiter_page.bring_to_front()
                await asyncio.sleep(2)
                logger.debug(f'{self.wallet.address} | Swap token to SOL is successful')
                return

            except Exception as e:
                logger.error(f'{self.wallet.address} | Error occurred: {str(e)}')
                await jupiter_page.reload()
                await backpack_page.reload()
                if attempt <= max_retries:
                    logger.info(f'Retrying... (Attempt {attempt} of {max_retries})')
                else:
                    logger.error(
                        f'{self.wallet.address} | Unable to complete SOL to token swap after {max_retries} attempts')
                    raise

    async def swap_from_token_to_sol(self, max_retries: int = 10) -> None:
        logger.debug(f'{self.wallet.address} | Starting Swap token to SOL')
        backpack_page = await self.get_backpack_page()
        jupiter_page = await self.get_jupiter_page()
        for attempt in range(1, max_retries + 1):
            try:
                await jupiter_page.bring_to_front()
                await asyncio.sleep(2)
                # вибір списку токена
                choose_token_btn = jupiter_page.locator(
                    '//*[@id="__next"]/div[2]/div[3]/div[2]/div[2]/div[2]/div[2]/form/div[1]/div[1]/div[2]/div/button'
                )
                await expect(choose_token_btn.first).to_be_visible()
                await choose_token_btn.click()

                await asyncio.sleep(3)
                # знаходження токена по контракту
                await jupiter_page.locator(
                    '//*[@id="__next"]/div[3]/div[1]/div/div/div[1]/input'
                ).type(str(settings.TOKEN_CONTRACT))
                # вибір токена
                token_btn = jupiter_page.locator(
                    '//*[@id="__next"]/div[3]/div[1]/div/div/div[4]/div/div/div/li'
                )
                await expect(token_btn.first).to_be_enabled()
                await token_btn.click()

                await asyncio.sleep(3)

                #  нажимаємо макс для заповення інпут

                max_btn = jupiter_page.locator(
                    '//*[@id="__next"]/div[2]/div[3]/div[2]/div[2]/div[2]/div[2]/form/div[1]/div[1]/div[1]/div/div[2]/button[2]'
                )
                await expect(max_btn.first).to_be_enabled()
                await max_btn.click()

                await asyncio.sleep(3)

                # кнопка списку токена 1
                choose_token_btn_2 = jupiter_page.locator(
                    '//*[@id="__next"]/div[2]/div[3]/div[2]/div[2]/div[2]/div[2]/form/div[1]/div[3]/div[2]/div/button'
                )
                await expect(choose_token_btn_2.first).to_be_visible()
                await choose_token_btn_2.click()

                await asyncio.sleep(3)

                # вибір солани
                solana_btn = jupiter_page.get_by_text('Solana', exact=True)
                await expect(solana_btn.first).to_be_enabled()
                await solana_btn.hover()
                await solana_btn.click()

                await asyncio.sleep(3)

                # своп
                swap_btn = jupiter_page.locator(
                    '//*[@id="__next"]/div[2]/div[3]/div[2]/div[2]/div[2]/div[2]/form/div[4]/button'
                )
                await expect(swap_btn.first).to_be_enabled()
                await swap_btn.click()
                await asyncio.sleep(3)

                approve_btn = backpack_page.locator(
                    '//*[@id="options"]/div/div/span/span/div/div/div[3]/div[2]'
                )
                await expect(approve_btn.first).to_be_enabled()
                await approve_btn.click()

                await asyncio.sleep(2)

                await jupiter_page.bring_to_front()
                await asyncio.sleep(30)

                logger.debug(f'{self.wallet.address} | Swap token to SOL is successful')
                return

            except Exception as e:
                logger.error(f'{self.wallet.address} | Error occurred: {str(e)}')
                await jupiter_page.reload()
                await backpack_page.reload()
                if attempt <= max_retries:
                    logger.info(f'Retrying... (Attempt {attempt} of {max_retries})')
                else:
                    logger.error(
                        f'{self.wallet.address} | Unable to complete token to SOL swap after {max_retries} attempts')
                    raise

    async def connect_wallet_to_meteora(self, max_retries: int = 10) -> None:
        logger.debug(f'{self.wallet.address} | Wallet Connecting To Meteora')

        for attempt in range(1, max_retries + 1):
            try:
                await asyncio.sleep(5)
                meteora_pool_page = await self.get_meteora_pool_page()
                await asyncio.sleep(2)
                backpack_page = await self.get_backpack_page()

                await meteora_pool_page.bring_to_front()

                await asyncio.sleep(2)

                connect_btn = meteora_pool_page.locator(
                    '//*[@id="__next"]/div[1]/div[4]/div/div/div[3]/div[2]/button'
                )
                await expect(connect_btn.first).to_be_enabled()
                await connect_btn.click()

                await asyncio.sleep(3)

                backpack_btn = meteora_pool_page.get_by_text('Backpack')
                await expect(backpack_btn.first).to_be_enabled()
                await backpack_btn.click()

                await asyncio.sleep(2)

                approve_btn = backpack_page.locator(
                    '//*[@id="options"]/div/div/span/span/div/div/div[2]/div[2]/div[2]'
                )
                await expect(approve_btn.first).to_be_enabled()
                await approve_btn.click()

                await asyncio.sleep(3)

                await meteora_pool_page.bring_to_front()

                await self.additional_settings(meteora_pool_page=meteora_pool_page)
                await asyncio.sleep(1)
                logger.debug(f'{self.wallet.address} | Wallet was connected To Meteora')
                return

            except Exception as e:
                logger.error(f'{self.wallet.address} | Error occurred: {str(e)}')
                if attempt <= max_retries:
                    logger.info(f'Retrying... (Attempt {attempt} of {max_retries})')
                else:
                    logger.error(f'{self.wallet.address} | Unable to connect after {max_retries} attempts')
                    raise

    async def add_liquidity(self, max_retries: int = 10) -> None:
        logger.debug(f'{self.wallet.address} | Starting add liquidity at Meteora')
        backpack_page = await self.get_backpack_page()
        meteora_pool_page = await self.get_meteora_pool_page()
        # jupiter_page = await self.get_jupiter_page()
        for attempt in range(1, max_retries + 1):
            try:
                await meteora_pool_page.bring_to_front()
                await asyncio.sleep(2)

                add_liquidity_btn = meteora_pool_page.locator(
                    '//*[@id="__next"]/div[1]/div[5]/div/div[2]/div/div[2]/div[2]/div[2]/div/div/button'
                )
                await expect(add_liquidity_btn.first).to_be_enabled()
                await add_liquidity_btn.click()
                await asyncio.sleep(3)

                await meteora_pool_page.locator(
                    '//*[@id="__next"]/div[1]/div[5]/div/div[2]/div/div[2]/div[2]/div[2]/form/div[1]/div[2]/div[2]/div[1]/input'
                ).type(str(settings.AMOUNT_SOL_TO_ADD))
                # -------------------------------
                # тут може бути введення відсотків
                # ---------------------------
                await asyncio.sleep(10)

                approve_liquidity_btn = meteora_pool_page.locator(
                    '//*[@id="__next"]/div[1]/div[5]/div/div[2]/div/div[2]/div[2]/div[2]/form/button'
                )
                await expect(approve_liquidity_btn.first).to_be_enabled()
                await approve_liquidity_btn.click()
                await asyncio.sleep(3)

                await backpack_page.bring_to_front()

                await asyncio.sleep(2)

                approve_btn = backpack_page.locator(
                    '//*[@id="options"]/div/div/span/span/div/div/div[3]/div[2]'
                )
                await expect(approve_btn.first).to_be_enabled()
                await approve_btn.click()
                await asyncio.sleep(2)

                await meteora_pool_page.bring_to_front()
                await asyncio.sleep(120)
                logger.debug(f'{self.wallet.address} | Liquidity was added at Meteora')
                return

            except Exception as e:
                logger.error(f'{self.wallet.address} | Error occurred: {str(e)}')
                await meteora_pool_page.reload()
                await backpack_page.reload()
                if attempt <= max_retries:
                    logger.info(f'Retrying... (Attempt {attempt} of {max_retries})')
                else:
                    logger.error(
                        f'{self.wallet.address} | Unable to complete adding liquidity after {max_retries} attempts')
                    raise

    async def withdraw_liquidity(self, max_retries: int = 10) -> None:
        logger.debug(f'{self.wallet.address} | Starting withdraw_liquidity at Meteora')
        backpack_page = await self.get_backpack_page()
        meteora_pool_page = await self.get_meteora_pool_page()
        for attempt in range(1, max_retries + 1):
            try:
                await meteora_pool_page.bring_to_front()
                await asyncio.sleep(2)

                position_btn = meteora_pool_page.get_by_text(f'SOL per {settings.TOKEN_NAME}')
                await expect(position_btn.first).to_be_enabled()
                await position_btn.click()

                await asyncio.sleep(3)

                withdraw_btn = meteora_pool_page.locator(
                    '//*[@id="radix-:r0:"]/div[2]/div[1]/div/div[2]'
                )
                await expect(withdraw_btn.first).to_be_enabled()
                await withdraw_btn.click()

                await asyncio.sleep(3)

                withdraw_and_close_btn = meteora_pool_page.get_by_text(
                    'Withdraw & Close Position'
                )
                await expect(withdraw_and_close_btn.first).to_be_enabled()
                await withdraw_and_close_btn.click()

                await asyncio.sleep(2)
                await backpack_page.bring_to_front()
                approve_btn = backpack_page.locator(
                    '//*[@id="options"]/div/div/span/span/div/div/div[3]/div[2]'
                )
                await expect(approve_btn.first).to_be_enabled()
                await approve_btn.click()
                await asyncio.sleep(2)

                await meteora_pool_page.bring_to_front()

                await asyncio.sleep(40)

                # for attemptt in range(1, max_retries + 1):
                #     try:
                #         withdraw_btn = meteora_pool_page.locator(
                #             '//*[@id="radix-:r0:"]/div[2]/div[1]/div/div[2]'
                #         )
                #         await expect(withdraw_btn.first).to_be_enabled()
                #         await withdraw_btn.click()
                #
                #         await asyncio.sleep(3)
                #
                #         withdraw_and_close_btn = meteora_pool_page.locator(
                #             '//*[@id="radix-:r0:"]/div[2]/div[2]/form/div[3]/div/button'
                #         )
                #         await expect(withdraw_and_close_btn.first).to_be_enabled()
                #         await withdraw_and_close_btn.click()
                #
                #         await asyncio.sleep(2)
                #         await backpack_page.bring_to_front()
                #         approve_btn = backpack_page.locator(
                #             '//*[@id="options"]/div/div/span/span/div/div/div[3]/div[2]'
                #         )
                #         await expect(approve_btn.first).to_be_enabled()
                #         await approve_btn.click()
                #         await asyncio.sleep(2)
                #
                #         await meteora_pool_page.bring_to_front()
                #
                #         await asyncio.sleep(90)
                #         if await check_button(meteora_pool_page=meteora_pool_page):
                #             continue
                #         else:
                #             break
                #
                #     except Exception as e:
                #         logger.error(f'{self.wallet.address} | Error occurred: {str(e)}')
                #         await meteora_pool_page.reload()
                #         await backpack_page.reload()
                #         if attemptt <= max_retries:
                #             logger.info(f'Retrying... (Attempt {attemptt} of {max_retries})')
                #         else:
                #             logger.error(
                #                 f'{self.wallet.address} | Unable to complete withdrawing liquidity after {max_retries} attempts')
                #             raise
                return
            except Exception as e:
                logger.error(f'{self.wallet.address} | Error occurred: {str(e)}')
                await meteora_pool_page.reload()
                await backpack_page.reload()
                if attempt <= max_retries:
                    logger.info(f'Retrying... (Attempt {attempt} of {max_retries})')
                else:
                    logger.error(
                        f'{self.wallet.address} | Unable to complete withdrawing liquidity after {max_retries} attempts')
                    raise

    async def additional_settings(self, meteora_pool_page):
        await asyncio.sleep(1)
        # ----------- change priority ---------------
        priority_btn = meteora_pool_page.get_by_text(
            'Priority:'
            # '//*[@id="__next"]/div[1]/div[3]/div/div/div[3]/div[1]/div[1]/div/div[1]/button'
        )
        await expect(priority_btn.first).to_be_visible()
        # await priority_btn.hover()
        await priority_btn.click()

        await asyncio.sleep(1)

        turbo_btn = meteora_pool_page.get_by_text(
            'Ultra'
            # '//*[@id="__next"]/div[1]/div[3]/div/div/div[3]/div[1]/div[1]/div/div[2]/div/div[2]/div/button[3]'
        )
        await expect(turbo_btn.first).to_be_visible()
        await turbo_btn.click()

        await asyncio.sleep(1)

        save_changes_btn = meteora_pool_page.get_by_text(
            'Save Changes'
            # '//*[@id="__next"]/div[1]/div[3]/div/div/div[3]/div[1]/div[1]/div/div[2]/div/button'
        )
        await expect(save_changes_btn.first).to_be_enabled()
        await save_changes_btn.click()
        # -------- change rpc ----------------
        # settings_btn = meteora_pool_page.locator(
        #     '//*[@id="__next"]/div[1]/div[3]/div/div/div[3]/div[1]/div[3]/div/div[1]/button'
        # )
        # await expect(settings_btn.first).to_be_visible()
        # await settings_btn.click()
        #
        # custom_btn = meteora_pool_page.locator(
        #     '//*[@id="__next"]/div[1]/div[3]/div/div/div[3]/div[1]/div[3]/div/div[2]/div/div[3]/label[4]'
        # )
        # await expect(custom_btn.first).to_be_visible()
        # await custom_btn.click()
        #
        # await meteora_pool_page.locator(
        #     '//*[@id="__next"]/div[1]/div[3]/div/div/div[3]/div[1]/div[3]/div/div[2]/div/div[3]/div/input'
        # ).fill(str(settings.own_node_rpc))
        #
        # await asyncio.sleep(1)
        #
        # save_btn = meteora_pool_page.locator(
        #     '//*[@id="__next"]/div[1]/div[3]/div/div/div[3]/div[1]/div[3]/div/div[2]/div/div[3]/div/button'
        # )
        # await expect(save_btn.first).to_be_visible()
        # await save_btn.click()

        await meteora_pool_page.reload()
        # --------- change slippage ---------
        slippage_btn = meteora_pool_page.get_by_text(
            '1%', exact=True
            # '//*[@id="__next"]/div[1]/div[4]/div/div[2]/div/div[2]/div[2]/div[1]/div[2]/div[2]'
        )
        await expect(slippage_btn.first).to_be_visible()
        await slippage_btn.click()

        await meteora_pool_page.locator(
            '//*[@id="__next"]/div[3]/div[1]/div/div/div[2]/form/div/div[3]/input'
        ).fill(str(settings.SLIPPAGE))

        save_settings = meteora_pool_page.get_by_text(
            'Save setting'
            # '//*[@id="__next"]/div[3]/div[1]/div/div/div[2]/form/button'
        )
        await expect(save_settings.first).to_be_visible()
        await save_settings.click()
        await asyncio.sleep(1)
        await meteora_pool_page.reload()


# async def check_button(meteora_pool_page):
#     try:
#         # await expect(meteora_pool_page.locator('//*[@id="88417"]/div[1]/div/div/div[3]/div[2]/button[2]').first).to_be_enabled()
#         await expect(
#             meteora_pool_page.get_by_text('Retry failed txs').first).to_be_enabled()
#         return True
#     except:
#         return False


