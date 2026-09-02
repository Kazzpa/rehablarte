from loguru import logger
from pydantic import BaseModel

from errors.errors import ReHablarteMappingException



class RelatedPalabra(BaseModel):
    """
    Clase que representa palabras relacionadas a otras palabras en la busqueda

    :param word: string con la palabra
    :param label: string con el uso o el coloquio
    """

    word: str
    label: str | None = None

class Origin(BaseModel):
    """
    Docstring for Origin

    :param raw: Procedencia de la palabra
    :param type: tipo
    :param voice: voice
    :param text: text
    """

    raw: str
    type: str | None = None
    voice: str | None = None
    text: str | None = None


class Sense(BaseModel):
    """
    Docstring for Sense

    :param raw: Contenido la palabra en la rae
    :param meaning_number: Numero de orden en los significados
    :param category: Verb, noun, etc
    :param usage: uso
    :param description: Unica descripcion
    :param synonyns: Lista de sinonimos (version antigua, se mantiene por compatibilidad)
    :param antonyns: Lista de antonimos (version antigua, se mantiene por compatibilidad)
    :param synonyns_v2: Lista de sinonimos String con objecto
    :param antonyns_v2: Lista de sinonimos String con objecto
    """

    raw: str
    meaning_number: int
    gender: str | None = None
    category: str = None
    usage: str | None = None
    description: str
    synonyms: list[str] | None = None
    antonyms: list[str] | None = None
    synonyms_v2: list[RelatedPalabra] | None = None
    antonyms_v2: list[RelatedPalabra] | None = None 


class PalabraSimple(BaseModel):
    """
    Docstring for palabraSimple
    this is used when the rae api returns limited response objects

    :param word: palabra buscada
    """

    word: str


# Clase modelando el objeto padre
class Palabra(BaseModel):
    """
    Docstring for palabra

    :param word: palabra de busqueda
    :type word: str
    :param sensesList: lista con los objectos con las definiciones
    :type sensesList: list[Sense]
    :param origin: Objecto origen con la informacion de origen
    :type origin: Origin
    :param suggestions: Unkown
    :type suggestions: str
    """

    word: str
    sensesList: list[Sense] | None
    origin: Origin | None
    suggestions: str | None = None


def map_json_to_palanbraSimple(data) -> PalabraSimple:
    """
    Function to manually map json response from RAE API into an object

    :param word: word
    """
    logger.info("Mapping to palabra simple")
    if data is None:
        logger.error("Error mapping the word to palabra simple, word is None")
        raise ReHablarteMappingException("Error mapping to palabra simple")

    return PalabraSimple(word=data.get("word"))


# For the mapper we expect a json with a defined structure as we will parse the values manually
def mapJsonToPalabra(meanings, word, suggestionsStr=None) -> Palabra:
    """
    Function to manually map json response from RAE API into an object

    :param json: data["meanings"] json in string
    :type json: str
    :param suggestions: suggestions value from data passed directly for easy access
    :type suggestions: str
    :return: palabra object
    :rtype: Palabra
    """
    try:
        logger.info("Mapping to palabra")
        if len(meanings) > 1:
            # TODO: Improve this mapping so muiltiple meanigns are supported
            logger.warning(
                "The meanings json had more than 1 result int the array, data missed"
            )
        originObj = meanings[0].get("origin")
        origin = mapJsonToOrigin(originObj)
        sensesList = []
        for sense in meanings[0].get("senses"):
            sensesList.append(mapJsonToSense(sense))

        ## TODO: FINISH PROPER MAPPING FOR RANDOM AND DAILY
        ## if suggestions is null, do not add it to the object as we need to return senses always
        if suggestionsStr is None:
            logger.info("Mappping simple response")
            return Palabra(
                word=word,
                origin=origin,
                sensesList=sensesList,
            )

        return Palabra(
            word=word,
            origin=origin,
            sensesList=sensesList,
            suggestions=suggestionsStr,
        )
    except KeyError as e:
        logger.error("Error in mapper")
        raise ReHablarteMappingException("Exception in palabra mapper") from e


def mapJsonToOrigin(json) -> Origin | None:
    """
    Function to manually map json data to Object
    can return None if the json provided is null

    :param json: ["meanings"][0]["origin"]
    :type json: str
    :return: object
    :rtype: Origin | None
    """
    try:
        logger.info("Mapping to origin")
        # En este caso la palabra no tiene origin
        if json is None:
            logger.warning("Skipping origin mapping as it is missing")
            return None

        return Origin(
            raw=json.get("raw"),
            type=json.get("type"),
            voice=json.get("voice"),
            text=json.get("text"),
        )
    except KeyError as e:
        logger.error("Error in mapper")
        raise ReHablarteMappingException("Exception in origin mapper") from e


def mapJsonToSense(json) -> Sense | None:
    try:
        """
        Function to manually map json data to Object
        can return None if the json provided is null
        
        :param json: ["meanings"][0]["senses"]
        :type json: str
        :return: Sense Object
        :rtype: Sense | None
        """
        logger.info("Mapping to sense")
        # En este caso la palabra no tiene sense
        if json is None:
            logger.warning("Skipping sense mapping as it is missing")
            return None

        # Get synonyms v2 looping raw object
        raw_synonyms_v2 = json.get("synonyms_v2")
        if raw_synonyms_v2 is None:
            synonyms_v2 = None
        else:
            synonyms_v2 = []
            for word in json.get("synonyms_v2"):
                synonyms_v2.append(mapJsonToRelatedPalabra(word))

        # Get antonyms v2 looping raw object
        raw_antonyms_v2 = json.get("antonyms_v2")
        if raw_antonyms_v2 is None:
            antonyms_v2 = None
        else:
            antonyms_v2 = []
            for word in json.get("antonyms_v2"):
                antonyms_v2.append(mapJsonToRelatedPalabra(word))

        return Sense(
            raw=json.get("raw"),
            meaning_number=json.get("meaning_number"),
            gender=json.get("gender"),
            category=json.get("category"),
            usage=json.get("usage"),
            description=json.get("description"),
            synonyms=json.get("synonyms"),
            antonyms=json.get("antonyms"),
            synonyms_v2=synonyms_v2,
            antonyms_v2=antonyms_v2
        )
    except KeyError as e:
        logger.error("Error in mapper")
        raise ReHablarteMappingException("Exception in sense mapper") from e

def mapJsonToRelatedPalabra(json) -> RelatedPalabra | None:
    try:
        logger.info("Mapping to RelatedPalabra")
        if json is None:
            logger.warning("Skipping RelatedPalabra mapper, raw is None")

        return RelatedPalabra(
            word=json.get("word"),
            label=json.get("label")
        )
    except KeyError as e:
        logger.error("Error in mapper")
        raise ReHablarteMappingException("Exception in related palabra mapper") from e