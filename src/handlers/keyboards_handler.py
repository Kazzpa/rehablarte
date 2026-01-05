from loguru import logger
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from handlers.fsm_conversation_handler import DailyMenuFlow


async def buildDiariaKeyboardMenu(message: Message, state: FSMContext) -> None:
    """
    """
    try:
        logger.info("Building diaria word keyboard")
        # The array defines the lineup of the buttons per each row: 2-2-1 in this case
        keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
                [
                    InlineKeyboardButton(text="Activar palabra diaria", callback_data="activate"),
                    InlineKeyboardButton(text="Desactivar palabra diaria", callback_data="deactivate")
                ],
                [
                    InlineKeyboardButton(text="Hora del mensaje", callback_data="timeconfig"),
                    InlineKeyboardButton(text="Repeticion del mensaje", callback_data="repetitionconfig")
                ],
                [
                    InlineKeyboardButton(text="Significado de la palabra", callback_data="senses"),
                    InlineKeyboardButton(text="Origen de la palabra", callback_data="origin")
                ],
                [
                    InlineKeyboardButton(text="❌ Cancelar", callback_data="cancel")
                ]
            ]
        )
    
        # set first state
        await state.set_state(DailyMenuFlow.config_choosing)

        await message.answer("Que opcion quieres configurar?", reply_markup=keyboard)
    except Exception as e:
        # TODO: Replace with custom exception for menus
        logger.exception("Exception!")
        raise e
    
async def buildDiariaRepeatKeyboardMenu(message: Message, state: FSMContext) -> None:
    """
    """
    try:
        logger.info("Building repeat diaria word keyboard")
        keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
                [
                    InlineKeyboardButton(text="Si", callback_data="yes_repeat"),
                    InlineKeyboardButton(text="No", callback_data="no_repeat")
                ],
                [
                    InlineKeyboardButton(text="❌ Cancelar", callback_data="cancel")
                ]
            ]
        )
    
        # set first state
        await state.set_state(DailyMenuFlow.config_choosing)

        await message.answer("¿Quieres que la palabra diaria se repita a lo largo del día?", reply_markup=keyboard)
    except Exception as e:
        # TODO: Replace with custom exception for menus
        logger.exception("Exception!")
        raise e