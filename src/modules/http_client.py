import httpx
from loguru import logger
from api import config

client: httpx.AsyncClient | None = None


def get_async_client() -> httpx.AsyncClient:
    """
    This function creates and shared an http async client to share across the bot
    """
    logger.info("Creating async http client")
    global client
    if client is None or client.is_closed:
        client = httpx.AsyncClient(
            base_url=config.rae_api_url_base,
            timeout=10.0,
            headers={"Accept": "application/json"},
        )
    return client


async def close_async_client() -> None:
    """
    This function closes the http client before shutdown
    """
    global client
    logger.info("Closing async http client")
    if client is not None and not client.is_closed:
        await client.aclose()
        client = None
