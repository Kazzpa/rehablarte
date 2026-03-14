import requests
from loguru import logger
from api.config import (
    rae_api_url_base,
    rae_api_url_random,
    rae_api_url_words,
    rae_api_url_daily,
)
from models.palabra_entity import mapJsonToPalabra, Palabra
from errors.errors import RehablarteApiRaeException


async def get_rae_random() -> str:
    """
    This function call RAE API random endpoint and returns the data with the word
    """
    try:
        logger.info("Calling API RAE - random word")
        # Define url
        url = rae_api_url_base + rae_api_url_random
        headers = {"Accept": "application/json"}
        # call the api
        response = requests.get(url, headers=headers)

        # If different response code log it and throw exception
        if response.status_code != 200:
            raise RehablarteApiRaeException(f"Error in response, failed with status code: {response.status_code} in RAE API {url}", 
                                            status_code=response.status_code, url_origin=url)

        logger.info("Response received with success!")
        # Parse the response,
        resultJson = response.json()
        if not resultJson or not resultJson.get("ok"):
            raise RehablarteApiRaeException(f"Response received is empty or null: {resultJson}")

        return resultJson.get("data")
    except Exception as e:
        logger.exception("Exception! - API RAE: ", extra={"url": url})
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
        # the url is the get words + {palabra}
        url = rae_api_url_base + rae_api_url_words + word
        headers = {"Accept": "application/json"}
        # call the api
        response = requests.get(url, headers=headers)

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
            raise RehablarteApiRaeException(f"Error in response, failed with status code: {response.status_code} in RAE API {url}", 
                                            status_code=response.status_code, url_origin=url)
        
        # process response
        logger.info("Responce received with success!")
        resultJson = response.json()
        if not resultJson or not resultJson.get("ok"):
            raise RehablarteApiRaeException(f"Response received is empty or null: {resultJson}")
        # Mapping the json
        resultData = resultJson.get("data")
        if resultData is None:
            raise RehablarteApiRaeException("Error reading data from json - cannot map subjson from api rae")
        # Now map the object
        return mapJsonToPalabra(
            resultData.get("meanings"),
            resultData.get("word"),
            resultData.get("suggestions"),
        )
    except Exception as e:
        raise RehablarteApiRaeException("Exception! - API RAE", status_code=response.status_code, url_origin=url) from e


async def get_rae_daily() -> Palabra:
    """
    Docstring for get_rae_daily

    :return: daily word (json) selected by the api
    :rtype: Palabra
    """
    try:
        logger.info("Calling API RAE - Daily")
        # Define url
        url = rae_api_url_base + rae_api_url_daily
        headers = {"Accept": "application/json"}
        # call the api
        response = requests.get(url, headers=headers)

        # If different response code log it and throw exception
        if response.status_code != 200:
            raise RehablarteApiRaeException(f"Error in response, failed with status code: {response.status_code} in RAE API {url}", 
                                            status_code=response.status_code, url_origin=url)

        logger.info("Response received with success!")
        # Parse the response
        resultJson = response.json()
        if not resultJson or not resultJson.get("ok"):
            raise RehablarteApiRaeException(f"Response received is empty or null: {resultJson}")

        return resultJson.get("data")
    except Exception as e:
        raise RehablarteApiRaeException("Exception! - API RAE", status_code=response.status_code, url_origin=url) from e
