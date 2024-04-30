import asyncio
import logging
import sys
import time
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram import Bot, Dispatcher, types, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.markdown import hbold
from aiogram.exceptions import TelegramBadRequest
# Initial Instaloader Commands
from instaloader import Instaloader, Profile, Post

#Components
from firebase_helpers import isUserExist, addFollowing, setupAccount, followingList, unFollow, setting, randomAccount
from keyboard import (unfollow_buttons, failedURL)
from functions import groupSend

L = Instaloader()

TOKEN = "6701068330:AAEInwHJitGP-GUcKhKqhueJMtXs8bI7oLE"

# All handlers should be attached to the Router
main_router = Router()

# State
class BotState(StatesGroup):
    unfollowAcc = State()
    followAcc = State()
    setTime = State()

scheduler = AsyncIOScheduler()

@main_router.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    global scheduler

    
    user = message.from_user

    if isUserExist(user.id):
        await message.answer(f"Welcome back {user.first_name}")
    else:
        setupAccount(user.id, user.full_name)
        await message.answer(f"Your virtual Instagram Account was successfully created \n So, Enjoy 😉")

    user_id = message.from_user.id
    
    if not scheduler.get_job(str(user_id)):
        scheduler.add_job(dailyUpdates, 'interval', minutes=1, args=[message], id=str(user_id))
    
    
    await message.answer("Welcome to InstaDelivery. \n This bot can help you to avoid Instagram Hell. start right now - command /follow ", parse_mode=ParseMode.HTML)

# @main_router.message(Command("setTime"))
# async def setTime(message: Message, state: FSMContext) -> None:
#     await message.answer("Set the time to fetch posts")
#     await state.set_state(BotState.setTime)


# @main_router.message(BotState.setTime)
# async def goSet(message: Message, state: FSMContext) -> None:
    # setting(message.text, message.from_user.id)
    # await state.clear()


@main_router.message(Command("fetch"))
async def fetch(message: Message, command: CommandObject) -> None: 
    username = command.args
    counter = 0
    if username:
        await message.answer("Fetching posts, please wait...")
        profile = Profile.from_username(L.context, username)
        posts = profile.get_posts()
        # get reels
        # Thinking about 
        for post in posts:
            if post.typename == "GraphSidecar":
                await groupSend(message, post.get_sidecar_nodes())
                await message.answer(f"👆🏻👆🏻👆🏻 \n {post.caption}")
            elif post.is_video:
                try:
                    await message.answer_video(video=post.video_url, caption=f"{post.date}")
                except:
                    print(f"This error occured:")
                    await message.answer(f"{post.date}", reply_markup=failedURL(post.video_url))
                
            else:
                try:
                    await message.answer_photo(photo=post.url, caption=f"{post.caption}")
                except:
                    print(f"This error occured:")
                    await message.answer(f"{post.caption}", reply_markup=failedURL(post.url))
            counter += 1
            if counter == 3:
                break
            time.sleep(2) # Small delay to help with rate limiting
    else:
        await message.answer(f"/fetch + username || to fetch posts from this username")

async def dailyUpdates(message) -> None:
    currentlyFollowing = followingList(message.from_user.id)
    currentTime = datetime.now() - timedelta(days=1)
    for username in currentlyFollowing:
        profile = Profile.from_username(L.context, username)
        posts = profile.get_posts()
        for post in posts:
            if post.date_utc > currentTime:
                if post.typename == "GraphSidecar":
                    await groupSend(message, post.get_sidecar_nodes())
                    await message.answer(f"👆🏻👆🏻👆🏻 \n {post.caption}")
                elif post.is_video:
                    try:
                        await message.answer_video(video=post.video_url, caption=f"{post.date}")
                    except:
                        print(f"This error occured:")
                        await message.answer(f"{post.date}", reply_markup=failedURL(post.video_url))
                else:
                    try:
                        await message.answer_photo(photo=post.url, caption=f"{post.caption}")
                    except:
                        print(f"This error occured:")
                        await message.answer(f"{post.caption}", reply_markup=failedURL(post.url))
            else:
                await message.answer(f"No posts found for {username}")
                break

@main_router.message(Command("follow"))
async def follow(message: Message, state: State) -> None:
    followingLength = len(followingList(message.from_user.id))
    if followingLength == 3:
        await message.answer("You can follow 3 accounts at most")
    else:
        await message.answer("Type the account you want to follow ↙️")
        await state.set_state(BotState.followAcc)
    
    
@main_router.message(BotState.followAcc)
async def goFollow(message: Message, state: FSMContext) -> None:
    followTo = message.text
    userID = message.from_user.id
        
    addFollowing(userID, followTo)

    await message.answer(f"You followed `@{followTo}`", parse_mode=ParseMode.MARKDOWN_V2)

    await state.clear()
    

@main_router.message(Command("unfollow"))
async def unfollow(message: Message, state: FSMContext) -> None:
    currentlyFollowing = followingList(message.from_user.id)
    
    if currentlyFollowing:
        await message.answer(text="Choose the account to unfollow 👇", reply_markup=unfollow_buttons(currentlyFollowing))
        await state.set_state(BotState.unfollowAcc)
    else:
        await message.answer(f"Currently, You don't have any followed accounts {hbold("Please follow accounts first using /follow + AccountName")}", parse_mode=ParseMode.HTML)
     

@main_router.message(BotState.unfollowAcc)
async def goDelete(message: Message, state: FSMContext) -> None:
    unFollow(message.from_user.id, message.text)
    message.answer(text="Successfully removed from your followed list", reply_markup=ReplyKeyboardRemove())
    await state.clear()


@main_router.message(Command(commands=["stories", "Stories", "story", "Story"]))
async def getStories(message: Message, command: CommandObject) -> None: 
    # random_account = randomAccount()
    # L.login(random_account['username'], random_account['password'])
    
    stories = []
    myMessage = await message.reply_sticker(sticker="CAACAgIAAxkBAAEL6bhmG_FMa3paannjWWswUZnt-yX_tAACIwADKA9qFCdRJeeMIKQGNAQ")
    loading = await message.answer('Loading...')
    username = command.args
    profile = Profile.from_username(L.context, username)
    isThereAny = profile.has_public_story

    if isThereAny:
        story = L.get_stories(userids=[profile.userid])
        for item in story:
            for i in item.get_items():
                stories.insert(0, i)
            
            for index, item in enumerate(stories):  
                try:
                    if item.is_video:
                        await message.answer_video(video=f"{item.video_url}", caption=f"{index+1}-story")
                    else:
                        await message.answer_photo(photo=f"{item.url}", caption=f"{index+1}-story")
                except TelegramBadRequest:
                    if item.is_video:
                        await message.answer(f"OOPS", reply_markup=failedURL(item.video_url))
                    else:
                        await message.answer(f"OOPS", reply_markup=failedURL(item.url))
    else:
        await message.answer(f"No stories found for {username}")
    await myMessage.delete()
    await loading.delete()

# @main_router.message()
# async def download(message: Message) -> None:
#     await message.answer("Downloading the video")

#     L = Instaloader()

#     url = message.text

#     shortcode = url.split('/')[-2]

#     try:
#         post = Post.from_shortcode(L.context, shortcode)

#         # Determine media URL based on post type (image or video)
#         if post.is_video:
#             media_url = post.video_url
#             await message.answer_video(video=media_url, caption=f"{italic("@InstaLoader_bot | Instagram upon your terms")}", parse_mode=ParseMode.MARKDOWN_V2)
#         else:
#             media_url = post.url
#             await message.answer_photo(photo=media_url, caption=f"@InstaLoader_bot | Instagram upon your terms")

#     except Exception as e:
#         print(f"Error downloading post: {e}")


async def main() -> None:

    
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(TOKEN)
    
    dp = Dispatcher()
    scheduler.start()
    dp.include_router(main_router)
    # And the run events dispatching
    await dp.start_polling(bot)


    while True:
        await asyncio.sleep(1000)

    # This is how you can send ads to users 👇🏻
    # await bot.send_message(5076971567, "there is an ad")



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

