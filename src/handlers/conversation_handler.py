from loguru import logger
from aiogram import Router, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from handlers.fsm_conversation_handler import DailyMenuFlow


# Callback function definitions
daily_config_router = Router()

# TODO: FINISH EACH SELECTED CASE

@daily_config_router.callback_query(DailyMenuFlow.config_choosing, F.data == "activate")
async def activate_daily(callback: CallbackQuery, state: FSMContext):
    logger.info("activating daily word")
    await callback.answer("Activar")
    await callback.message.edit_text("La palabra diaria esta activada")
    
    # comprobar si la palabra diaria se ha guardado ya
    
    # Cambiar el estado

    await state.clear()


@daily_config_router.callback_query(DailyMenuFlow.config_choosing, F.data == "deactivate")
async def deactivate_daily(callback: CallbackQuery, state: FSMContext):
    logger.info("deactivating daily word")
    await callback.answer("Desactivando")
    await callback.message.edit_text("La pabra diaria esta desactivada")
    
    # Cambiar el estado

    await state.clear()

@daily_config_router.callback_query(DailyMenuFlow.config_choosing, F.data == "timeconfig")
async def time_config_selected(callback: CallbackQuery, state: FSMContext):
    logger.info("time configuration selected")


@daily_config_router.callback_query(DailyMenuFlow.config_choosing, F.data == "repetitionconfig")
async def repetition_config_selected(callback: CallbackQuery, state: FSMContext):
    logger.info("repetition configuration selected")
    await callback


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
