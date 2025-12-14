import requests
import json
from loguru import logger
from api.config import rae_api_url_base, rae_api_url_random, rae_api_url_words

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
            logger.error(f"Error in response, failed with status code: {response.status_code} in RAE API {url}")
            raise Exception(f"Request failed with status code: {response.status_code}")

        logger.info("Response received with success!")
        # Parse the response,
        resultJson = response.json()
        if not resultJson or not resultJson.get("ok"):
            logger.error("Response returned empty string or null value")
            raise Exception(f"Response received: {resultJson} not valid")
            
        return resultJson["data"]
    except Exception as e:
        logger.exception("Exception! - API RAE: ", extra={"url": url})
        raise e
        

async def get_rae_word(word: str) -> str:
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
                    logger.warning("Error in response from RAE API - word/url not found")
                    # in this case avoid exception and re
                    return "NOT_FOUND"
            logger.error(f"Error in response, failed with status code: {response.status_code} in RAE API {url}")
            raise Exception(f"Request failed with status code: {response.status_code}")

        # process response
        logger.info("Responce received with success!")
        resultJson = response.json()
        if not resultJson or not resultJson.get("ok"):
            logger.error("Response returned empty string or null value")
            raise Exception(f"Response received: {resultJson} not valid")
        
        return resultJson["data"]
    except Exception as e:
        logger.exception("Exception! - API RAE: ", extra={"url": url})
        raise e