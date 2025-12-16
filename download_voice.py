from piper import download_voices
from pathlib import Path

DEFAULT_VOICE = "es_ES-davefx-medium"


def main(**kwargs):
    voice = kwargs.get("voice", DEFAULT_VOICE)
    voices_path = Path("src/voices")
    voices_path.mkdir(parents=True, exist_ok=True)
    download_voices.download_voice(voice, download_dir=voices_path)


if __name__ == "__main__":
    main()
