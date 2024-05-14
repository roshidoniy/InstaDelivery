import asyncio
import logging
import sys
import time
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram import Bot, Dispatcher, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.utils.markdown import hbold
from aiogram.exceptions import TelegramBadRequest
# Initial Instaloader Commands

#Components
from firebase_helpers import isUserExist, addFollowing, setupAccount, followingList, unFollow
from keyboard import (unfollow_buttons, failedURL)
from functions import groupSend, dailyUpdates
from instagram_helpers import L, usernameCheck


TOKEN = "6701068330:AAEInwHJitGP-GUcKhKqhueJMtXs8bI7oLE"

# All handlers should be attached to the Router
main_router = Router()

# State
class BotState(StatesGroup):
    unfollowAcc = State()
    followAcc = State()



scheduler = AsyncIOScheduler()

@main_router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    global scheduler

    user = message.from_user

    if isUserExist(user.id):
        pass
    else:
        setupAccount(user.id, user.full_name)
    await message.answer(f"Xush kelibsiz {user.first_name}")
    await helpCommand(message)
    user_id = message.from_user.id
    
    if not scheduler.get_job(str(user_id)):
        scheduler.add_job(dailyUpdates, 'interval', minutes=1, args=[message, L], id=str(user_id))

@main_router.message(Command("help"))
async def helpCommand(message: Message) -> None:
    await message.answer(f"/follow - Shu buyruq orqali instagram akkauntlarga a'zo bo'lishingiz mumkin\n\n/story - Anonym stories ko'rish\n\n")


@main_router.message(Command("now"))
async def now(message: Message) -> None:
    user_id = message.from_user.id

    # If there is a job running, it removes. But Anyway, the new job will be added
    try:
        scheduler.remove_job(str(user_id))
    except:
        pass
    scheduler.add_job(dailyUpdates, 'interval', minutes=1, args=[message, L], id=str(user_id))
    await message.reply(f"🔔 Endi xar kuni shu paytda yangiliklarni yetkazaman")


@main_router.message(Command("fetch"))
async def fetch(message: Message, state: FSMContext) -> None:
    await message.answer("Tez kunda bu funksiyadan foydalana olasiz") 
    # await state.set_state(BotState.fetch)
    # await message.answer(f"username kiriting ↙️")


# @main_router.message(BotState.fetch)
# async def goFetch(message: Message, state: FSMContext) -> None:
#     await state.clear()
#     username = message.text
#     counter = 0
#     await message.answer("Iltimos Kuting, Postlar yuklanyapti...")
#     profile = profileData(username)
#     posts = profile.get_posts() 
#     for post in posts:
#         if post.typename == "GraphSidecar":
#             await groupSend(message, post.get_sidecar_nodes())
#             await message.answer(f"👆🏻👆🏻👆🏻 \n {post.caption}")
#         elif post.is_video:
#             try:
#                 await message.answer_video(video=post.video_url, caption=f"{post.caption}")
#             except:
#                 print(f"This error occured:")
#                 await message.answer(f"{post.caption}", reply_markup=failedURL(post.video_url))
#         else:
#             try:
#                 await message.answer_photo(photo=post.url, caption=f"{post.caption}")
#             except:
#                 print(f"This error occured:")
#                 await message.answer(f"{post.caption}", reply_markup=failedURL(post.url))
#         counter += 1
#         if counter == 3:
#             break
#         time.sleep(2) # Small delay to help with rate limiting



@main_router.message(Command("follow"))
async def follow(message: Message, state: State) -> None:
    followingLength = len(followingList(message.from_user.id))
    if followingLength == 5:
        await message.answer("Hozircha siz 5ta akkountga a'zo bo'la olasiz")
    else:
        await message.answer("Obuna bo'lmoqchi bo'lgan username kiriting ↙️ | \nMisol: sodiq_school") 
        await state.set_state(BotState.followAcc)
    
    
@main_router.message(BotState.followAcc)
async def goFollow(message: Message, state: FSMContext) -> None:
    await state.clear()
    followTo = message.text
    userID = message.from_user.id
    addFollowing(userID, followTo)
    await message.answer(f"Siz obuna bo'ldingiz: `@{followTo}`", parse_mode=ParseMode.MARKDOWN_V2)


@main_router.message(Command("unfollow"))
async def unfollow(message: Message, state: FSMContext) -> None:
    currentlyFollowing = followingList(message.from_user.id)
    
    if currentlyFollowing:
        await message.answer(text="Obunani olmoqchi bo'lgan akkauntni tanlang 👇", reply_markup=unfollow_buttons(currentlyFollowing))
        await state.set_state(BotState.unfollowAcc)
    else:
        await message.answer(f"Hozirda, Sizda obuna bo'lgan akkauntlar yo'q {hbold(f'/follow')} Shu buyruqni berish orqali obuna bo'ling", parse_mode=ParseMode.HTML)
     
@main_router.message(BotState.unfollowAcc)
async def goDelete(message: Message, state: FSMContext) -> None:
    unFollow(message.from_user.id, message.text)
    await message.answer(text="Obunangizdan olib tashlandi", reply_markup=ReplyKeyboardRemove())
    await state.clear()


@main_router.message(Command(commands=["stories", "Stories", "story", "Story"]))
async def getStories(message: Message, state: FSMContext) -> None: 
    await message.answer("Tez kunda bu funksiyadan foydalana olasiz")

    # await message.answer("username kiriting ↙️ | Misol: harrypotter")

    # await state.set_state(BotState.story)

# @main_router.message(BotState.story)
# async def goStory(message: Message, state: FSMContext) -> None:
#     await state.clear()
#     myMessage = await message.reply_sticker(sticker="CAACAgIAAxkBAAEL6bhmG_FMa3paannjWWswUZnt-yX_tAACIwADKA9qFCdRJeeMIKQGNAQ")
#     error_message = "Bu postni telegram'ga yuborib bo'lmadi \n Lekin pastdagi tugmani bosib be'malol ko'rishingiz mumkin"
#     username = message.text
#     stories = []
#     randomLogin()

#     try:
#         profile = profileData(username)
#     except QueryReturnedBadRequestException:
#         await message.answer(f"Kechirasiz Hozirda Story'larni ko'rib bo'lmaydi, keyinchalik urunib kor'ing.")
#     except ProfileNotExistsException as e:
#         print(e)
#         await message.answer(f"❌ Bu akkaunt topilmadi: `@{username}`", parse_mode=ParseMode.MARKDOWN_V2)
#     else:
#         loading = await message.answer('Yuklanyapti...')
#         if profile.has_public_story:
#             await message.answer('Story bor...')
#             story = storiesFrom(profile.userid)

#             for item in story:
#                 for i in item.get_items():
#                     stories.insert(0, i)
            
#                 for index, item in enumerate(stories):  
#                     try:
#                         if item.is_video:
#                             await message.answer_video(video=f"{item.video_url}", caption=f"{index+1}-story")
#                         else:
#                             await message.answer_photo(photo=f"{item.url}", caption=f"{index+1}-story")
#                     except TelegramBadRequest:
#                         if item.is_video:
#                             await message.answer(error_message, reply_markup=failedURL(item.video_url))
#                         else:
#                             await message.answer(error_message, reply_markup=failedURL(item.url))
#         else:
#             await message.answer(f"Hozirda bu akkauntda story'lar yo'q: {username}")
#     finally:
#         await myMessage.delete()
#         try:
#             await loading.delete()
#         except:
#             pass


# @main_router.message()
# # help command

async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(TOKEN)
    dp = Dispatcher()
    scheduler.start()
    dp.include_router(main_router)

    await dp.start_polling(bot)

    while True:
        await asyncio.sleep(1000)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())