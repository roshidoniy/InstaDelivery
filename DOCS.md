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

------- Downlaod Posts --------

@main_router.message()
async def download(message: Message) -> None:
    downloading = await message.answer("Downloading the video")

    L = Instaloader()

    url = message.text

    shortcode = url.split('/')[-2]

    try:
        random_account = randomAccount()
        L.login(random_account['username'], random_account['password'])
        post = Post.from_shortcode(L.context, shortcode)

        # Determine media URL based on post type (image or video)
        if post.is_video:
            media_url = post.video_url
            await message.answer_video(video=media_url, caption=f"{italic(f'@InstaLoader_bot | Instagram upon your terms')}", parse_mode=ParseMode.MARKDOWN_V2)
        else:
            media_url = post.url
            await message.answer_photo(photo=media_url, caption=f"@InstaLoader_bot | Instagram upon your terms")

    except Exception as e:
        # handle the username and delete from instaAccounts
        print(f"Error downloading post: {e}")
        await message.answer("Videoni yuklab bo'lmadi ❌")
    await downloading.delete()