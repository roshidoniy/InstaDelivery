from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton

)

def unfollow_buttons(follows):

    keyboard_buttons = [[KeyboardButton(text=f"{str(response)}")] for response in follows]

    print(keyboard_buttons)

    return ReplyKeyboardMarkup(
    keyboard=keyboard_buttons,
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder="Choose the account to unfollow",
    selective=True,
    )

## Inline Delete Buttons Function
# def unfollowInline(follows):
#     return InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text=f"{(response)}", callback_data=f"d_{response}") for response in follows]
#     ]
#     )