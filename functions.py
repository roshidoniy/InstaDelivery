import time
from datetime import datetime, timedelta
from firebase_helpers import followingList
from aiogram.utils.markdown import blockquote
from aiogram.enums import ParseMode
from instaloader import Profile, Instaloader
from instaloader.exceptions import LoginRequiredException, ConnectionException, ProfileNotExistsException


from keyboard import failedURL
from instaloader import Profile
from instagram_helpers import randomLogin
from firebase_helpers import deleteInstaAccount
L = Instaloader(max_connection_attempts=1)
async def groupSend(message, postSidecar):
    count = 1
    for slide in postSidecar:
        if slide.is_video:
            await message.answer_video(slide.video_url, caption=f"{count}")
        else:
            await message.answer_photo(slide.display_url, caption=f"{count}")
        count += 1

async def dailyUpdates(message, L) -> None:
    currentlyFollowing = followingList(message.from_user.id)
    currentTime = datetime.now() - timedelta(days=1)
    for username in currentlyFollowing:
        try:
            profile = Profile.from_username(L.context, username)
            posts = profile.get_posts()
            for post in posts:
                if post.date_utc > currentTime:
                    caption = f"{blockquote(f'{post.owner_username}')} \n {post.caption}"
                    if post.typename == "GraphSidecar":
                        await groupSend(message, post.get_sidecar_nodes())
                        await message.answer(f"👆🏻👆🏻👆🏻 {caption}")
                    elif post.is_video:
                        try:
                            await message.answer_video(video=post.video_url, caption=caption, parse_mode=ParseMode.MARKDOWN_V2)
                        except:
                            print(f"This error occured:")
                            await message.answer(caption, reply_markup=failedURL(post.video_url))
                    else:
                        try:
                            await message.answer_photo(photo=post.url, caption=caption, parse_mode=ParseMode.MARKDOWN_V2)
                        except:
                            print(f"This error occured:")
                            await message.answer(caption, reply_markup=failedURL(post.url))
                else:
                    if post.is_pinned:
                        continue
                    else:
                        break
                time.sleep(3)
            await message.answer(f"`@{username}`dan boshqa yangi postlar yo'q", parse_mode=ParseMode.MARKDOWN_V2)
        except LoginRequiredException:
            print("Login Required Exception occured: Account was logged out")
            await dailyUpdates(message, L)
            randomLogin()
        except ConnectionException:
            print("ConnectionException occured: Checkpoint required")
            await dailyUpdates(message, L)
            randomLogin()
            
