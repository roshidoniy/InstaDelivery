import asyncio
import logging
import sys
import time

from keyboard import unfollow_buttons

#Components
from firebase_helpers import isUserExist, addFollowing, setupAccount, followingList

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message, LinkPreviewOptions
from aiogram.utils.markdown import italic
from instaloader import (Instaloader, Profile) 

# Initial Instaloader Commands

L = Instaloader()
# L.login("white_walter00", "white%0000")
print("logged in")


TOKEN = "6701068330:AAEInwHJitGP-GUcKhKqhueJMtXs8bI7oLE"

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()


@dp.message(CommandStart()) # /start Command
async def command_start_handler(message: types.Message) -> None:
    user = message.from_user

    if isUserExist(user.id):
        await message.answer(f"Welcome back {user.first_name} *This is bold*", parse_mode=ParseMode.MARKDOWN_V2)
    else:
        setupAccount(user.id, user.full_name)
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
            await message.answer(f"{italic(post.caption)}", link_preview_options=LinkPreviewOptions(
                url=fresh_video_url,
                show_above_text=True,
            ), parse_mode=ParseMode.MARKDOWN_V2)
            print(fresh_video_url)
        else:
            await message.answer(f"{italic(post.caption)}", link_preview_options=LinkPreviewOptions(
                url=post.url,
                show_above_text=True,
            ), parse_mode=ParseMode.MARKDOWN)
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

    addStatus = addFollowing(userID, followTo)

    if not addStatus:
        await message.answer("You can follow 3 accounts at most")
    else :
        await message.answer(f"You followed `@{followTo}`", parse_mode=ParseMode.MARKDOWN_V2)

        

@dp.message(Command("unfollow"))
async def unfollow(message: Message) -> None:
    #unfollow feature
    currentlyFollowing = followingList(message.from_user.id)

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