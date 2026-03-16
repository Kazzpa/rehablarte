from loguru import logger
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from handlers.fsm_conversation_handler import DailyMenuFlow
from errors.errors import MenukeyboardException
from models.chat_entity import ReChatDiariaConfig, ReChatSession


async def startDiariaBuildMenu(
    message: Message, state: FSMContext, session: ReChatSession
) -> None:
    """ """
    try:
        logger.info("Starting diaria setting menu process")
        keyboard = await buildDiariaKeyboardMenu()

        # Create a temporary config object to replace later
        config = session.chat.diariaConfig
        await state.update_data(config_data=config.model_dump_json())
        # set first state
        await state.set_state(DailyMenuFlow.config_choosing)

        await message.answer(build_menu_text(config), reply_markup=keyboard)
    except Exception as e:
        raise MenukeyboardException(
            "Error building keyboard menu", menu_name="diariaKeyboardMenu"
        ) from e


async def buildDiariaKeyboardMenu() -> InlineKeyboardMarkup:
    """ """
    logger.info("Building diaria word keyboard")
    # The array defines the lineup of the buttons per each row: 2-2-1 in this case
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Activar palabra diaria", callback_data="activate"
                ),
                InlineKeyboardButton(
                    text="Desactivar palabra diaria", callback_data="deactivate"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Hora del mensaje", callback_data="timeconfig"
                ),
                InlineKeyboardButton(
                    text="Repeticion del mensaje", callback_data="repetitionconfig"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Significado de la palabra", callback_data="senses"
                ),
                InlineKeyboardButton(
                    text="Origen de la palabra", callback_data="origin"
                ),
            ],
            [
                InlineKeyboardButton(text="✅​ Finalizar", callback_data="confirm"),
                InlineKeyboardButton(text="❌ Cancelar", callback_data="cancel"),
            ],
        ]
    )
    return keyboard


async def buildDiariaRepeatKeyboardMenu(message: Message) -> None:
    """ """
    try:
        logger.info("Building repeat diaria word keyboard")
        keyboard = buildGenericResponseKeyboard()

        await message.answer(
            "¿Quieres que la palabra diaria se repita a lo largo del día?",
            reply_markup=keyboard,
        )
    except Exception as e:
        raise MenukeyboardException(
            "Error building keyboard menu", menu_name="diariaRepeatKeyboardMenu"
        ) from e


async def buildNumberOfRepeatsKeyboardMenu() -> InlineKeyboardMarkup:
    try:
        logger.info("Building repeat number keyboard")
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="1", callback_data="1"),
                    InlineKeyboardButton(text="2", callback_data="2"),
                    InlineKeyboardButton(text="3", callback_data="3"),
                    InlineKeyboardButton(text="4", callback_data="4"),
                ],
                [InlineKeyboardButton(text="❌ Cancelar", callback_data="cancel")],
            ]
        )
        return keyboard
    except Exception as e:
        raise MenukeyboardException(
            "Error building keyboard menu", menu_name="NumberOfRepetsKeybardMenu"
        ) from e


# Builds the keyboard menu for selecting a time in for the daily word
async def buildClockSelectionKeyboard() -> InlineKeyboardMarkup:
    rows = []
    hours = [f"{h:02d}:00" for h in range(24)]

    hoursPerBtn = 4  # Increment
    for i in range(0, len(hours), hoursPerBtn):
        row = []
        for hour in hours[i : i + hoursPerBtn]:
            col = InlineKeyboardButton(text=hour, callback_data=f"time:{hour}")
            row.append(col)
        rows.append(row)

    # append buttons in last row
    rows.append([InlineKeyboardButton(text="❌ Cancelar", callback_data="cancel")])

    # build keyboard
    keyboard = InlineKeyboardMarkup(inline_keyboard=rows)

    return keyboard


# Generic function to generate a yes/no keyboard
async def buildGenericResponseKeyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Si", callback_data="yes"),
                InlineKeyboardButton(text="No", callback_data="no"),
            ],
            [InlineKeyboardButton(text="❌ Cancelar", callback_data="cancel")],
        ]
    )
    return keyboard


def build_menu_text(config: ReChatDiariaConfig) -> str:
    lines = ["¿Que opcion quieres configurar?\n"]
    lines.append(f"{'✅' if config.isActive else '❌'} Palabra diaria activa")
    lines.append(
        f"🕐 Hora: {config.scheduleTime.strftime('%H:%M') if config.scheduleTime else 'No configurada'}"
    )
    lines.append(
        f"🔁 Repeticion: {config.repetition if config.repetition else 'Sin repeticion'}"
    )
    lines.append(f"{'✅' if config.senses else '❌'} Mostrar significado")
    lines.append(f"{'✅' if config.origin else '❌'} Mostrar origen")
    return "\n".join(lines)
