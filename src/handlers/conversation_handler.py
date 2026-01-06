from loguru import logger
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from handlers.fsm_conversation_handler import DailyMenuFlow
from handlers.keyboards_handler import buildGenericResponseKeyboard, buildDiariaKeyboardMenu, buildNumberOfRepeatsKeyboardMenu


# Callback function definitions
daily_config_router = Router()

# TODO: FINISH EACH SELECTED CASE

@daily_config_router.callback_query(DailyMenuFlow.config_choosing, F.data == "activate")
async def activate_daily(callback: CallbackQuery, state: FSMContext):
    logger.info("activating daily word")
    await callback.answer("Activar")
    await callback.message.edit_text("La palabra diaria esta activada")
    
    # comprobar si la palabra diaria se ha guardado ya
    
    # Cambiar el estado guardado
    
    await state.clear()


@daily_config_router.callback_query(DailyMenuFlow.config_choosing, F.data == "deactivate")
async def deactivate_daily(callback: CallbackQuery, state: FSMContext):
    logger.info("deactivating daily word")
    await callback.answer("Desactivando")
    await callback.message.edit_text("La pabra diaria esta desactivada")
    
    # Cambiar el estado guardado

    await state.clear()

@daily_config_router.callback_query(DailyMenuFlow.config_choosing, F.data == "timeconfig")
async def time_config_selected(callback: CallbackQuery, state: FSMContext):
    logger.info("time configuration selected")


@daily_config_router.callback_query(DailyMenuFlow.config_choosing, F.data == "repetitionconfig")
async def repetition_config_selected(callback: CallbackQuery, state: FSMContext):
    logger.info("repetition configuration selected")
    
    # Build second keyboard
    kb = await buildNumberOfRepeatsKeyboardMenu()

    # message
    await callback.message.edit_text("¿Cuantas veces al dia quieres que se repita la palabra diaria?", reply_markup=kb)

    # Cambiar estado

    # check if senses is in persistance

    # set FSM state
    await state.set_state(DailyMenuFlow.confirming)


#USER SELELECTS SENSES
@daily_config_router.callback_query(DailyMenuFlow.config_choosing, F.data == "senses")
async def senses_config_selected(callback: CallbackQuery, state: FSMContext):
    logger.info("Senses configuration selected")
    
    # Build second keyboard
    kb = await buildGenericResponseKeyboard() 

    # message
    await callback.message.edit_text("¿Quieres saber el significado de la palabra?", reply_markup=kb)

    # Cambiar estado

    # check if senses is in persistance

    # set FSM state

# Function to configure origin
@daily_config_router.callback_query(DailyMenuFlow.config_choosing, F.data == "origin")
async def origin_config_selected(callback: CallbackQuery, state: FSMContext):
    logger.info("origin configuration selected")

    #Build second keyboard
    kb = await buildGenericResponseKeyboard()
    await callback.message.edit_text("¿Quieres saber el origen de la palabra?", reply_markup=kb)

    # cambiar estado

    # comprobar si origen esta en persistencia

    # set FSM state
    await state.set_state(DailyMenuFlow.config_choosing)

@daily_config_router.callback_query(DailyMenuFlow.confirming, F.data.regexp("[1-4]"))
async def number_repetition_selected(callback: CallbackQuery, state: FSMContext):
    logger.info("Selecting a number of repetitions")

    # Guardar en persistencia la seleccion
    selected_number = callback.data
    logger.info(f"Selected: {selected_number}")

    await state.set_state(DailyMenuFlow.config_choosing)

    await callback.message.edit_text("Volviendo a menu de configuración...")

    # Reload main keyboard
    await buildDiariaKeyboardMenu(callback.message, state) 
    

# Functions to confirm or cancel an option
@daily_config_router.callback_query(DailyMenuFlow.confirming, F.data == "yes")
async def yes_option_selected(callback: CallbackQuery, state: FSMContext):
    logger.info("confirming yes change")

    # guardamos estado en persistencia

    await callback.message.edit_text("Finalizando selección")

    # Volvemos al primer estado
    await state.set_state(DailyMenuFlow.config_choosing)

    # Reload main keyboard
    await buildDiariaKeyboardMenu(callback.message, state)

@daily_config_router.callback_query(DailyMenuFlow.confirming, F.data == "no")
async def no_option_selected(callback: CallbackQuery, state: FSMContext):
    logger.info("confirming no change")
    # No cambiamos nada y volvemos al estado anterior
    await state.set_state(DailyMenuFlow.config_choosing)

    await callback.message.edit_text("Volviendo a menu de configuración...")

    # Reload main keyboard
    await buildDiariaKeyboardMenu(callback.message, state) 

# TODO: Implement functions to save in confirm and dont save delete all in cancel
# FINAL STATES
@daily_config_router.callback_query(DailyMenuFlow.config_choosing, F.data == "cancel")
async def cancel_selected(callback: CallbackQuery, state: FSMContext):
    logger.info("Abort configuration")
    await callback.answer("Cancelled")
    await callback.message.edit_text("❌ Configuracion cancelada")
    await state.clear()

@daily_config_router.callback_query(DailyMenuFlow.config_choosing, F.data == "confirm")
async def confirm_selected(callback: CallbackQuery, state: FSMContext):
    logger.info("Confirm configuration")
    await callback.answer("Confirmed")
    await callback.message.edit_text("​✅​ Configuracion confirmada")
    await state.clear()
