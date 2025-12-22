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
## Docker

You can also run this project using Docker or Docker Compose.
Build and run with Docker

To build the Docker image manually and run the container:

```shell
docker build -t rehablarte .
docker run --env-file .env -v ./voices:/app/voices -p 8080:8080 --restart unless-stopped rehablarte
```

### Run with Docker Compose

You can use the provided docker-compose.yml file for convenience
Start the service with:
```shell
docker-compose up -d
```
To stop it:
```shell
docker-compose down
```

