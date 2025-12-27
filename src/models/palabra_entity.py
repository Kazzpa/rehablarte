from loguru import logger

class Origin:
    def __init__(self, raw: str, type: str, voice: str, text: str):
        """
        Docstring for __init__
        
        :param self: self
        :param raw: Procedencia de la palabra
        :param type: tipo
        :param voice: voice
        :param text: text
        """
        self.raw = raw
        self.type = type
        self.voice = voice
        self.text = text

class Sense:
    def __init__(self , raw: str, category: str, usage: str, description: str, synonyms: str, antonyms: str):
        """
        Docstring for __init__
        
        :param self: Description
        :param raw: Contenido la palabra en la rae
        :param category: Verb, noun, etc
        :param usage: uso
        :param description: Unica descripcion
        :param synonyms: Lista de sinonimos
        :param antonyms: Lista de antonimos
        """
        self.raw = raw
        self.category = category
        self.usage = usage
        self.description = description
        self.synonyms = synonyms
        self.antonyms = antonyms

# Clase modelando el objeto padre
class Palabra:
    def __init__(self, word: str, sensesList: list[Sense], origin: Origin, suggestions: str):
        """
        Docstring for __init__
        
        :param self: self
        :param word: palabra de busqueda
        :type word: str
        :param sensesList: lista con los objectos con las definiciones
        :type sensesList: list[Sense]
        :param origin: Objecto origen con la informacion de origen 
        :type origin: Origin
        :param suggestions: Unkown
        :type suggestions: str
        """
        self.word = word
        self.origin = origin
        self.sensesList = sensesList
        self.suggestions = suggestions

# For the mapper we expect a json with a defined structure as we will parse the values manually
def mapJsonToPalabra(meanings, word, suggestionsStr) -> Palabra:
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
        if (len(meanings) > 1):
            # TODO: Improve this mapping so muiltiple meanigns are supported
            logger.warning("The meanings json had more than 1 result int the array, data missed")
        originObj = meanings[0].get("origin")
        origin = mapJsonToOrigin(originObj)
        suggestions = suggestionsStr
        sensesList = []
        for sense in meanings[0].get("senses"):
            sensesList.append(mapJsonToSense(sense))
        return Palabra(
            word = word,
            origin = origin,
            sensesList = sensesList,
            suggestions = suggestions
        )
    except:
        logger.error("Exception in mapper...")
        raise Exception("Exception in palabra mapper")

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
        if(json == None):
            logger.warning("Skipping origin mapping as it is missing")
            return None
        
        return Origin(
            raw = json.get("raw"), 
            type = json.get("type"), 
            voice = json.get("voice"), 
            text = json.get("text"))
    except:
        logger.error("Exception in mapper...")
        raise Exception("Exception in origin mapper")

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
        if(json == None):
            logger.warning("Skipping sense mapping as it is missing")
            return None
        
        return Sense(
            raw = json.get("raw"), 
            category = json.get("category"), 
            usage = json.get("usage"), 
            description = json.get("description"), 
            synonyms = json.get("synonyms"),
            antonyms = json.get("antonyms"))
    except:
        logger.error("Exception in mapper...")
        raise Exception("Exception in sense mapper")