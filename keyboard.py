from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

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

def failedURL(link):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Postni ko'ring 🎬", url=link)]
    ]
    )