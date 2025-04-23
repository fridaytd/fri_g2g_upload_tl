import asyncio

from .logger import logger


async def sleep_for(delay: float) -> None:
    logger.info(f"Sleep for {delay} seconds")
    await asyncio.sleep(delay)
