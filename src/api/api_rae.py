import httpx
from loguru import logger
from api.config import (
    rae_api_url_random,
    rae_api_url_words,
    rae_api_url_daily,
)
from models.palabra_entity import PalabraSimple, map_json_to_palanbraSimple, mapJsonToPalabra, Palabra
from errors.errors import RehablarteApiRaeException
from modules.http_client import get_async_client


async def get_rae_random() -> str:
    """
    This function call RAE API random endpoint and returns the data with the word
    """
    try:
        logger.info("Calling API RAE - random word")
        # get the client
        client = get_async_client()
        # call the api
        response = await client.get(url=rae_api_url_random)

        # If different response code log it and throw exception
        if response.status_code != 200:
            raise RehablarteApiRaeException(
                f"Error in response, failed with status code: {response.status_code} in RAE API {rae_api_url_random}",
                status_code=response.status_code,
                url_origin=rae_api_url_random,
            )

        logger.info("Response received with success!")
        # Parse the response,
        resultJson = response.json()
        if not resultJson or not resultJson.get("ok"):
            raise RehablarteApiRaeException(
                f"Response received is empty or null: {resultJson}"
            )

        return resultJson.get("data")
    except Exception as e:
        logger.exception("Exception! - API RAE: ", extra={"url": rae_api_url_random})
        raise e


async def get_rae_word(word: str) -> Palabra:
    """
    Docstring for get_rae_word
    :param word: word to search
    :type word: str
    :return: rae api json data with info about the word
    :rtype: str
    """
    try:
        logger.info("Calling API RAE - Get words")
        # get the client
        client = get_async_client()
        # call the api
        word_url = rae_api_url_words + word
        response = await client.get(url=word_url)

        # process api response
        if response.status_code != 200:
            if response.status_code == 404:
                resultJson = response.json()
                if not resultJson.get("ok") and resultJson.get("error") == "NOT_FOUND":
                    logger.warning(
                        "Error in response from RAE API - word/url not found"
                    )
                    # in this case avoid exception and re
                    return "NOT_FOUND"
            raise RehablarteApiRaeException(
                f"Error in response, failed with status code: {response.status_code} in RAE API {word_url}",
                status_code=response.status_code,
                url_origin=rae_api_url_words,
            )

        # process response
        logger.info("Responce received with success!")
        resultJson = response.json()
        if not resultJson or not resultJson.get("ok"):
            raise RehablarteApiRaeException(
                f"Response received is empty or null: {resultJson}"
            )
        # Mapping the json
        resultData = resultJson.get("data")
        if resultData is None:
            raise RehablarteApiRaeException(
                "Error reading data from json - cannot map subjson from api rae"
            )
        # Now map the object
        return mapJsonToPalabra(
            resultData.get("meanings"),
            resultData.get("word"),
            resultData.get("suggestions")
        )
    except Exception as e:
        raise RehablarteApiRaeException(
            "Exception! - API RAE",
            status_code=response.status_code,
            url_origin=word_url,
        ) from e


async def get_rae_daily() -> PalabraSimple:
    """
    Docstring for get_rae_daily

    :return: daily word (json) selected by the api
    :rtype: Palabra
    """
    try:
        logger.info("Calling API RAE - Daily")
        # get the client
        client = get_async_client()
        # call the api
        response = await client.get(url=rae_api_url_daily)

        # If different response code log it and throw exception
        if response.status_code != 200:
            raise RehablarteApiRaeException(
                f"Error in response, failed with status code: {response.status_code} in RAE API {rae_api_url_daily}",
                status_code=response.status_code,
                url_origin=rae_api_url_daily,
            )

        logger.info("Response received with success!")
        # Parse the response
        resultJson = response.json()
        if not resultJson or not resultJson.get("ok"):
            raise RehablarteApiRaeException(
                f"Response received is empty or null: {resultJson}"
            )

        return map_json_to_palanbraSimple(
            resultJson.get("data")
        )
    except Exception as e:
        raise RehablarteApiRaeException(
            "Exception! - API RAE",
            status_code=response.status_code,
            url_origin=rae_api_url_daily,
        ) from e
