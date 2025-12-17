from piper import PiperVoice, SynthesisConfig
from dotenv import load_dotenv
import wave
from pathlib import Path
from decorators import log_duration
from loguru import logger

load_dotenv()

class PiperTTS:
    def __init__(self, model_path=None):
        """Load Piper Spanish voice"""
        logger.info("Loading piperTTS")

        # TODO: Bug here solve later (the model path never exists)
        package_dir = Path(__file__).parent.parent
        model_path = package_dir / "voices" / model_path
        logger.info(f"Model path: {model_path}")

        if not model_path.exists():
            logger.debug("No model_path provided loading default model")
            model_path = "voices/es_ES-davefx-medium.onnx"

        self.voice = PiperVoice.load(model_path)
        self.syn_config = SynthesisConfig(
            volume=1,  # half as loud
            length_scale=1.3,  # twice as slow
            noise_scale=0.6,  # more audio variation
            noise_w_scale=0.6,  # more speaking variation
            normalize_audio=False,  # use raw audio from voice
        )
        logger.info(f"✅ Loaded Piper TTS: {model_path}")

    @log_duration("Synthesize_voice")
    def synthesize_text(self, text) -> str:
        """Generate Spanish speech (WAV bytes)"""
        # Pass wav_buffer as parameter
        wav_path = "/tmp/audio.wav"
        with wave.open(wav_path, "wb") as wav_file:
            self.voice.synthesize_wav(
                text, wav_file=wav_file, syn_config=self.syn_config
            )
        return wav_path

    def get_audio_bytes(self, text):
        """Get WAV bytes for Telegram"""
        wav_path = self.synthesize_text(text)

        # Read the generated WAV file
        with open(wav_path, "rb") as f:
            audio_bytes = f.read()

        return audio_bytes


# Test
if __name__ == "__main__":
    tts = PiperTTS()
    text = "¡Hola! Texto a voz súper ligero con Piper TTS."
    audio_bytes = tts.get_audio_bytes(text)

    with open("../test_spanish.wav", "wb") as f:
        f.write(audio_bytes)
    logger.info("✅ Saved test_spanish.wav")
