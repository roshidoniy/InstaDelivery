---------- Inline buttons callback handle ----------
# @main_router.callback_query(F.data.startswith("d_")) - main.py -> handle the query
# async def goDelete(query: CallbackQuery):
#     unfollowingAccount = query.data[2:]
#     unFollow(query.from_user.id, unfollowingAccount)
#     print(unfollowingAccount)
#     await query.answer(f"You unfollowed @{unfollowingAccount}")

# Inline Delete Buttons Function - keyboards.py
def unfollowInline(follows):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{(response)}", callback_data=f"d_{response}") for response in follows]
    ]
    )

------- Error Handle --------

# @dp.error() # -> error was handled. Using that, I can just send the video url
# async def error_handler(event: ErrorEvent):
#     print("Critical error caused by %s")