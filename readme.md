# REHABLARTE BOT

-----

Project to build a free telegram bot that is able to process text to speech and viceversa.

-----

### Bot Set up

- Create an env file  
need to set up an .env file with this values

``` 
MODEL_PATH=es_ES-davefx-medium.onnx
BOT_TOKEN={your-token-here}
```
### Install libraries

It will install libraries form pyproject.toml
```shell
python install -e .
```
### Download required models
Running this script would download the voice model required for TTS
```shell
python scripts/download_voice.py
```

### Running the bot
```shell
python bot.py
```
## Code formatter and linter
In order to maintain clean code and 
``` 
ruff check
ruff format
```

