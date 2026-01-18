from faster_whisper import WhisperModel
from decorators import log_duration
from loguru import logger
import multiprocessing


class SpeechToText:
    @log_duration("STT: Init")
    def __init__(self, model_size="tiny"):
        """Load lightweight Faster-Whisper (Spanish optimized)"""
        logger.info(f"⏳ Loading STT model: {model_size}...")

        total_cores = multiprocessing.cpu_count()
        cpu_threads = max(1, total_cores // 2)

        self.model = WhisperModel(
            model_size,
            device="cpu",
            compute_type="int8",  # ~200MB RAM
            cpu_threads=cpu_threads,
        )
        logger.info("✅ STT Model loaded (~200MB RAM)")

    @log_duration("STT: Transcribe audio")
    async def transcribe(self, audio_path):
        """Convert voice note → Spanish text"""
        segments = self.model.transcribe(
            audio_path,
            beam_size=1,  # Fast + low RAM
            language="es",  # Force Spanish
            vad_filter=True,  # Skip silence
            word_timestamps=False,
        )
        if segments:
            transcribed_text = " ".join([segment.text.strip() for segment in segments[0]]).strip()
        else:
            logger.warning("No se detecto voz")
            transcribed_text = "[No se detectó voz]"
        return transcribed_text if transcribed_text else "[No se detectó voz]"


if __name__ == "__main__":
    global STT
    STT = SpeechToText()
    text = STT.transcribe("/tmp/audio.wav")
    print(text)
