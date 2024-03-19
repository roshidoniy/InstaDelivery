import asyncio
import logging
import sys
from email import message_from_bytes

import firebase_admin
import datetime
from os import getenv  # TOKEN
from keyboard import unfollow_buttons
# --------------------------------
from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message
from aiogram.utils.markdown import hbold, hide_link
from instaloader import Instaloader, Profile
from firebase_admin import credentials, firestore

# Initial Firebase Commands
cred = credentials.Certificate("./instadeliver0SDK.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
col_ref = db.collection('users_info')

# Initial Instaloader Commands

L = Instaloader()
L.login("white_walter00", "white%0000")
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
        'currentTime': currentTime,
        'follows': []
    }


    doc_ref = col_ref.document(f"{user.id}")

    if doc_ref.get().exists:
        await message.answer(f"Welcome back {user.first_name}")
    else:
        doc_ref.set(data)
        await message.answer(f"Your virtual Instagram Account was successfully created \n So, Enjoy 😉")

    
    # If /start command runs, the follows array will be removed. Fix this

    await message.answer(
        f"Hello, Welcome to Insta Deliver!\nRun \"/fetch + {hbold('username')}\" to fetch last 3 posts from this "
        f"username")

    # message.reply(f"Welcome to InstaFetcher. click /fetch to get posts from {USER}")


@dp.message(Command("fetch"))
async def fetch(message: Message, command: CommandObject) -> None:
    username = command.args

    print(message.from_user.full_name)

    await message.answer("Azgina Kutib turas 🤏")

    # await message.send(username)

    profile = Profile.from_username(L.context, username)
    posts = profile.get_posts()

    # recognizes if it is a video or photo and it return 3 last posts
    counter = 0
    for post in posts:
        if post.is_video:
            await message.answer(f"{hide_link(post.video_url)} {post.date_local}")
        else:
            await message.answer(f"{hide_link(post.url)} {post.date_local}")
        counter += 1
        if counter == 3:
            break


@dp.message(Command("follow"))
async def follow(message: Message, command: CommandObject) -> None:
    # catch the item after /follow command
    followTo = command.args
    userID = message.from_user.id

    doc_ref = col_ref.document(f"{userID}")
    followsArray = doc_ref.get().to_dict()['follows']
    
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
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)

    # This is how you can send ads to users 👇🏻
    ## await bot.send_message(5076971567, "there is an ad")
    
    # And the run events dispatching
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())