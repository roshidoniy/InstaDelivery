import asyncio
import logging
import sys
import time

import firebase_admin
import datetime
from keyboard import unfollow_buttons
# --------------------------------
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message, LinkPreviewOptions
from instaloader import (Instaloader, Profile) 
from firebase_admin import credentials, firestore

# Initial Firebase Commands
cred = credentials.Certificate("./instadeliver0SDK.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
col_ref = db.collection('users_info')

# Initial Instaloader Commands

L = Instaloader()
# L.login("white_walter00", "white%0000")
print("logged in")


TOKEN = "6701068330:AAEInwHJitGP-GUcKhKqhueJMtXs8bI7oLE"

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    """
    This handler receives messages with `/start` command

    """

    user = message.from_user

    currentTime = datetime.datetime.now().strftime("%H:%M")

    data = {
        'id': message.from_user.id,
        'fullname': message.from_user.full_name,
        'fetchTime': currentTime,
        'follows': [],
        'last_post_time': None,
    }


    doc_ref = col_ref.document(f"{user.id}")

    if doc_ref.get().exists:
        await message.answer(f"Welcome back {user.first_name} *This is bold*", parse_mode=ParseMode.MARKDOWN_V2)
    else:
        doc_ref.set(data)
        await message.answer(f"Your virtual Instagram Account was successfully created \n So, Enjoy 😉")

    
    # If /start command runs, the follows array will be removed. Fix this

    await message.answer("Hello, Welcome to Insta Deliver!\nRun <blockquote>/fetch + 'username'</blockquote> to fetch last 3 posts from this username", parse_mode=ParseMode.HTML)

    # message.reply(f"Welcome to InstaFetcher. click /fetch to get posts from {USER}")


@dp.message(Command("fetch"))
async def fetch(message: Message, command: CommandObject) -> None:
    username = command.args

    print(message.from_user.full_name)

    if username:
        await message.answer("Fetching posts, please wait...")

    # await message.send(username)

    profile = Profile.from_username(L.context, username)
    posts = profile.get_posts()

    # recognizes if it is a video or photo and it return 3 last posts
    counter = 0
    for post in posts:
        if post.is_video:
            # there is an error, The preview or video is not loading because of changing of url.
            # Sometimes I should just send the url

            fresh_video_url = post.video_url
            await message.answer(f"{post.likes}👍🏻", link_preview_options=LinkPreviewOptions(
                url=fresh_video_url,
                show_above_text=True,
            ))
            print(fresh_video_url)
        else:
            await message.answer(f"{post.likes}👍🏻", link_preview_options=LinkPreviewOptions(
                url=post.url,
                show_above_text=True,
            ))
        counter += 1
        if counter == 3:
            break
        time.sleep(2)  # Small delay to help with rate limiting
    # except instaloader.exceptions.QueryReturnedBadRequestException:
    #     await message.answer(f"Error fetching posts from {username}. Please try again later.")
    #     break --> implement try first *above*


@dp.message(Command("follow"))
async def follow(message: Message, command: CommandObject) -> None:
    # catch the item after /follow command
    followTo = command.args
    userID = message.from_user.id

    doc_ref = col_ref.document(f"{userID}")
    followsArray = list(doc_ref.get().to_dict()['follows'])

    
    
    if len(followsArray) > 3:
        await message.answer(text="You are currently following 3 accounts, which is a limit")
    else:
        # adds new follow to follows property in the document
        doc_ref.update({
        'follows': [followTo] + followsArray
        })

    

@dp.message(Command("unfollow"))
async def unfollow(message: Message) -> None:
    #unfollow feature
    currentlyFollowing = col_ref.document(f"{message.from_user.id}").get().to_dict()['follows']


    await message.answer(text="Choose the account to unfollow", reply_markup=unfollow_buttons(currentlyFollowing))

@dp.message(Command(commands=["getStories", "getstories"]))
async def getStories(message: Message) -> None:
    #unfollow feature
    await message.reply_photo("https://techcrunch.com/wp-content/uploads/2023/03/alexander-shatov-71Qk8ODIBko-unsplash.jpg?w=1390&crop=1", "Soon", )

async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(TOKEN)
    
    # And the run events dispatching
    await dp.start_polling(bot)

    # This is how you can send ads to users 👇🏻
    # await bot.send_message(5076971567, "there is an ad")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())