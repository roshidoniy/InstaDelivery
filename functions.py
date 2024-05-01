from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest
from datetime import datetime, timedelta
from firebase_helpers import followingList
from keyboard import failedURL
from instaloader import Profile
async def groupSend(message, postSidecar):
    count = 1
    for slide in postSidecar:
        if slide.is_video:
            await message.answer_video(slide.video_url, caption=f"{count}")
            print("Video", slide.video_url)
        else:
            await message.answer_photo(slide.display_url, caption=f"{count}")
            print("Photo", slide.display_url)
        count += 1

async def dailyUpdates(message, L) -> None:
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
                await message.answer(f"{username}'dan postlar topilmadi")
                break