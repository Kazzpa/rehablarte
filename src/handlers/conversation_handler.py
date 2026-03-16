from loguru import logger
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import time
from errors.errors import MenukeyboardException, ReHablarteMappingException, RehablarteApiRaeException
from handlers.fsm_conversation_handler import DailyMenuFlow
from handlers.keyboards_handler import (
    buildClockSelectionKeyboard,
    buildDiariaKeyboardMenu,
    buildNumberOfRepeatsKeyboardMenu,
    build_menu_text
)
from api.api_rae import get_rae_random
from models.chat_entity import ReChatSession
from utils.common import cache_keys_prefix
from models.palabra_entity import PalabraSimple
from models.chat_entity import ReChatDiariaConfig
from utils.common import seconds_until_midnight
from utils.redis_cache import cached_api_call


# Callback function definitions
daily_config_router = Router()

# -------------------------- ACTIVATION CALLBACKS HANDLERS --------------------------

@daily_config_router.callback_query(DailyMenuFlow.config_choosing, F.data == "activate")
async def activate_daily(callback: CallbackQuery, state: FSMContext):
    """
    This activates the daily word, step in the FSM to activate the flow
    Search the random word if not saved already and set state to active
    """
    logger.info("activating daily word")
    await callback.answer("Activar")

    # comprobar si la palabra diaria se ha guardado ya
    cache_key = cache_keys_prefix.rae_random_key

    rae_data = await cached_api_call(
        cache_key=cache_key,
        api_function=get_rae_random,
        ttl=seconds_until_midnight, # Cache for until midnight
        result_type=PalabraSimple
    )

    if not rae_data:
        raise RehablarteApiRaeException("Error calling rae api for word")

    if not isinstance(rae_data, PalabraSimple):
        raise ReHablarteMappingException("Error mapping response type")
    
    # Cambiar el estado guardado a activado
    data = await state.get_data()
    config_draft = ReChatDiariaConfig.model_validate_json(data["config_data"])
    config_draft.isActive = True

    # Save draft back to FSM
    await state.update_data(config_data=config_draft.model_dump_json())
    # return to first menu
    await callback.message.edit_text(
        build_menu_text(config_draft),
        reply_markup = await buildDiariaKeyboardMenu()
    )


@daily_config_router.callback_query(
    DailyMenuFlow.config_choosing, F.data == "deactivate"
)
async def deactivate_daily(callback: CallbackQuery, state: FSMContext):
    """
    Deactivates the daily word, step in the FSM to deactivate the word
    """
    logger.info("deactivating daily word")
    await callback.answer("Desactivando")

    # Cambiar el estado guardado a activado
    data = await state.get_data()
    config_draft = ReChatDiariaConfig.model_validate_json(data["config_data"])
    config_draft.isActive = False

    # Save draft back to FSM
    await state.update_data(config_data=config_draft.model_dump_json())

    # return to first menu
    await callback.message.edit_text(
        build_menu_text(config_draft),
        reply_markup = await buildDiariaKeyboardMenu()
    )

# -------------------------- END OF ACTIVATION CALLBACK HADNLERS --------------------------

# -------------------------- TIME CONFIG HANDLERS --------------------------

@daily_config_router.callback_query(
    DailyMenuFlow.config_choosing, F.data == "timeconfig"
)
async def time_config_selected(callback: CallbackQuery, state: FSMContext):
    logger.info("time configuration selected")
    # TODO: Finish this
    kb = await buildClockSelectionKeyboard()
    # Build clock menu
    # message
    await callback.message.edit_text(
        "¿A que hora quieres que se envie la palabra diaria?",
        reply_markup=kb,
    )

    # change FSM state
    await state.set_state(DailyMenuFlow.confirming)


@daily_config_router.callback_query(
    DailyMenuFlow.confirming, F.data.startswith("time:")
)
async def time_config_confirm(callback: CallbackQuery, state: FSMContext):
    logger.info("Selecting time for daily word")

    # Guardar en persistencia la seleccion
    selected_time = callback.data.split(":")[1]
    if selected_time is None:
        raise MenukeyboardException("Error getting time selected for scheduled daily word")

    logger.info(f"Selected: {selected_time}")

    # Cambiar el estado guardado a activado
    data = await state.get_data()
    config_draft = ReChatDiariaConfig.model_validate_json(data["config_data"])
    config_draft.scheduleTime = time(hour=int(selected_time), minute=0)

    # Save draft back to FSM
    await state.update_data(config_data=config_draft.model_dump_json())
    await state.set_state(DailyMenuFlow.config_choosing)

    # Reload main keyboard
    await callback.message.edit_text(
        build_menu_text(config_draft),
        reply_markup = await buildDiariaKeyboardMenu()
    )

# -------------------------- END OF TIME CONFIG HANDLERS --------------------------

# -------------------------- REPETITION CONFIG HANDLERS --------------------------

@daily_config_router.callback_query(
    DailyMenuFlow.config_choosing, F.data == "repetitionconfig"
)
async def repetition_config_selected(callback: CallbackQuery, state: FSMContext):
    logger.info("repetition configuration selected")

    # Build second keyboard
    kb = await buildNumberOfRepeatsKeyboardMenu()

    # message
    await callback.message.edit_text(
        "¿Cuantas veces al dia quieres que se repita la palabra diaria?",
        reply_markup=kb,
    )

    # set FSM state
    await state.set_state(DailyMenuFlow.confirming)

@daily_config_router.callback_query(DailyMenuFlow.confirming, F.data.regexp("[1-4]"))
async def number_repetition_selected(callback: CallbackQuery, state: FSMContext):
    logger.info("Selecting a number of repetitions")

    # Guardar en persistencia la seleccion
    selected_number = callback.data
    if selected_number is None:
        raise MenukeyboardException("Error getting repetition number in set daily word")

    logger.info(f"Selected: {selected_number}")

    # Cambiar el estado guardado a activado
    data = await state.get_data()
    config_draft = ReChatDiariaConfig.model_validate_json(data["config_data"])
    config_draft.repetition = selected_number

    # Save draft back to FSM
    await state.update_data(config_data=config_draft.model_dump_json())
    await state.set_state(DailyMenuFlow.config_choosing)

    # Reload main keyboard
    await callback.message.edit_text(
        build_menu_text(config_draft),
        reply_markup = await buildDiariaKeyboardMenu()
    )


@daily_config_router.callback_query(DailyMenuFlow.confirming, F.data == "cancel")
async def cancel_repetition_selection(callback: CallbackQuery, state: FSMContext):
    logger.info("Number of repetion selection cancelled")
    await state.set_state(DailyMenuFlow.config_choosing)
    await callback.message.edit_text("❌ Seleccion cancelada",
        reply_markup = await buildDiariaKeyboardMenu()
    )

# -------------------------- END OF REPETITION CALLBACK HANDLERS --------------------------

# -------------------------- USER SELELECTS SENSES/ORIGIN CALLBACK HANDLERS --------------------------

@daily_config_router.callback_query(DailyMenuFlow.config_choosing, F.data == "senses")
async def senses_config_selected(callback: CallbackQuery, state: FSMContext):
    logger.info("Senses configuration selected")

    # message
    await callback.answer("¿Quieres saber el significado de la palabra?")

    # Cambiar estado
    data = await state.get_data()
    config_draft = ReChatDiariaConfig.model_validate_json(data["config_data"])
    config_draft.senses = not config_draft.senses

    # Save draft back to FSM
    await state.update_data(config_data=config_draft.model_dump_json())
    # return to first menu
    await callback.message.edit_text(
        build_menu_text(config_draft),
        reply_markup = await buildDiariaKeyboardMenu()
    )
    

# Function to configure origin
@daily_config_router.callback_query(DailyMenuFlow.config_choosing, F.data == "origin")
async def origin_config_selected(callback: CallbackQuery, state: FSMContext):
    logger.info("origin configuration selected")

    # Build second keyboard
    await callback.answer("¿Quieres saber el origen de la palabra?")

    # cambiar estado
    data = await state.get_data()
    config_draft = ReChatDiariaConfig.model_validate_json(data["config_data"])
    config_draft.origin = not config_draft.origin

    # Save draft back to FSM
    await state.update_data(config_data=config_draft.model_dump_json())
    # return to first menu
    await callback.message.edit_text(
        build_menu_text(config_draft),
        reply_markup = await buildDiariaKeyboardMenu()
    )

# -------------------------- END OF ORIGIN/SENSES CALLBACK HANDLERS --------------------------


# -------------------------- FINAL STATES --------------------------

@daily_config_router.callback_query(DailyMenuFlow.config_choosing, F.data == "cancel")
async def cancel_selected(callback: CallbackQuery, state: FSMContext):
    logger.info("Abort configuration")
    await state.set_state(None)
    await callback.answer("Cancelled")
    await callback.message.edit_text("❌ Configuracion cancelada")
    await state.clear()


@daily_config_router.callback_query(DailyMenuFlow.config_choosing, F.data == "confirm")
async def confirm_selected(callback: CallbackQuery, state: FSMContext, session: ReChatSession):
    logger.info("Confirm configuration")
    # Get draft
    data = await state.get_data()
    config_draft = ReChatDiariaConfig.model_validate_json(data["config_data"])
    # apply changes and persist
    session.chat.diariaConfig = config_draft
    session.is_dirty = True
    # Clear FSM flow data
    await state.set_state(None)
    await callback.answer("Confirmed")
    await callback.message.edit_text("​✅​ Configuracion confirmada")
    await state.clear()



### TODO: UNUSED FUNCTIONS - Should probably remove later --------------------------

# Functions to confirm or cancel an option
@daily_config_router.callback_query(DailyMenuFlow.confirming, F.data == "yes")
async def yes_option_selected(callback: CallbackQuery, state: FSMContext):
    logger.info("confirming yes change")
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