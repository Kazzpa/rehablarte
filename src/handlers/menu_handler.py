from loguru import logger
from aiogram import Router, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from handlers.fsm_conversation_handler import DailyMenuFlow

async def buildKeyboardMenu(message: Message) -> None:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👍 Yes", callback_data="yes"),
                InlineKeyboardButton(text="👎 No", callback_data="no"),
            ]    
        ]
    )
    await message.answer("Do you agree?", reply_markup=keyboard)


menu_test_router = Router()

@menu_test_router.callback_query(F.data == "yes")
async def yes_clicked(callback: CallbackQuery):
    await callback.answer("You clicked YES")
    await callback.message.edit_text("Thanks!")

@menu_test_router.callback_query(F.data == "no")
async def no_clicked(callback: CallbackQuery):
    await callback.answer("You clicked NO")




async def buildDiariaKeyboardMenu(message: Message, state: FSMContext) -> None:
    """
    """
    try:
        logger.info("Building diaria word keyboard")
        # The array defines the lineup of the buttons per each row: 2-2-1 in this case
        keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
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

# Callback function definitions
daily_config_router = Router()

# TODO: FINISH EACH SELECTED CASE

@daily_config_router.callback_query(DailyMenuFlow.config_choosing, F.data == "timeconfig")
async def time_config_selected(callback: CallbackQuery, state: FSMContext):
    logger.info("time configuration selected")


@daily_config_router.callback_query(DailyMenuFlow.config_choosing, F.data == "repetitionconfig")
async def repetition_config_selected(callback: CallbackQuery, state: FSMContext):
    logger.info("repetition configuration selected")


@daily_config_router.callback_query(DailyMenuFlow.config_choosing, F.data == "senses")
async def senses_config_selected(callback: CallbackQuery, state: FSMContext):
    logger.info("Senses configuration selected")


@daily_config_router.callback_query(DailyMenuFlow.config_choosing, F.data == "origin")
async def origin_config_selected(callback: CallbackQuery, state: FSMContext):
    logger.info("origin configuration selected")

@daily_config_router.callback_query(DailyMenuFlow.config_choosing, F.data == "cancel")
async def cancel_selected(callback: CallbackQuery, state: FSMContext):
    logger.info("Abort configuration")
    await callback.answer("Cancelled")

    await callback.message.edit_text("❌ Configuracion cancelada")
    await state.clear()
