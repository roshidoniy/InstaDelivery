import asyncio
import logging
import sys
import time
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler 


#Components
from firebase_helpers import isUserExist, addFollowing, setupAccount, followingList, unFollow, getTime
from keyboard import (unfollow_buttons, failedURL)

from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.utils.markdown import italic, hbold, hide_link
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.types.error_event import ErrorEvent
from instaloader import (Instaloader, Profile) 

# Initial Instaloader Commands

L = Instaloader()
L.login("Iamautisticbear911", "mahmudjon0505")

print("logged in")


TOKEN = "6701068330:AAEInwHJitGP-GUcKhKqhueJMtXs8bI7oLE"

# All handlers should be attached to the Router
main_router = Router()

# State
class BotState(StatesGroup):
    unfollowAcc = State()
    followAcc = State()
        


@main_router.message(CommandStart()) # /start Command
async def command_start_handler(message: types.Message) -> None:
    user = message.from_user

    if isUserExist(user.id):
        await message.answer(f"Welcome back {user.first_name}")
    else:
        setupAccount(user.id, user.full_name)
        await message.answer(f"Your virtual Instagram Account was successfully created \n So, Enjoy 😉")

    
    # If /start command runs, the follows array will be removed. Fix this

    await message.answer("Hello, Welcome to Insta Deliver!\nRun <blockquote>/fetch + 'username'</blockquote> to fetch last 3 posts from this username", parse_mode=ParseMode.HTML)

    # scheduler = AsyncIOScheduler()
    # scheduler.add_job(example, 'interval', seconds=3)
    # scheduler.start()
    # message.reply(f"Welcome to InstaFetcher. click /fetch to get posts from {USER}")


@main_router.message(Command("fetch"))
async def fetch(message: Message, command: CommandObject) -> None:
    username = command.args # /fetch {username}

    if username:
        await message.answer("Fetching posts, please wait...")

    profile = Profile.from_username(L.context, username)
    posts = profile.get_posts()

    # recognizes if it is a video or photo and it return 3 last posts
    counter = 0
    for post in posts:
        if post.is_video:
            # there is an error, The preview or video is not loading because of changing of url.
            # Sometimes I should just send the url

            try:
                await message.answer_video(video=post.video_url, caption=f"{italic(post.caption)}", parse_mode=ParseMode.MARKDOWN_V2)
            except Exception as e:
                await message.answer(f"{italic(post.caption)}", reply_markup=failedURL(post.video_url))
                print(e)
            
        else:
            await message.answer_photo(photo=post.url, caption=f"{italic(post.caption)}", parse_mode=ParseMode.MARKDOWN_V2)
        counter += 1
        if counter == 3:
            break
        time.sleep(2)  # Small delay to help with rate limiting
    # except instaloader.exceptions.QueryReturnedBadRequestException:
    #     await message.answer(f"Error fetching posts from {username}. Please try again later.")
    #     break --> implement try first *above*

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
    

@main_router.message(Command("unfollow")) ## | unfollow feature
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


@main_router.message(Command("check")) # Check
async def check(message: Message) -> None:
    now = datetime.now()
    ifTrue = datetime.fromisoformat(f"{now}") > datetime.fromisoformat(getTime(message.from_user.id))
    print(getTime(message.from_user.id))
    await message.answer(f"{ifTrue}")

@main_router.message(Command(commands=["stories", "Stories", "story", "Story"]))
async def getStories(message: Message, command: CommandObject) -> None: 
    stories = []
    myMessage = await message.answer('🔎')
    loading = await message.answer('Loading...')
    media_group = MediaGroupBuilder()
    username = command.args
    profile = Profile.from_username(L.context, username)
    isThereAny = profile.has_public_story
    
    if isThereAny:
        story = L.get_stories(userids=[profile.userid])
        for item in story:
            for i in item.get_items():
                stories.insert(0, i)
        
            if len(stories) < 10:
                for item in stories: 
                    if item.is_video:
                        media_group.add_video(media=f"{item.video_url}")
                    else:
                        media_group.add_photo(media=f"{item.url}")
                await message.answer_media_group(media_group.build())
            else:
                for item in stories:  
                    if item.is_video:
                        await message.answer_video(video=f"{item.video_url}")
                    else:
                        await message.answer_photo(photo=f"{item.url}")
        
    else:
        await message.answer(f"No stories found for {username}")
    await myMessage.delete()
    await loading.delete()
# async def example() -> None:
#     print("hello")

async def main() -> None:
    
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(TOKEN)
    
    dp = Dispatcher()

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

