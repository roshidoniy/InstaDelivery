from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest
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