# rae api cache keys
from datetime import datetime


class cache_keys_prefix:
    rae_random_key = "RAERANDOM"
    rae_word_key = "RAEWORD:"
    rae_tts_key = "TTS:"


# function to calculate seconds until midnight
def seconds_until_midnight() -> int:
    now = datetime.now()
    midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
    # Move to next midnight
    from datetime import timedelta

    midnight += timedelta(days=1)
    return int((midnight - now).total_seconds())
