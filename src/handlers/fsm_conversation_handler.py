# File with FSM States
from aiogram.fsm.state import StatesGroup, State

# Group state for waiting on rae api
class RaeState(StatesGroup):
    searchWord = State()

class DailyMenuFlow(StatesGroup):
    config_choosing = State()
    confirming = State()
    