import requests
import json
from loguru import logger
from api.config import rae_api_url_base, rae_api_url_random

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
        response.raise_for_status() # throw exceptions if any

        # If different response code log it and throw exception
        if response.status_code != 200:
            logger.error(f"Error in response with status code: {response.status_code} in RAE API {url}")
            raise Exception(f"Request failed with status code: {response.status_code}")

        logger.info("Response received with success!")
        # Parse the response,
        resultJson = response.json()
        if not resultJson or not resultJson.get("ok"):
            logger.error("Response returned empty string or null value");
            # throw exception here
            
        return resultJson["data"]
    except Exception as e:
        logger.exception("Exception! - API RAE: ", extra={"url": url})
        raise e
        