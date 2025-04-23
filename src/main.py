import asyncio
from datetime import datetime

from pydantic import ValidationError
from pydoll.browser.options import Options

from app.config import config

from app.paths import USER_DIR_PATH
from app.brw.brw import G2GBrowser
from app.logger import logger
from app.process import main_flow
from app.sheet.models import SOffer
from app.update_messages import last_update_message
from app.utils import sleep_for

NOTE_COL = "C"


async def run_in_loop(brw: G2GBrowser):
    logger.info("Start running")

    run_indexes = SOffer.get_run_indexes(config.SPREADSHEET_KEY, config.SHEET_NAME, 2)
    # run_indexes = [5]
    logger.info(f"Run index: {run_indexes}")

    for index in run_indexes:
        logger.info(f"INDEX (ROW): {index}")
        try:
            s_offer = SOffer.get(
                sheet_id=config.SPREADSHEET_KEY,
                sheet_name=config.SHEET_NAME,
                index=index,
            )

            await main_flow(brw, s_offer)
            await sleep_for(s_offer.relax)
        except ValidationError as e:
            logger.error(f"VALIDATION ERROR AT ROW: {index}")
            logger.error(e.errors())
            try:
                now = datetime.now()
                worksheet = SOffer.get_worksheet(
                    sheet_id=config.SPREADSHEET_KEY, sheet_name=config.SHEET_NAME
                )
                worksheet.batch_update(
                    [
                        {
                            "range": f"{NOTE_COL}{index}",
                            "values": [
                                [
                                    f"{last_update_message(now)}: VALIDATION ERROR AT ROW: {index}"
                                ]
                            ],
                        }
                    ]
                )
            except Exception as e:
                logger.error(e)
                await sleep_for(10)

        except Exception as e:
            logger.error(f"FAILED AT ROW: {index}")
            try:
                now = datetime.now()
                worksheet = SOffer.get_worksheet(
                    sheet_id=config.SPREADSHEET_KEY, sheet_name=config.SHEET_NAME
                )
                worksheet.batch_update(
                    [
                        {
                            "range": f"{NOTE_COL}{index}",
                            "values": [[f"{last_update_message(now)}: FAILED: {e}"]],
                        }
                    ]
                )
            except Exception as e1:
                logger.error(e1)
                await sleep_for(10)
            logger.exception(e, exc_info=True)


async def main():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument(f"--user-data-dir={str(USER_DIR_PATH)}")
    async with G2GBrowser.init(options) as brw:
        await brw.get_access_token_in_safe()
        logger.info("Login success")
        while True:
            try:
                logger.info("Run in loop")
                await run_in_loop(brw)
                await sleep_for(config.RELAX_TIME_EACH_ROUND)
            except Exception as e:
                logger.exception(e)


if __name__ == "__main__":
    asyncio.run(main())
