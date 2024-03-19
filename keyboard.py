from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

def unfollow_buttons(follows):

    keyboard_buttons = [KeyboardButton(text=f"@{str(response)} ✨") for response in follows]

    return ReplyKeyboardMarkup(
    keyboard=[
        keyboard_buttons
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Choose the account to unfollow",
    selective=True,
    )